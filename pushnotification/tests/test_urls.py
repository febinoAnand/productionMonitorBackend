from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User, Group
from pushnotification.models import SendReport, NotificationAuth, Setting

class URLTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.login(username='testuser', password='testpassword')
        self.group = Group.objects.create(name='testgroup')
        self.notification_auth = NotificationAuth.objects.create(user_to_auth=self.user, noti_token='testtoken')
        self.setting = Setting.objects.create(application_name='TestApp', application_id='testid')
        self.send_report = SendReport.objects.create(
            date='2023-01-01',
            time='12:00:00',
            title='Test Report',
            message='This is a test report',
            send_to_user=self.user,
            users_group=self.group,
            delivery_status='-'
        )

    def test_send_report_list(self):
        url = reverse('sendreport-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_send_report_detail(self):
        url = reverse('sendreport-detail', args=[self.send_report.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_notification_auth_list(self):
        url = reverse('notificationauth-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_notification_auth_detail(self):
        url = reverse('notificationauth-detail', args=[self.notification_auth.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_setting_list(self):
        url = reverse('setting-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)