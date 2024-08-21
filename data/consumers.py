import json
import asyncio
import random
from datetime import datetime
from channels.generic.websocket import AsyncWebsocketConsumer

class DeviceDataConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        print(f'WebSocket connected: {self.channel_name}')
        await self.accept()
        self.send_random_data_task = asyncio.create_task(self.send_random_data())
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
        self.send_random_data_task.cancel()

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
        await self.send(text_data=json.dumps({
            'type': 'send_device_data',
            'data': data
        }))

    async def send_random_data(self):
        while True:
            random_value = random.randint(1, 100)
            random_device_id = random.randint(1, 1000)
            random_date = datetime.now().strftime('%Y-%m-%d')
            random_time = datetime.now().strftime('%H:%M:%S')
            random_message = f'Random data message {random.randint(1, 100)}'

            random_data = {
                'date': random_date,
                'time': random_time,
                'data': {
                    'device_id': str(random_device_id),
                    'value': str(random_value)
                },
                'message': random_message
            }

            await self.send(text_data=json.dumps({
                'type': 'send_device_data',
                'data': random_data
            }))
            await asyncio.sleep(5)
