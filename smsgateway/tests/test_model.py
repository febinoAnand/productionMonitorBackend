from django.test import TestCase
from django.core.exceptions import ValidationError
from smsgateway.models import SMSNumber, Setting, SendReport

class SMSNumberModelTest(TestCase):
    def setUp(self):
        self.sms_number = SMSNumber.objects.create(
            smsnumber="+1234567890",
            description="Test SMS Number"
        )

    def test_sms_number_creation(self):
        self.assertEqual(self.sms_number.smsnumber, "+1234567890")
        self.assertEqual(self.sms_number.description, "Test SMS Number")

    def test_sms_number_validation(self):
        with self.assertRaises(ValidationError):
            sms = SMSNumber(smsnumber="1234567890")
            sms.clean()

class SettingModelTest(TestCase):
    def setUp(self):
        self.setting = Setting.objects.create(
            sid="test_sid",
            auth_token="test_auth_token"
        )

    def test_setting_creation(self):
        self.assertEqual(self.setting.sid, "test_sid")
        self.assertEqual(self.setting.auth_token, "test_auth_token")

    def test_single_instance(self):
        with self.assertRaises(ValueError):
            Setting.objects.create(
                sid="another_sid",
                auth_token="another_auth_token"
            )

class SendReportModelTest(TestCase):
    def setUp(self):
        self.sms_number = SMSNumber.objects.create(
            smsnumber="+1234567890",
            description="Test SMS Number"
        )
        self.setting = Setting.objects.create(
            sid="test_sid",
            auth_token="test_auth_token"
        )
        self.report = SendReport.objects.create(
            to_number="+0987654321",
            from_number=self.sms_number,
            message="Test message"
        )

    def test_send_report_creation(self):
        self.assertEqual(self.report.to_number, "+0987654321")
        self.assertEqual(self.report.from_number, self.sms_number)
        self.assertEqual(self.report.message, "Test message")

    def test_send_report_validation(self):
        with self.assertRaises(ValidationError):
            report = SendReport(
                to_number="0987654321",
                from_number=self.sms_number,
                message="Test message"
            )
            report.clean()
