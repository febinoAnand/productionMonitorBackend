from django.test import TestCase
from django.contrib.auth.models import User, Group
from pushnotification.models import SendReport, NotificationAuth, Setting
from unittest.mock import patch

class SendReportModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.group = Group.objects.create(name='testgroup')
        self.noti_auth = NotificationAuth.objects.create(user_to_auth=self.user, noti_token='dummy_token')

    @patch('requests.post')
    def test_send_report_creation(self, mock_post):
        mock_post.return_value.status_code = 200
        mock_post.return_value.reason = 'OK'

        report = SendReport.objects.create(
            date='2024-08-22',
            time='12:00:00',
            title='Test Report',
            message='This is a test report message.',
            send_to_user=self.user,
            users_group=self.group
        )

        self.assertEqual(report.title, 'Test Report')
        self.assertEqual(report.message, 'This is a test report message.')
        self.assertEqual(report.send_to_user, self.user)
        self.assertEqual(report.users_group, self.group)
        self.assertEqual(report.delivery_status, "200 - OK")

    @patch('requests.post')
    def test_send_report_no_notification_auth(self, mock_post):
        NotificationAuth.objects.get(user_to_auth=self.user).delete()
        mock_post.return_value.status_code = 200
        mock_post.return_value.reason = 'OK'

        report = SendReport(
            date='2024-08-22',
            time='12:00:00',
            title='Test Report',
            message='This is a test report message.',
            send_to_user=self.user,
            users_group=self.group
        )
        report.save()
        self.assertEqual(report.delivery_status, '200 - OK')

    @patch('requests.post')
    def test_send_report_exception_handling(self, mock_post):
        mock_post.side_effect = Exception("Test exception")

        report = SendReport(
            date='2024-08-22',
            time='12:00:00',
            title='Test Report',
            message='This is a test report message.',
            send_to_user=self.user,
            users_group=self.group
        )
        report.save()
        self.assertTrue(report.delivery_status.startswith('Error:'))

class NotificationAuthModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')

    def test_notification_auth_creation(self):
        noti_auth = NotificationAuth.objects.create(
            user_to_auth=self.user,
            noti_token='dummy_token'
        )
        self.assertEqual(noti_auth.user_to_auth, self.user)
        self.assertEqual(noti_auth.noti_token, 'dummy_token')

class SettingModelTest(TestCase):

    def test_setting_creation(self):
        setting = Setting.objects.create(
            application_name='MyApp',
            application_id='app_id_123'
        )
        self.assertEqual(setting.application_name, 'MyApp')
        self.assertEqual(setting.application_id, 'app_id_123')

    def test_singleton_behavior(self):
        Setting.objects.create(
            application_name='MyApp',
            application_id='app_id_123'
        )
        with self.assertRaises(ValueError):
            Setting.objects.create(
                application_name='MyApp',
                application_id='app_id_456'
            )
