import paho.mqtt.client as mqtt
import json
import datetime
import uuid
from django.conf import settings
from django.db.models import ObjectDoesNotExist
from data.models import LogData, DeviceData, MachineData
from devices.models import DeviceDetails, MachineDetails

univaPublish = "univaPublish"
univaSubscribe = "univaSub/#"

def on_connect(mqtt_client, userdata, flags, rc):
    if rc == 0:
        print('Connected successfully')
        mqtt_client.subscribe(univaSubscribe)
        mqtt_client.publish(univaPublish, "test connection")
    else:
        print(f'Bad connection. Code: {rc}')

def publish_response(mqtt_client, topic, response, is_error=False):
    publish_topic = univaPublish
    result = mqtt_client.publish(publish_topic, json.dumps(response))
    print(f"Response Published to {publish_topic}: {response} with result {result}")

def on_message(mqtt_client, userdata, msg):
    print(f'Received message on topic: {msg.topic} with payload: {msg.payload}')
    currentTopic = msg.topic.split("/")
    currentMessage = msg.payload.decode()
    print(currentTopic)
    print(currentMessage)

    try:
        message_data = json.loads(currentMessage)

        # Handling the format with timestamp, device token, and data
        if 'timestamp' in message_data and 'device_token' in message_data:
            timestamp = message_data['timestamp']
            device_token = message_data['device_token']
            machine_id = next((key for key in message_data if key.isdigit()), None)

            if not machine_id:
                response = {
                    "status": "MACHINE ID ERROR",
                    "message": "Machine ID not found in message data",
                    "timestamp": timestamp,
                    "device_token": device_token
                }
                publish_response(mqtt_client, msg.topic, response, is_error=True)
                print('Machine ID not found in message data')
                return

            dt = datetime.datetime.fromtimestamp(timestamp)
            message_date = dt.date()
            message_time = dt.time()
            unique_id = str(timestamp)

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
                        publish_response(mqtt_client, msg.topic, response, is_error=True)
                        print('Timestamp is less than the first data in the log')
                        return
            except Exception as e:
                print(f'Error checking first log data: {e}')

            current_date = datetime.date.today()
            current_time = datetime.datetime.now().time()

            try:
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
            except Exception as e:
                if "UNIQUE constraint failed" in str(e):
                    response = {
                        "status": "DUPLICATE TIMESTAMP",
                        "message": "Timestamp data already updated",
                        "timestamp": timestamp,
                        "device_token": device_token
                    }
                    publish_response(mqtt_client, msg.topic, response, is_error=True)
                    print(f'Error saving log data to database: {e}')
                    return
                else:
                    response = {
                        "status": "LOG DATA ERROR",
                        "message": f"Error saving log data: {e}",
                        "timestamp": timestamp,
                        "device_token": device_token
                    }
                    publish_response(mqtt_client, msg.topic, response, is_error=True)
                    print(f'Error saving log data to database: {e}')
                    return

            try:
                device = DeviceDetails.objects.get(device_token=device_token)
                machine = MachineDetails.objects.get(machine_id=machine_id)

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

                response = {
                    "status": "OK",
                    "message": "Successfully data saved",
                    "timestamp": timestamp,
                    "device_token": device_token
                }
                publish_response(mqtt_client, msg.topic, response)

            except DeviceDetails.DoesNotExist:
                response = {
                    "status": "DEVICE NOT FOUND",
                    "message": "Device not found with given token",
                    "timestamp": timestamp,
                    "device_token": device_token
                }
                publish_response(mqtt_client, msg.topic, response, is_error=True)
                print('Device token mismatch')
            except MachineDetails.DoesNotExist:
                response = {
                    "status": "MACHINE NOT FOUND",
                    "message": "Machine not found with given ID",
                    "timestamp": timestamp,
                    "device_token": device_token
                }
                publish_response(mqtt_client, msg.topic, response, is_error=True)
                print('Machine ID mismatch')

        # Handling the command "TIMESTAMP"
        elif 'cmd' in message_data and message_data['cmd'] == "TIMESTAMP" and 'device_token' in message_data:
            device_token = message_data['device_token']
            current_timestamp = int(datetime.datetime.now().timestamp())

            response = {
                "status": "OK",
                "cmd_response": current_timestamp,
                "device_token": device_token
            }
            publish_response(mqtt_client, msg.topic, response)

        else:
            print("Unsupported message format")
            response = {
                "status": "DATA ERROR",
                "message": "Unsupported message format",
                
            }
            publish_response(mqtt_client, msg.topic, response)

    except json.JSONDecodeError as e:
        response = {
            "status": "ERROR JSON",
            "message": "Not a valid JSON received",
            "timestamp": timestamp,
            "device_token": device_token
        }
        publish_response(mqtt_client, msg.topic, response, is_error=True)
        print(f'Error decoding JSON: {e}')
    except ValueError as e:
        response = {
            "status": "VALUE ERROR",
            "message": str(e),
            "timestamp": timestamp,
            "device_token": device_token
        }
        publish_response(mqtt_client, msg.topic, response, is_error=True)
        print(f'Error processing message: {e}')


mqtt_client = mqtt.Client()

def start_mqtt_client():
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
    mqtt_client.username_pw_set("", "")
    mqtt_client.connect(
        host=settings.MQTT_SERVER,
        port=settings.MQTT_PORT,
        keepalive=settings.MQTT_KEEP_ALIVE
    )
    mqtt_client.loop_start()
