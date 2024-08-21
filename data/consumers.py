import json
import redis
from channels.generic.websocket import AsyncWebsocketConsumer

class DeviceDataConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        print(f'WebSocket connected: {self.channel_name}')

        await self.accept()

        default_data = {
            'date': '2024-08-21',
            'time': '00:00:00',
            'data': {
                'device_id': '100',
                'value': '123'
            },
            'message': 'Default data sent on connect'
        }

        await self.send(text_data=json.dumps({
            'type': 'send_device_data',
            'data': default_data
        }))

    async def disconnect(self, close_code):
        print(f'WebSocket disconnected: {self.channel_name}, close code: {close_code}')

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            print(f'Received data from WebSocket: {data}')

            await self.handle_device_data(data)

            await self.send(text_data=json.dumps({
                'type': 'receive_data',
                'data': data
            }))
        except json.JSONDecodeError as e:
            print(f'Error parsing WebSocket message: {e}')

    async def handle_device_data(self, data):
        redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)
        sorted_set_key = 'device_data'

        timestamp = data.get('timestamp', 0)
        device_id = data.get('device_id', 'default_device')
        redis_client.zadd(sorted_set_key, {json.dumps(data): timestamp})

        min_element = redis_client.zrange(sorted_set_key, 0, 0, withscores=True)
        if min_element:
            min_data, _ = min_element[0]
            min_data = json.loads(min_data)

            await self.send(text_data=json.dumps({
                'type': 'send_device_data',
                'data': min_data
            }))

            redis_client.zrem(sorted_set_key, json.dumps(min_data))

    async def send_device_data(self, event):
        data = event['data']
        await self.send(text_data=json.dumps({
            'type': 'send_device_data',
            'data': data
        }))
