
import os
import django
import paho.mqtt.client as mqtt
import json
import datetime
import time
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'univaProductionMonitor.settings')
django.setup()


from configuration.models import MqttSettings
from data.models import LogData, DeviceData, MachineData,ProductionData
from devices.models import DeviceDetails, MachineDetails,ShiftTiming
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from configuration.models import Setting
from univaProductionMonitor.celery import processAndSaveMqttData
# from channels.layers import get_channel_layer
# from asgiref.sync import async_to_sync


subscribed_topics = set()


def on_connect(client, userdata, flags, rc):
    setting = Setting.objects.first()
    enable_printing = setting.enable_printing if setting else False

    if rc == 0:
        if enable_printing:
          print('Connected successfully')
        global subscribed_topics

        # Fetch the last MqttSettings instance
        mqtt_settings = MqttSettings.objects.last()
        if not mqtt_settings:
            if enable_printing:
              print('MqttSettings instance does not exist.')
            return

        sub_topic = mqtt_settings.sub_topic
        if sub_topic and sub_topic not in subscribed_topics:
            client.subscribe(sub_topic)
            subscribed_topics.add(sub_topic)
            if enable_printing:
              print(f'Subscribed to {sub_topic}')
        if enable_printing:
          print("All topics are successfully subscribed!!")
    else:
        if enable_printing:
          print(f'Bad connection. Code: {rc}')



@receiver(post_save, sender=DeviceDetails)
def handle_device_details_save(sender, instance, **kwargs):

    if instance.sub_topic: 
      subscribe_to_topic(instance.sub_topic)


@receiver(post_save, sender=MqttSettings)
def subscribe_to_topic(sender, instance, **kwargs):
    setting = Setting.objects.first()
    enable_printing = setting.enable_printing if setting else False
    global mqtt_client

    if instance.sub_topic:
        mqtt_client.subscribe(instance.sub_topic)
        if enable_printing:
          print(f'Subscribed to {instance.sub_topic}')

def subscribe_to_topic(sub_topic):
    setting = Setting.objects.first()
    enable_printing = setting.enable_printing if setting else False

    if sub_topic not in subscribed_topics:
        mqtt_client.subscribe(sub_topic)
        subscribed_topics.add(sub_topic)
        if enable_printing:
          print(f'Subscribed to {sub_topic}')
    else:
        if enable_printing: 
           print(f'Topic {sub_topic} is already subscribed.')
        

def publish_response(mqtt_client, device_token, response, is_error=False):
    setting = Setting.objects.first()
    enable_printing = setting.enable_printing if setting else False
    try:
        # Fetch the first MqttSettings instance
        mqtt_settings = MqttSettings.objects.first()
        if not mqtt_settings:
            if enable_printing:
              print("MqttSettings instance does not exist. Cannot publish response.")
            return

        publish_topic = mqtt_settings.pub_topic

        # Publish the response to the topic
        result = mqtt_client.publish(publish_topic+'/'+device_token, json.dumps(response))
        # if enable_printing:
        print()
        print(f"Response Published to {publish_topic}: {response}")
        # print(f"Response Published to {publish_topic}: {response} with result {result}")

    except Exception as e:
        if enable_printing:
          print(f"An error occurred: {e}")


def log_message(currentMessage, topic, protocol='MQTT'):
    setting = Setting.objects.first()
    enable_printing = setting.enable_printing if setting else False
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
    if enable_printing:
       print('Saved log data to database')

    return message_data, log_data


def on_message(mqtt_client, userdata, msg):
    try:
        print()
        print()
        print(f'Received message on topic: {msg.topic} with payload: {msg.payload}')
        currentMessage = msg.payload.decode()

        # Log the message and get the parsed data and log entry
        message_data, log_data = log_message(currentMessage, msg.topic)

        # processAndSaveMqttData.delay(msg.payload)

        # If the message is not a valid JSON, return after logging it
        if message_data is None:
            response = {
                "status": "INVALID JSON",
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
                # args = {"mqtt_client":mqtt_client,"message_data":message_data,"log_data":log_data}
                message_data['log_id'] = log_data.id
                processAndSaveMqttData.delay(message_data)
                # print (args)
                # handle_production_data(mqtt_client, message_data, log_data)
        else:
            response = {
                "status": "UNKNOWN FORMAT",
                "message": "Received message format is not recognized",
                "timestamp": timestamp
            }
            publish_response(mqtt_client, device_token, response, is_error=True)
    except Exception as e:
        print (e)


def handle_command_message(mqtt_client, msg, message_data, log_data):
    setting = Setting.objects.first()
    enable_printing = setting.enable_printing if setting else False


    current_timestamp = int(datetime.datetime.now().timestamp())
    device_token = message_data['device_token']

    try:
        device = DeviceDetails.objects.get(device_token=device_token)
        if enable_printing:
           print("device",device)
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
        if enable_printing:
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
        if enable_printing:
          print('Device token mismatch')


def handle_machine_data(mqtt_client, msg, message_data, log_data):
    setting = Setting.objects.first()
    enable_printing = setting.enable_printing if setting else False

    timestamp = message_data['timestamp']
    

    # "PHR":18.0000,"PMIN":32.0000,"PSEC":16.0000
    
    # dt = datetime.datetime.utcfromtimestamp(timestamp)
    dt = datetime.datetime.fromtimestamp(timestamp)
    message_date = dt.date()
    message_time = dt.time()

    if 'PHR' in message_data and 'PMIN' in message_data and 'PSEC' in message_data:
        plcHR = int(message_data['PHR'])
        plcMIN = int(message_data['PMIN'])
        plcSEC = int(message_data['PSEC'])
        # print (plcHR,plcMIN,plcSEC)
        message_time = datetime.time(plcHR,plcMIN,plcSEC)
    
    # print("time",message_time)
    device_token = message_data.get('device_token', '')
    errors = []
    
    try:
        device = DeviceDetails.objects.get(device_token=device_token)
        if enable_printing:
           print("device",device)
    except DeviceDetails.DoesNotExist:
        errors.append({
            "status": "DEVICE NOT FOUND",
            "message": "Device not found with given token",
            "device_token": device_token,
            "timestamp": timestamp
        })
        if enable_printing:
           print('Device token mismatch')
        publish_response(mqtt_client, device_token, errors, is_error=True)
        # Return False as the device was not found
        return False
    
        # Retrieve the first data entry for the device based on the timestamp
    deviceFirstData = DeviceData.objects.filter(device_id__device_token=device_token).order_by('data__timestamp').first()

    # Check if deviceFirstData exists and contains the timestamp
    if deviceFirstData and "timestamp" in deviceFirstData.data:
        oldTimestamp = deviceFirstData.data["timestamp"]

        # Compare the old timestamp with the incoming timestamp
        if oldTimestamp > timestamp:
            errors.append({
                "status": "INVALID TIMESTAMP",
                "message": "Received timestamp is less than first data timestamp",
                "device_token": device_token,
                "timestamp": timestamp
            })
            if enable_printing:
               print('Received timestamp is less than current timestamp: firstTimestamp =', oldTimestamp, '- Received =', timestamp)
            publish_response(mqtt_client, device_token, errors, is_error=True)
            return False
    else:
        # Handle case where no prior data exists or the timestamp key is missing
        # errors.append({
        #     "status": "MISSING DATA",
        #     "message": "No previous timestamp found for the device or timestamp is missing",
        #     "device_token": device_token
        # })
        # print('No previous timestamp found for device_token:', device_token)
        # publish_response(mqtt_client, device_token, errors, is_error=True)
        # return False
        if enable_printing:
           print('No previous data found. Saving this as the first data entry for device_token:', device_token)
    
    currentTimestamp = time.time()
    if currentTimestamp < timestamp:
        errors.append({
            "status": "INVALID TIMESTAMP",
            "message": "Received timestamp is greater than current timestamp",
            "device_token": device_token,
            "timestamp": timestamp
        })
        if enable_printing:
           print('Received timestamp is greater than current timestamp current =',currentTimestamp,' - Received',timestamp)
        publish_response(mqtt_client, device_token, errors, is_error=True)
        return False

    if DeviceData.objects.filter(timestamp=str(timestamp),device_id__device_token=device_token).exists(): 
        errors.append({
            "status": "DUPLICATE TIMESTAMP",
            "message": "Duplicate timestamp found, data not saved.",
            "device_token": device_token,
            "timestamp": timestamp
        })
        if enable_printing:
           print('Duplicate timestamp found, data not saved.')
        publish_response(mqtt_client, device_token, errors, is_error=True)
        return False

    # for key, value in message_data.items():
    #     if key in ['timestamp', 'device_token', 'cmd', 'shift_no']:
    #         continue  # Skip non-machine ID keys

    #     machine_id = key
    #     machine_data_content = value

    #     try:
    #         machine = MachineDetails.objects.get(machine_id=machine_id)
    #     except MachineDetails.DoesNotExist:
    #         if enable_printing:
    #           print(f'Machine ID mismatch for {machine_id}')
    #         continue  # Skip this machine_id and move to the next one

    #     try:
    #         machine_data = MachineData(
    #             date=message_date,
    #             time=message_time,
    #             machine_id=machine,
    #             data={machine_id: machine_data_content},
    #             device_id=device,
    #             log_data_id=log_data,
    #             timestamp=str(timestamp)
    #         )
    #         machine_data.save()
    #         if enable_printing:
    #           print(f'Saved machine data to database: {machine_data}')

    #     except Exception as e:
    #         errors.append({
    #             "status": "DATA SAVE ERROR",
    #             "message": f"Error saving machine data: {e}",
    #             "device_token": device_token,
    #             "timestamp": timestamp,
    #         })
    #         if enable_printing:
    #           print(f'Error saving machine data to database: {e}')
    #         continue  # Continue with the next machine data

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

    response = {
        "status": "OK",
        "message": "Successfully saved data",
        "device_token": device_token,
        "timestamp": timestamp
    }
    publish_response(mqtt_client, device_token, response)
    
    if enable_printing:
      print(f'Saved device data to database: {device_data}')
    
    if errors:
        for error in errors:
            publish_response(mqtt_client, device_token, error, is_error=True)
        return False

    return True

def handle_production_data(mqtt_client, message_data, log_data):
    setting = Setting.objects.first()
    enable_printing = setting.enable_printing if setting else False

    end_shift_time_str = settings.END_SHIFT_TIME
    end_shift_number = settings.END_SHIFT_NUMBER

    if isinstance(end_shift_time_str, str):
        end_shift_time = datetime.datetime.strptime(end_shift_time_str, "%H:%M:%S").time()
    else:
        # If end_shift_time_str is already a time object, use it directly
        end_shift_time = end_shift_time_str

    timestamp = message_data['timestamp']
    # dt = datetime.datetime.utcfromtimestamp(timestamp)
    dt = datetime.datetime.fromtimestamp(timestamp)
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
            # errors.append(f"No machine found for machine_id: {machine_id}")
            if enable_printing:
              print(f"No machine found for machine_id: {machine_id}")
            continue

        try:
            last_production_data = ProductionData.objects.filter(machine_id=machine.machine_id, timestamp__lt = timestamp).order_by('-timestamp').first()
        except Exception as e:
           pass

        # print ("Last production:",last_production_data.date,last_production_data.time,last_production_data.shift_number, last_production_data.machine_id, last_production_data.production_count, last_production_data.target_production)
        # if last_production_data and last_production_data.production_count > production_count:
        #     errors.append({
        #         "status": "PRODUCTION COUNT ERROR",
        #         "message": "Production count is less than last recorded count for " + machine_id,
        #         "device_token": device_token,
        #         "production_count": production_count,
        #         "timestamp": timestamp
        #     })
        #     print('Production count is less than the last recorded count')
        #     continue

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
            if not last_production_data or last_production_data.shift_number != shift_instance.shift_number or last_production_data.target_production != machine.production_per_hour or last_production_data.production_count != production_count or last_production_data.production_date != production_date:
                if last_production_data or production_count == 0 and last_production_data.shift_name == shift_instance.shift_number:
                   pass
                else:
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
                # print ("Production:",production_data.date,production_data.time,production_data.shift_number, production_data.machine_id, production_data.production_count, production_data.target_production)

                    if enable_printing:
                        print(f'Saved production data to database: {production_data}')

        except Exception as e:
            errors.append({
                "status": "DATA SAVE ERROR",
                "message": f"Error saving production data: {e}",
                "device_token": device_token,
                "timestamp": timestamp,
            })
            if enable_printing:
              print(f'Error saving production data to database: {e}')
            continue
    # print()   
    # if errors:
    #     for error in errors:
    #         response = {
    #             "status": "ERROR",
    #             "message": error
    #         }
    #         publish_response(mqtt_client, device_token, response, is_error=True)
    #     return False

    # response = {
    #     "status": "OK",
    #     "message": "Successfully saved data",
    #     "device_token": device_token,
    #     "timestamp": timestamp
    # }
    # publish_response(mqtt_client, device_token, response)

    # return True

    







mqtt_client = mqtt.Client()
MAX_RECONNECT_ATTEMPTS = 5  # Maximum number of reconnection attempts
RECONNECT_DELAY = 5  # Delay between reconnection attempts in seconds


def get_mqtt_settings():
    setting = Setting.objects.first()
    enable_printing = setting.enable_printing if setting else False

    try:
        mqtt_settings = MqttSettings.objects.first()
        return mqtt_settings.__dict__

    except MqttSettings.DoesNotExist:
        if enable_printing:
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
        if enable_printing:
           print ("Error in getting MQTT settings:",e)


def on_disconnect(client, userdata, rc):
    setting = Setting.objects.first()
    enable_printing = setting.enable_printing if setting else False

    if rc != 0:
        if enable_printing:
          print("Unexpected disconnection.")
        attempt_reconnect(client)


def attempt_reconnect(client):
    setting = Setting.objects.first()
    enable_printing = setting.enable_printing if setting else False
    attempt = 0
    while attempt < MAX_RECONNECT_ATTEMPTS:
        try:
            mqtt_settings = get_mqtt_settings()
            client.username_pw_set(mqtt_settings["username"], mqtt_settings["password"])
            client.connect(mqtt_settings["host"], mqtt_settings["port"], mqtt_settings["keepalive"])
            client.loop_start()
            if enable_printing:
               print("Reconnected successfully.")
            return  # Exit the loop if reconnection is successful
        except Exception as e:
            attempt += 1
            if enable_printing:
              print(f"Reconnection attempt {attempt}/{MAX_RECONNECT_ATTEMPTS} failed: {e}")
            time.sleep(RECONNECT_DELAY)
    if enable_printing:
       print("Failed to reconnect after multiple attempts.")

def start_mqtt_client():
    setting = Setting.objects.first()
    enable_printing = setting.enable_printing if setting else False

    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
    mqtt_client.on_disconnect = on_disconnect

    mqtt_settings = get_mqtt_settings()
    
    try:
        mqtt_client.username_pw_set(mqtt_settings["username"], mqtt_settings["password"])
        mqtt_client.connect(mqtt_settings["host"], mqtt_settings["port"], mqtt_settings["keepalive"])
        mqtt_client.loop_forever()
    except Exception as e:
        if enable_printing:
           print("MQTT not connected. Error:", e)
        attempt_reconnect(mqtt_client)

start_mqtt_client()