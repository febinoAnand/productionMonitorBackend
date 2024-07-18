import paho.mqtt.client as mqtt
import requests
from univaProductionMonitor.settings import *
import json
import datetime
import uuid 
from data.models import LogData,DeviceData,MachineData
from devices.models import DeviceDetails,MachineDetails
# mqttServer = "localhost"
# mqttPort = 1883
# mqttKeepAlive = 60
#
# httpHost = "localhost"
# httpPort = 8000

univaPublish = "univaPublish"
univaSubscribe = "univaSub/#"

requestList = ["POST","GET","DELETE","PUT","PATCH"]


# from Andon.models import LiveData, MachineDetail, MQTTConfig, MachineError, TechnicianDetail


def on_connect(mqtt_client, userdata, flags, rc):
    if rc == 0:
        print('Connected successfully')
        mqtt_client.subscribe(univaSubscribe)
        mqtt_client.publish(univaPublish,"test connection")
    else:
        print('Bad connection. Code:', rc)

mqtt_client = mqtt.Client()

def publish_response(topic, response):
    mqtt_client.publish(topic, json.dumps(response))
    print("Response Published:",response)

def on_message(mqtt_client, userdata, msg):
    print(f'Received message on topic: {msg.topic} with payload: {msg.payload}')
    currentTopic = msg.topic.split("/")
    currentMessage = msg.payload.decode()
    print(currentTopic)
    print(currentMessage)

    current_date = datetime.date.today()
    current_time = datetime.datetime.now().time()
    unique_id = str(uuid.uuid4())

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
        print(f'Error saving log data to database: {e}')
    
    try:
        message_data = json.loads(currentMessage)
        timestamp = message_data.get('timestamp')
        device_token = message_data.get('device_token')
        machine_id = next((key for key in message_data if key.isdigit()), None)

        if not machine_id:
            raise ValueError("Machine ID not found in message data")
        
        try:
            device = DeviceDetails.objects.get(device_token=device_token)
            machine = MachineDetails.objects.get(machine_id=machine_id)
            
            # Save MachineData
            machine_data = MachineData(
                date=current_date,
                time=current_time,
                machine_id=machine,
                data=message_data,
                device_id=device,
                data_id=log_data
            )
            machine_data.save()
            print(f'Saved machine data to database: {machine_data}')

            # Save DeviceData
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
                "status": "ok",
                "message": "Successfully data saved",
                "timestamp": timestamp,
                "device_token": device_token
            }
            publish_response(msg.topic, response)

        except DeviceDetails.DoesNotExist:
            response = {
                "status": "DEVICE NOT FOUND",
                "message": "Device not found with given token",
                "timestamp": timestamp,
                "device_token": device_token
            }
            publish_response(msg.topic, response)
            print('Device token mismatch')
        except MachineDetails.DoesNotExist:
            response = {
                "status": "MACHINE NOT FOUND",
                "message": "Machine not found with given ID",
                "timestamp": timestamp,
                "device_token": device_token
            }
            publish_response(msg.topic, response)
            print('Machine ID mismatch')

    except json.JSONDecodeError as e:
        response = {
            "status": "ERROR JSON",
            "message": "Not a valid JSON received",
            "timestamp": int(datetime.datetime.now().timestamp()),
            "device_token": ""
        }
        publish_response(msg.topic, response)
        print(f'Error decoding JSON: {e}')
    except ValueError as e:
        response = {
            "status": "MACHINE ID ERROR",
            "message": str(e),
            "timestamp": int(datetime.datetime.now().timestamp()),
            "device_token": device_token
        }
        publish_response(msg.topic, response)
        print(f'Error processing message: {e}')
try:
    # mqttconfig = MQTTConfig.objects.get(MQTT_ID=1)
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.username_pw_set("","")
    client.connect(
        host=mqttServer,
        port=mqttPort,
        keepalive=mqttKeepAlive
    )

except Exception as e:
    print (e)


