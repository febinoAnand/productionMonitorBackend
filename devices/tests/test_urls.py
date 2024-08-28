from django.test import TestCase, Client
from django.urls import reverse
from rest_framework import status

class URLTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.urls = {
            'machine-list': reverse('machine-list'),
            'device-list': reverse('device-list'),
            'unregister-list': reverse('unregister-list'),
            'machinegroup-list': reverse('machinegroup-list'),
            'shifttimings-list': reverse('shifttimings-list'),
            'verify': reverse('verify'),
            'get-token': reverse('get-token'),
            'register': reverse('register'),
        }

    def test_device_list_url(self):
        response = self.client.get(self.urls['device-list'])
        self.assertEqual(response.status_code, 200)

    def test_unregister_list_url(self):
        response = self.client.get(self.urls['unregister-list'])
        self.assertEqual(response.status_code, 200)

    def test_machine_list_url(self):
        response = self.client.get(self.urls['machine-list'])
        self.assertEqual(response.status_code, 200)

    def test_machinegroup_list_url(self):
        response = self.client.get(self.urls['machinegroup-list'])
        self.assertEqual(response.status_code, 200)

    def test_shifttimings_list_url(self):
        response = self.client.get(self.urls['shifttimings-list'])
        self.assertEqual(response.status_code, 200)

    def test_verify_url(self):
        response = self.client.post(self.urls['verify'], {
            'sessionID': 'some-session-id',
            'OTP': 'some-otp'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_get_token_url(self):
        response = self.client.post(self.urls['get-token'], {
            'deviceID': 'some-id',
            'devicePassword': 'password'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
