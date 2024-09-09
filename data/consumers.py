from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
import json

class DataConsumer(WebsocketConsumer):
    def connect(self):
        self.room_name = "productionMonitor"
        self.room_group_name = "productionMonitorGroup"
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,self.channel_name
        )
        self.accept()
        print ("connected successfully")
        # self.send(text_data=json.dumps({"message": "Test connection successfull"}))

    def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]

        # self.send(text_data=json.dumps({"message": message}))
        print("message from",self.channel_name,">",message)
    

    def sendmqttmessage(self, event):
        # print (event)
        self.send(text_data=json.dumps(event['value']))

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name, self.channel_name
        )