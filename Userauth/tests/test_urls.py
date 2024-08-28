from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from django.conf import settings
from rest_framework.authtoken.models import Token
from Userauth.models import UserDetail 
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase

class APIEndpointsTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.default_token = 'f82ee8560ff71d0036153bfab78c02cf23cf5e02'
        settings.APP_TOKEN = self.default_token

    def get_auth_token(self):
        return self.default_token

    def assertJsonResponse(self, response):
        content_type = response.get('Content-Type', '')
        self.assertTrue('application/json' in content_type or 'text/html' in content_type,
                        f"Expected 'application/json' or 'text/html' but got '{content_type}'")
        try:
            response_json = response.json()
        except ValueError:
            self.fail('Response content is not valid JSON')

    def test_user_login(self):
        response = self.client.post('/Userauth/userlogin/', 
                                    data={
                                        'username': 'admin1', 
                                        'password': 'admin1', 
                                        'app_token': self.get_auth_token(),
                                        'device_id': 'test_device_id',
                                        'notification_id': 'test_notification_id'
                                    },
                                    format='json')
        self.assertJsonResponse(response)
        
        if response.status_code == status.HTTP_200_OK:
            self.assertTrue(response.data['status'] in ['OK', 'INACTIVE', 'INVALID', 'DEVICE_MISMATCH'])
        else:
            print(response.data)
            self.fail(f"Unexpected status code: {response.status_code}")


class LogoutViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.default_token = 'f82ee8560ff71d0036153bfab78c02cf23cf5e02'
        settings.APP_TOKEN = self.default_token
        
        # Setup a test user and token
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.token = Token.objects.create(user=self.user)
        self.device_id = 'test_device_id'
        self.user_detail = UserDetail.objects.create(extUser_id=self.user.id, device_id=self.device_id)
        self.auth_header = f'Token {self.token.key}'

    def get_auth_token(self):
        return self.default_token

    def assertJsonResponse(self, response):
        content_type = response.get('Content-Type', '')
        self.assertTrue('application/json' in content_type,
                        f"Expected 'application/json' but got '{content_type}'")
        try:
            response_json = response.json()
        except ValueError:
            self.fail('Response content is not valid JSON')

    def test_logout_successful(self):
        response = self.client.post('/Userauth/userlogout/', 
                                    data={
                                        'app_token': self.get_auth_token(),
                                        'device_id': self.device_id
                                    },
                                    HTTP_AUTHORIZATION=self.auth_header,
                                    format='json')
        self.assertJsonResponse(response)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('status'), 'OK')

    def test_logout_invalid_device_id(self):
        response = self.client.post('/Userauth/userlogout/', 
                                    data={
                                        'app_token': self.get_auth_token(),
                                        'device_id': 'invalid_device_id'
                                    },
                                    HTTP_AUTHORIZATION=self.auth_header,
                                    format='json')
        self.assertJsonResponse(response)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data.get('status'), 'INVALID')
        self.assertEqual(response.data.get('message'), 'Invalid device ID')

    def test_logout_invalid_app_token(self):
        invalid_app_token = 'invalid_app_token'
        response = self.client.post('/Userauth/userlogout/', 
                                    data={
                                        'app_token': invalid_app_token,
                                        'device_id': self.device_id
                                    },
                                    HTTP_AUTHORIZATION=self.auth_header,
                                    format='json')
        self.assertJsonResponse(response)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data.get('status'), 'INVALID')
        self.assertEqual(response.data.get('message'), 'Invalid app token')
        
class URLTests(APITestCase):
    def test_weblogin_url_invalid_credentials(self):
        url = reverse('weblogin')
        response = self.client.post(url, data={
            'username': 'invaliduser',
            'password': 'invalidpassword'
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_weblogin_url_valid_credentials(self):
        from django.contrib.auth.models import User
        User.objects.create_user(username='admin1', password='admin1')

        url = reverse('weblogin')
        response = self.client.post(url, data={
            'username': 'admin1',
            'password': 'admin1'
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_weblogout_url(self):
        from django.contrib.auth.models import User
        from rest_framework.authtoken.models import Token
        
        user = User.objects.create_user(username='admin1', password='admin1')
        token = Token.objects.create(user=user)
        
        url = reverse('weblogout')
        response = self.client.post(url, data={
            'token': token.key
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
    def test_weblogin_invalid_request(self):
        url = reverse('weblogin')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_weblogout_invalid_request(self):
        url = reverse('weblogout')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)