import paho.mqtt.client as mqtt
import json
import datetime
from configuration.models import MqttSettings
from data.models import LogData, DeviceData, MachineData,ProductionData
from devices.models import DeviceDetails, MachineDetails,ShiftTiming
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings


subscribed_topics = set()


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print('Connected successfully')
        global subscribed_topics

        # Fetch the last MqttSettings instance
        mqtt_settings = MqttSettings.objects.last()
        if not mqtt_settings:
            print('MqttSettings instance does not exist.')
            return

        sub_topic = mqtt_settings.sub_topic
        if sub_topic and sub_topic not in subscribed_topics:
            client.subscribe(sub_topic)
            subscribed_topics.add(sub_topic)
            print(f'Subscribed to {sub_topic}')

        print("All topics are successfully subscribed!!")
    else:
        print(f'Bad connection. Code: {rc}')



@receiver(post_save, sender=DeviceDetails)
def handle_device_details_save(sender, instance, **kwargs):
    if instance.sub_topic: 
      subscribe_to_topic(instance.sub_topic)


@receiver(post_save, sender=MqttSettings)
def subscribe_to_topic(sender, instance, **kwargs):
    global mqtt_client

    if instance.sub_topic:
        mqtt_client.subscribe(instance.sub_topic)
        print(f'Subscribed to {instance.sub_topic}')

def subscribe_to_topic(sub_topic):
    if sub_topic not in subscribed_topics:
        mqtt_client.subscribe(sub_topic)
        subscribed_topics.add(sub_topic)
        print(f'Subscribed to {sub_topic}')
    else:
        print(f'Topic {sub_topic} is already subscribed.')
        

def publish_response(mqtt_client, device_token, response, is_error=False):
    try:
        # Fetch the first MqttSettings instance
        mqtt_settings = MqttSettings.objects.first()
        if not mqtt_settings:
            print("MqttSettings instance does not exist. Cannot publish response.")
            return

        publish_topic = mqtt_settings.pub_topic

        # Publish the response to the topic
        result = mqtt_client.publish(publish_topic, json.dumps(response))
        print(f"Response Published to {publish_topic}: {response} with result {result}")

    except Exception as e:
        print(f"An error occurred: {e}")


def log_message(currentMessage, topic, protocol='MQTT'):
    # Extract current date and time
    current_date = datetime.date.today()
    current_time = datetime.datetime.now().time()

    # Attempt to parse JSON and extract timestamp if available
    try:
        message_data = json.loads(currentMessage)
        data_id = str(message_data['timestamp']) if 'timestamp' in message_data else None
    except json.JSONDecodeError:
        message_data = None
        data_id = None

    # Save log data to database
    log_data = LogData(
        date=current_date,
        time=current_time,
        received_data=currentMessage,
        protocol=protocol,
        topic_api=topic,
        data_id=data_id
    )
    log_data.save()
    print('Saved log data to database')

    return message_data, log_data


def on_message(mqtt_client, userdata, msg):
    print(f'Received message on topic: {msg.topic} with payload: {msg.payload}')
    currentMessage = msg.payload.decode()

    # Log the message and get the parsed data and log entry
    message_data, log_data = log_message(currentMessage, msg.topic)

    # If the message is not a valid JSON, return after logging it
    if message_data is None:
        response = {
            "status": "Invalid JSON",
            "message": "The received message is not a valid JSON",
            "timestamp": int(datetime.datetime.now().timestamp())
        }
        publish_response(mqtt_client,'', response, is_error=True)
        return
    

    # Extract device token and timestamp from the message
    device_token = message_data.get('device_token', '')
    timestamp = message_data.get('timestamp', int(datetime.datetime.now().timestamp()))
    
    if 'cmd' in message_data and message_data['cmd'] == "TIMESTAMP" and device_token:
        handle_command_message(mqtt_client, msg, message_data, log_data)
    elif 'timestamp' in message_data and device_token and 'shift_no' in message_data:
        machine_data_saved = handle_machine_data(mqtt_client, msg, message_data, log_data)
        if machine_data_saved:
            handle_production_data(mqtt_client, message_data, log_data)
    else:
        response = {
            "status": "UNKNOWN FORMAT",
            "message": "Received message format is not recognized",
            "timestamp": timestamp
        }
        publish_response(mqtt_client, device_token, response, is_error=True)


def handle_command_message(mqtt_client, msg, message_data, log_data):
    current_timestamp = int(datetime.datetime.now().timestamp())
    device_token = message_data['device_token']

    try:
        device = DeviceDetails.objects.get(device_token=device_token)
        device_data = DeviceData(
            date=datetime.date.today(),
            time=datetime.datetime.now().time(),
            data=message_data,
            device_id=device,
            protocol='MQTT',
            topic_api=msg.topic,
            log_data_id=log_data
        )
        device_data.save()
        print(f'Saved device data to database: {device_data}')

        response = {
            "status": "OK",
            "device_token": device_token,
            "cmd_response": current_timestamp,
        }
        publish_response(mqtt_client, device_token, response)
    except DeviceDetails.DoesNotExist:
        response = {
            "status": "DEVICE NOT FOUND",
            "message": "Device not found with given token"
        }
        publish_response(mqtt_client, device_token, response, is_error=True)
        print('Device token mismatch')


def handle_machine_data(mqtt_client, msg, message_data, log_data):
    timestamp = message_data['timestamp']
    dt = datetime.datetime.utcfromtimestamp(timestamp)
    message_date = dt.date()
    message_time = dt.time()

    device_token = message_data.get('device_token', '')
    errors = []
    
    try:
        device = DeviceDetails.objects.get(device_token=device_token)
    except DeviceDetails.DoesNotExist:
        errors.append({
            "status": "DEVICE NOT FOUND",
            "message": "Device not found with given token",
            "device_token": device_token,
            "timestamp": timestamp
        })
        print('Device token mismatch')
        publish_response(mqtt_client, device_token, errors, is_error=True)
        # Return False as the device was not found
        return False



    if DeviceData.objects.filter(timestamp=str(timestamp),device_id=device): 


        errors.append({
            "status": "DUPLICATE TIMESTAMP",
            "message": "Duplicate timestamp found, data not saved.",
            "device_token": device_token,
            "timestamp": timestamp
        })
        print('Duplicate timestamp found, data not saved.')
        publish_response(mqtt_client, device_token, errors, is_error=True)
        return False

    for key, value in message_data.items():
        if key in ['timestamp', 'device_token', 'cmd', 'shift_no']:
            continue  # Skip non-machine ID keys

        machine_id = key
        machine_data_content = value

        try:
            machine = MachineDetails.objects.get(machine_id=machine_id)
        except MachineDetails.DoesNotExist:
            print(f'Machine ID mismatch for {machine_id}')
            continue  # Skip this machine_id and move to the next one

        try:
            machine_data = MachineData(
                date=message_date,
                time=message_time,
                machine_id=machine,
                data={machine_id: machine_data_content},
                device_id=device,
                log_data_id=log_data,
                timestamp=str(timestamp)
            )
            machine_data.save()
            print(f'Saved machine data to database: {machine_data}')

        except Exception as e:
            errors.append({
                "status": "DATA SAVE ERROR",
                "message": f"Error saving machine data: {e}",
                "device_token": device_token,
                "timestamp": timestamp,
            })
            print(f'Error saving machine data to database: {e}')
            continue  # Continue with the next machine data

    device_data = DeviceData(
        date=message_date,
        time=message_time,
        data=message_data,
        device_id=device,
        protocol='MQTT',
        topic_api=msg.topic,
        timestamp=str(timestamp),
        log_data_id=log_data
    )
    device_data.save()
    print(f'Saved device data to database: {device_data}')
    
    if errors:
        for error in errors:
            publish_response(mqtt_client, device_token, error, is_error=True)
        return False

    response = {
        "status": "OK",
        "message": "Successfully saved data",
        "device_token": device_token,
        "timestamp": timestamp
    }
    publish_response(mqtt_client, device_token, response)

    return True

def handle_production_data(mqtt_client, message_data, log_data):
    end_shift_time_str = settings.END_SHIFT_TIME
    end_shift_number = settings.END_SHIFT_NUMBER

    if isinstance(end_shift_time_str, str):
        end_shift_time = datetime.datetime.strptime(end_shift_time_str, "%H:%M:%S").time()
    else:
        # If end_shift_time_str is already a time object, use it directly
        end_shift_time = end_shift_time_str

    timestamp = message_data['timestamp']
    dt = datetime.datetime.utcfromtimestamp(timestamp)
    message_date = dt.date()
    message_time = dt.time()
    device_token = message_data['device_token']
    shift_number = message_data['shift_no']
    errors = []

    for machine_id, production_count in message_data.items():
        if machine_id in ['timestamp', 'device_token', 'shift_no']:
            continue

        machine = MachineDetails.objects.filter(machine_id=machine_id).first()
        if not machine:
            errors.append(f"No machine found for machine_id: {machine_id}")
            continue

        last_production_data = ProductionData.objects.filter(machine_id=machine.machine_id).order_by('-date', '-time').first()

        if last_production_data and last_production_data.production_count > production_count:
            errors.append({
                "status": "PRODUCTION COUNT ERROR",
                "message": "Production count is less than last recorded count for " + machine_id,
                "device_token": device_token,
                "production_count": production_count,
                "timestamp": timestamp
            })
            print('Production count is less than the last recorded count')
            continue

        shift_instance = ShiftTiming.objects.filter(shift_number=shift_number).first()
        if not shift_instance:
            shift_instance = ShiftTiming(
                shift_number=shift_number,
                start_time=None,
                end_time=None,
                shift_name=None
            )
            shift_instance.save()

        production_date = message_date - datetime.timedelta(days=1) if dt.time() < end_shift_time and shift_number == end_shift_number else message_date

        try:
            production_data = ProductionData(
                date=message_date,
                time=message_time,
                shift_number=shift_instance.shift_number,
                shift_name=shift_instance.shift_name,
                target_production=machine.production_per_hour,
                machine_id=machine.machine_id,
                machine_name=machine.machine_name,
                production_count=production_count,
                production_date=production_date,
                log_data_id=log_data.id,
                timestamp=timestamp
            )
            production_data.save()
            print(f'Saved production data to database: {production_data}')

        except Exception as e:
            errors.append({
                "status": "DATA SAVE ERROR",
                "message": f"Error saving production data: {e}",
                "device_token": device_token,
                "timestamp": timestamp,
            })
            print(f'Error saving production data to database: {e}')
            continue

    if errors:
        for error in errors:
            response = {
                "status": "ERROR",
                "message": error
            }
            publish_response(mqtt_client, device_token, response, is_error=True)
        return False

    response = {
        "status": "OK",
        "message": "Successfully saved data",
        "device_token": device_token,
        "timestamp": timestamp
    }
    publish_response(mqtt_client, device_token, response)

    return True

    







mqtt_client = mqtt.Client()

def get_mqtt_settings():
    try:
        mqtt_settings = MqttSettings.objects.first()
        return mqtt_settings.__dict__

    except MqttSettings.DoesNotExist:
        print("Error getting mqtt")
        default_settings = {}
        default_settings["username"] = ""
        default_settings["password"] = ""
        default_settings["host"] = "mqtt.univa.cloud"
        default_settings["port"] = 1883
        default_settings["keepalive"] = 60
        
        return default_settings
        # raise ValueError("MQTT settings not found in the database.")
    
    except Exception as e:
        print ("Error in getting MQTT settings:",e)

def start_mqtt_client():

    mqtt_settings = get_mqtt_settings()
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
    
    try:
        mqtt_client.username_pw_set(mqtt_settings["username"], mqtt_settings["password"])
        mqtt_client.connect(
            host=mqtt_settings["host"],
            port=mqtt_settings["port"],
            keepalive=mqtt_settings["keepalive"]
        )
        mqtt_client.loop_start()
    except Exception as e:
        print ("MQTT not connected..",e)