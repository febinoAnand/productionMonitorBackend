import paho.mqtt.client as mqtt
import json
import datetime
from configuration.models import MqttSettings
from data.models import LogData, DeviceData, MachineData,ProductionData
from devices.models import DeviceDetails, MachineDetails,ShiftTimings
from django.db.models.signals import post_save
from django.dispatch import receiver



subscribed_topics = set()


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print('Connected successfully')
        global subscribed_topics
        devices = DeviceDetails.objects.all()
        
        for device in devices:
            sub_topic = device.sub_topic
            if sub_topic and sub_topic not in subscribed_topics:
                mqtt_client.subscribe(sub_topic)
                subscribed_topics.add(sub_topic)
                print(f'Subscribed to {sub_topic}')
        
        print("All topics are successfully subscribed!!")
    else:
        print(f'Bad connection. Code: {rc}')


@receiver(post_save, sender=DeviceDetails)
def handle_device_details_save(sender, instance, **kwargs):
    if instance.sub_topic: 
      subscribe_to_topic(instance.sub_topic)


def subscribe_to_topic(sub_topic):
    if sub_topic not in subscribed_topics:
        mqtt_client.subscribe(sub_topic)
        subscribed_topics.add(sub_topic)
        print(f'Subscribed to {sub_topic}')
    else:
        print(f'Topic {sub_topic} is already subscribed.')
        

def publish_response(mqtt_client, device_token, response, is_error=False):
    try:
        device = DeviceDetails.objects.get(device_token=device_token)
        publish_topic = device.pub_topic
        result = mqtt_client.publish(publish_topic, json.dumps(response))
        print(f"Response Published to {publish_topic}: {response} with result {result}")
    except DeviceDetails.DoesNotExist:
        print(f"Device with token {device_token} not found. Cannot publish response.")




def on_message(mqtt_client, userdata, msg):
    print(f'Received message on topic: {msg.topic} with payload: {msg.payload}')
    currentMessage = msg.payload.decode()
    currentTopic = msg.topic.split("/")
    print(currentTopic)
    print(currentMessage)

    try:
        # Step 2: Check if the message is a valid JSON
        try:
            message_data = json.loads(currentMessage)
        except json.JSONDecodeError as e:
            print("status: ERROR JSON message: Not a valid JSON received")
            print(f'Error decoding JSON: {e}')
            return

        # Extract timestamp and unique ID from the message
        if 'timestamp' in message_data:
            timestamp = message_data['timestamp']
        else:
            timestamp = int(datetime.datetime.now().timestamp())
            message_data['timestamp'] = timestamp
            print('Generated current timestamp')

        unique_id = str(timestamp)


        current_date = datetime.date.today()
        current_time = datetime.datetime.now().time()

        # Step 1: Store raw message in LogData if unique_id is not a duplicate
        if not LogData.objects.filter(unique_id=unique_id).exists():
            log_data = LogData(
                date=current_date,
                time=current_time,
                received_data=currentMessage,
                protocol='MQTT',
                topic_api=msg.topic,
                unique_id=unique_id
            )
            log_data.save()
            print(f'Saved log data to database: {log_data}')
        else:
            log_data = LogData.objects.get(unique_id=unique_id)
            print(f'Log data with unique_id {unique_id} already exists: {log_data}')
            device_token = str(message_data.get('device_token', ''))
            response = {
                "status": "Duplicate Timestamp",
                "message": "Timestamp already exists",
                "Device Token": device_token,
                "timestamp":message_data['timestamp']
            }
            publish_response(mqtt_client, device_token, response, is_error=True)
            return

        # Step 3: Check if it's a command or machine data
        device_token = message_data.get('device_token', '')
        if 'cmd' in message_data and message_data['cmd'] == "TIMESTAMP" and device_token:
            # Handle command
            current_timestamp = int(datetime.datetime.now().timestamp())

            try:
                device = DeviceDetails.objects.get(device_token=device_token)

                device_data = DeviceData(
                    date=current_date,
                    time=current_time,
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
                    "cmd_response": current_timestamp,
                    "device_token": device_token
                }
                publish_response(mqtt_client, device_token, response)

            except DeviceDetails.DoesNotExist:
                response = {
                    "status": "DEVICE NOT FOUND",
                    "message": "Device not found with given token"
                }
                publish_response(mqtt_client, device_token, response, is_error=True)
                print('Device token mismatch')

        elif 'timestamp' in message_data and device_token:
            # Step 4: Handle machine data
            dt = datetime.datetime.fromtimestamp(timestamp)
            message_date = dt.date()
            message_time = dt.time()

            try:
                first_log = LogData.objects.first()
                if first_log:
                    try:
                        first_timestamp = int(first_log.unique_id)
                    except ValueError:
                        first_timestamp = int(datetime.datetime.strptime(first_log.unique_id, "%Y-%m-%d %H:%M:%S").timestamp())

                    if timestamp < first_timestamp:
                        response = {
                            "status": "INVALID TIMESTAMP",
                            "message": "Timestamp is less than first data",
                            "timestamp": timestamp,
                            "device_token": device_token
                        }
                        publish_response(mqtt_client, device_token, response, is_error=True)
                        print('Timestamp is less than the first data in the log')
                        return
            except Exception as e:
                print(f'Error checking first log data: {e}')

            try:
                device = DeviceDetails.objects.get(device_token=device_token)
            except DeviceDetails.DoesNotExist:
                response = {
                    "status": "DEVICE NOT FOUND",
                    "message": "Device not found",
                    "timestamp": timestamp,
                    "device_token": device_token
                }
                publish_response(mqtt_client, device_token, response, is_error=True)
                print('Device token mismatch')
                return

            # Validate machine ID (handle both numbers and characters)
            machine_id = next((key for key in message_data if key not in ['timestamp', 'device_token', 'cmd']), None)
            if not machine_id:
                response = {
                    "status": "MACHINE ID ERROR",
                    "message": "Machine ID not found in message data",
                    "timestamp": timestamp,
                    "device_token": device_token
                }
                publish_response(mqtt_client, device_token, response, is_error=True)
                print('Machine ID not found in message data')
                return

            # Save device data first
            try:
                device_data = DeviceData(
                    date=message_date,
                    time=message_time,
                    data=message_data,
                    device_id=device,
                    protocol='MQTT',
                    topic_api=msg.topic,
                    log_data_id=log_data
                )
                device_data.save()
                print(f'Saved device data to database: {device_data}')
            except Exception as e:
                response = {
                    "status": "DATA SAVE ERROR",
                    "message": f"Error saving device data: {e}",
                    "timestamp": timestamp,
                    "device_token": device_token
                }
                publish_response(mqtt_client, device_token, response, is_error=True)
                print(f'Error saving device data to database: {e}')
                return

            try:
                machine = MachineDetails.objects.get(machine_id=machine_id)
            except MachineDetails.DoesNotExist:
                response = {
                    "status": "MACHINE NOT FOUND",
                    "message": "Machine not found with given ID",
                    "timestamp": timestamp,
                    "device_token": device_token
                }
                publish_response(mqtt_client, device_token, response, is_error=True)
                print('Machine ID mismatch')
                return

            # Step 5: Save machine data
            try:
                machine_data = MachineData(
                    date=message_date,
                    time=message_time,
                    machine_id=machine,
                    data=message_data,
                    device_id=device,
                    data_id=log_data
                )
                machine_data.save()
                print(f'Saved machine data to database: {machine_data}')

                #Step 6: Extract production count
                production_count = message_data.get(machine_id, 0)
                print(f"Extracted production count: {production_count} for machine_id: {machine_id}")
                last_production_data = ProductionData.objects.filter(machine_id=machine.machine_id).order_by('-date', '-time').first()
                print("Queried last_production_data:", last_production_data)

                if last_production_data:
                    print(f"Last production count: {last_production_data.production_count}")
                    if last_production_data.production_count > production_count:
                        response = {
                            "status": "PRODUCTION COUNT ERROR",
                            "message": "Production count is less than last recorded count",
                            "timestamp": timestamp,
                            "device_token": device_token,
                            "production_count": production_count
                        }
                        publish_response(mqtt_client, device_token, response, is_error=True)
                        print('Production count is less than the last recorded count')
                        return
                else:
                    print("No previous production data found for the given machine_id")
                
                #Step 7: Save production data
                # Fetch the ShiftTimings instance
                dt = datetime.datetime.fromtimestamp(message_data['timestamp'])
                message_date = dt.date()
                message_time = dt.time()
                shift_instance = get_shift_instance(message_time)
    
                if not shift_instance:
                    print('No matching shift found for the given time')
                    response = {
                        "status": "SHIFT ERROR",
                        "message": "No matching shift found for the given time",
                        "timestamp": message_data['timestamp'],
                        "device_token": message_data.get('device_token', '')
                    }
                    publish_response(mqtt_client, message_data.get('device_token', ''), response, is_error=True)
                    return
              

                # Save production data
                production_data = ProductionData(
                    date=message_date,
                    time=message_time,
                    shift_id=shift_instance._id,
                    shift_name=shift_instance.shift_name,
                    shift_start_time=shift_instance.start_time,
                    shift_end_time=shift_instance.end_time,
                    target_production=machine.production_per_hour,  
                    machine_id=machine.machine_id,
                    machine_name=machine.machine_name,
                    production_count=production_count,
                    data_id=log_data.id
                )
                production_data.save()
                print(f'Saved production data to database: {production_data}')


                response = {
                    "status": "OK",
                    "message": "Successfully data saved",
                    "timestamp": timestamp,
                    "device_token": device_token
                }
                publish_response(mqtt_client, device_token, response)

            except Exception as e:
                response = {
                    "status": "DATA SAVE ERROR",
                    "message": f"Error production data: {e}",
                    "timestamp": timestamp,
                    "device_token": device_token
                }
                publish_response(mqtt_client, device_token, response, is_error=True)
                print(f'Error saving machine or production data to database: {e}')

        else:
            print("Unsupported message format")
            response = {
                "status": "DATA ERROR",
                "message": "Unsupported message format",
            }
            publish_response(mqtt_client, device_token, response)

    except ValueError as e:
        response = {
            "status": "VALUE ERROR",
            "message": str(e),
            "timestamp": timestamp,
            "device_token": device_token
        }
        publish_response(mqtt_client, device_token, response, is_error=True)
        print(f'Error processing message: {e}')


def get_shift_instance(message_time):
    print("msg time",message_time)
    try:
        shift_instance = ShiftTimings.objects.filter(
            start_time__lte=message_time,
            end_time__gte=message_time
        ).first()
        return shift_instance
    except Exception as e:
        print(f'Error fetching ShiftTimings instance: {e}')
        return None



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