import paho.mqtt.client as mqtt
import requests
from univaProductionMonitor.settings import *
import json
import datetime


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
    else:
        print('Bad connection. Code:', rc)


def on_message(mqtt_client, userdata, msg):
    print(f'Received message on topic: {msg.topic} with payload: {msg.payload}')
    currentTopic = msg.topic.split("/")
    currentMessage = msg.payload
    print (currentTopic)
    print (currentMessage)


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


