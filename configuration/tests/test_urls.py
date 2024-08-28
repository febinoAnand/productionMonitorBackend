from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from configuration.models import MqttSettings, HttpsSettings

class URLTests(APITestCase):
    def setUp(self):
        self.client = APIClient()

        self.mqtt_instance = MqttSettings.objects.create(
            server_name_alias="Test Server",
            host="test.mqtt.com",
            port=1883,
            username="testuser",
            password="testpass",
            qos=1,
            keepalive=60,
            pub_topic="test/pub/topic",
            sub_topic="test/sub/topic"
        )
        
        self.https_instance = HttpsSettings.objects.create(
            auth_token="testtoken",
            api_path="/api/test"
        )

    def test_mqttsettings_list(self):
        url = reverse('mqttsettings-list')
        print(f"MQTT Settings List URL: {url}")
        response = self.client.get(url)
        print(f"Response: {response.status_code}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_mqttsettings_update(self):
        url = reverse('mqttsettings-detail', kwargs={'pk': self.mqtt_instance.pk})
        data = {
            "server_name_alias": "Updated Server",
            "host": "updated.mqtt.com",
            "port": 1884,
            "username": "updateduser",
            "password": "updatedpass",
            "qos": 2,
            "keepalive": 120,
            "pub_topic": "updated/pub/topic",
            "sub_topic": "updated/sub/topic"
        }
        response = self.client.put(url, data, format='json')
        print(f"Response: {response.status_code}, Content: {response.content}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_httpsettings_list(self):
        url = reverse('httpsettings-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_httpsettings_update(self):
        url = reverse('httpsettings-detail', kwargs={'pk': self.https_instance.pk})
        data = {
            "auth_token": "updatedtoken",
            "api_path": "/api/updated"
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
