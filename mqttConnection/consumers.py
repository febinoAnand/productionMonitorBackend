import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import async_to_sync
import paho.mqtt.client as mqtt

class MqttConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        # Start the MQTT client here if needed

    async def disconnect(self, close_code):
        # Handle disconnection
        pass

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Here you could publish the message to an MQTT topic
        # or handle it as needed

        await self.send(text_data=json.dumps({
            'message': message
        }))
