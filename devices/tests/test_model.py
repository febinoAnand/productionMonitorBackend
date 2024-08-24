from django.test import TestCase
from django.core.exceptions import ValidationError
from devices.models import DeviceDetails, MachineDetails, MachineGroup, ShiftTimings, ShiftTiming, RFID, UnRegisteredDevice, Token
from django.contrib.auth.models import User
import uuid
from datetime import time

class DeviceDetailsModelTest(TestCase):
    
    def setUp(self):
        self.device = DeviceDetails.objects.create(
            device_name='Device1',
            device_token='token123',
            protocol='mqtt',
            pub_topic='pub/topic',
            sub_topic='sub/topic'
        )

    def test_device_creation(self):
        self.assertEqual(self.device.device_name, 'Device1')
        self.assertEqual(self.device.device_token, 'token123')
        self.assertEqual(self.device.protocol, 'mqtt')

    def test_protocol_validation(self):
        device = DeviceDetails(
            device_name='Device2',
            device_token='token124',
            protocol='mqtt'
        )
        with self.assertRaises(ValidationError):
            device.clean()

        device = DeviceDetails(
            device_name='Device3',
            device_token='token125',
            protocol='http'
        )
        with self.assertRaises(ValidationError):
            device.clean()

class MachineDetailsModelTest(TestCase):
    
    def setUp(self):
        self.device = DeviceDetails.objects.create(
            device_name='Device1',
            device_token='token123',
            protocol='mqtt',
            pub_topic='pub/topic',
            sub_topic='sub/topic'
        )
        self.machine = MachineDetails.objects.create(
            machine_name='Machine1',
            machine_id='ID123',
            device=self.device
        )

    def test_machine_creation(self):
        self.assertEqual(self.machine.machine_name, 'Machine1')
        self.assertEqual(self.machine.machine_id, 'ID123')

class MachineGroupModelTest(TestCase):
    
    def setUp(self):
        self.device = DeviceDetails.objects.create(
            device_name='Device1',
            device_token='token123',
            protocol='mqtt',
            pub_topic='pub/topic',
            sub_topic='sub/topic'
        )
        self.machine1 = MachineDetails.objects.create(
            machine_name='Machine1',
            machine_id='ID123',
            device=self.device
        )
        self.machine2 = MachineDetails.objects.create(
            machine_name='Machine2',
            machine_id='ID124',
            device=self.device
        )
        self.group = MachineGroup.objects.create(
            group_name='Group1'
        )
        self.group.machine_list.add(self.machine1, self.machine2)

    def test_group_creation(self):
        self.assertEqual(self.group.group_name, 'Group1')
        self.assertIn(self.machine1, self.group.machine_list.all())
        self.assertIn(self.machine2, self.group.machine_list.all())

    def test_machine_assignment_validation(self):
        group2 = MachineGroup.objects.create(
            group_name='Group2'
        )
        group2.machine_list.add(self.machine1)
        with self.assertRaises(ValidationError):
            self.group.clean()

class ShiftTimingsModelTest(TestCase):
    
    def setUp(self):
        self.shift = ShiftTimings.objects.create(
            shift_number=1,
            start_time=time(8, 0),  # 08:00:00
            end_time=time(16, 0)    # 16:00:00
        )

    def test_shift_creation(self):
        self.assertEqual(self.shift.shift_number, 1)
        self.assertEqual(self.shift.start_time, time(8, 0))
        self.assertEqual(self.shift.end_time, time(16, 0))

class ShiftTimingModelTest(TestCase):
    
    def setUp(self):
        self.shift = ShiftTiming.objects.create(
            shift_number=1,
            start_time=time(8, 0),  # 08:00:00
            end_time=time(16, 0)    # 16:00:00
        )

    def test_shift_creation(self):
        self.assertEqual(self.shift.shift_number, 1)
        self.assertEqual(self.shift.start_time, time(8, 0))
        self.assertEqual(self.shift.end_time, time(16, 0))

class RFIDModelTest(TestCase):
    
    def setUp(self):
        self.user = User.objects.create(username='testuser')
        self.rfid = RFID.objects.create(
            rfid='RFID123',
            rfidUser=self.user
        )

    def test_rfid_creation(self):
        self.assertEqual(self.rfid.rfid, 'RFID123')
        self.assertEqual(self.rfid.rfidUser, self.user)

class UnRegisteredDeviceModelTest(TestCase):
    
    def setUp(self):
        self.device = UnRegisteredDevice.objects.create(
            sessionID=uuid.uuid4(),
            deviceID='ID123',
            devicePassword='password',
            OTP=1234
        )

    def test_unregistered_device_creation(self):
        self.assertEqual(self.device.deviceID, 'ID123')
        self.assertEqual(self.device.devicePassword, 'password')

class TokenModelTest(TestCase):
    
    def setUp(self):
        self.device = DeviceDetails.objects.create(
            device_name='Device1',
            device_token='token123',
            protocol='mqtt',
            pub_topic='pub/topic',
            sub_topic='sub/topic'
        )
        self.token = Token.objects.create(
            deviceID=self.device,
            token='tokenABC'
        )

    def test_token_creation(self):
        self.assertEqual(self.token.token, 'tokenABC')
        self.assertEqual(self.token.deviceID, self.device)
