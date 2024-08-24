from django.test import TestCase
from django.contrib.auth.models import User
from Userauth.models import UnauthUser, UserDetail, Setting, Group
import uuid

class UnauthUserModelTestCase(TestCase):
    def setUp(self):
        self.unauth_user = UnauthUser.objects.create(
            mobile_no='1234567890',
            emailaddress='test@example.com',
            session_id=uuid.uuid4(),
            device_id='device-001',
        )

    def test_unauth_user_creation(self):
        self.assertTrue(isinstance(self.unauth_user, UnauthUser))
        self.assertEqual(str(self.unauth_user.mobile_no), '1234567890')
        self.assertEqual(str(self.unauth_user.emailaddress), 'test@example.com')
        self.assertIsNotNone(self.unauth_user.session_id)
        self.assertEqual(str(self.unauth_user.device_id), 'device-001')

    def test_otp_field(self):
        self.assertIsNone(self.unauth_user.otp)
        self.unauth_user.otp = '12345'
        self.unauth_user.save()
        self.assertEqual(self.unauth_user.otp, '12345')

    def test_otp_wrong_count_default(self):
        self.assertEqual(self.unauth_user.otp_wrong_count, 0)

class UserDetailModelTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.user_detail = UserDetail.objects.create(
            extUser=self.user,
            mobile_no='1234567890',
            device_id='device-002',
        )

    def test_user_detail_creation(self):
        self.assertTrue(isinstance(self.user_detail, UserDetail))
        self.assertEqual(str(self.user_detail.extUser.username), 'testuser')
        self.assertEqual(str(self.user_detail.mobile_no), '1234567890')
        self.assertEqual(str(self.user_detail.device_id), 'device-002')

    def test_designation_field(self):
        self.assertIsNone(self.user_detail.designation)
        self.user_detail.designation = 'Manager'
        self.user_detail.save()
        self.assertEqual(self.user_detail.designation, 'Manager')

    def test_employee_id_unique(self):
        self.user_detail.employee_id = 'EMP-001'
        self.user_detail.save()
        with self.assertRaises(Exception):
            UserDetail.objects.create(
                extUser=self.user,
                mobile_no='0987654321',
                device_id='device-003',
                employee_id='EMP-001'
            )

class SettingModelTestCase(TestCase):
    def setUp(self):
        self.setting = Setting.objects.create()

    def test_setting_defaults(self):
        self.assertEqual(self.setting.unAuth_user_expiry_time, 900)
        self.assertEqual(self.setting.all_user_expiry_time, 86400)
        self.assertEqual(self.setting.OTP_resend_interval, 20)
        self.assertEqual(self.setting.OTP_valid_time, 600)
        self.assertEqual(self.setting.OTP_call_count, 5)
        self.assertEqual(self.setting.OTP_wrong_count, 3)

class GroupModelTestCase(TestCase):
    def test_group_creation(self):
        group = Group.objects.create(name='Test Group')
        self.assertTrue(isinstance(group, Group))
        self.assertEqual(group.name, 'Test Group')
