from django.test import TestCase
from events.models import Event, EventGroup
from data.models import MachineDetails, RFID, DeviceDetails, ShiftTimings
import datetime
from data.models import RawData, ProblemData, LastProblemData, LogData, DeviceData, MachineData, ProductionData

class ModelTestCase(TestCase):
    def setUp(self):
        # Create test data
        self.event = Event.objects.create(name="Test Event")
        self.event_group = EventGroup.objects.create(name="Test Event Group")
        self.device = DeviceDetails.objects.create(name="Test Device")
        self.machine = MachineDetails.objects.create(name="Test Machine")
        self.rfid = RFID.objects.create(code="123456")
        self.shift = ShiftTimings.objects.create(shift_name="Shift 1", start_time="08:00:00", end_time="16:00:00")

    def test_raw_data_creation(self):
        raw_data = RawData.objects.create(
            datetime=datetime.datetime.now(),
            data="Test data",
            date=datetime.date.today(),
            time=datetime.datetime.now().time(),
            eventID=self.event,
            deviceID=self.device,
            machineID=self.machine,
            eventGroupID=self.event_group
        )
        self.assertEqual(str(raw_data), str(raw_data.id))
        self.assertEqual(raw_data.data, "Test data")

    def test_problem_data_creation(self):
        problem_data = ProblemData.objects.create(
            date=datetime.date.today(),
            time=datetime.datetime.now().time(),
            eventID=self.event,
            eventGroupID=self.event_group,
            machineID=self.machine,
            deviceID=self.device,
            issueTime=datetime.datetime.now(),
            acknowledgeTime=None,
            rfidTime=self.rfid,
            endTime=None
        )
        self.assertEqual(str(problem_data), str(problem_data.eventGroupID))

    def test_last_problem_data_creation(self):
        last_problem_data = LastProblemData.objects.create(
            date=datetime.date.today(),
            time=datetime.datetime.now().time(),
            eventID=self.event,
            eventGroupID=self.event_group,
            deviceID=self.device,
            machineID=self.machine,
            issueTime=None,
            acknowledgeTime=None,
            rfidTime=self.rfid,
            endTime=None
        )
        self.assertEqual(str(last_problem_data), str(last_problem_data.eventGroupID))

    def test_log_data_creation(self):
        log_data = LogData.objects.create(
            date=datetime.date.today(),
            time=datetime.datetime.now().time(),
            received_data="Log data",
            protocol="HTTP",
            topic_api="test/topic",
            data_id="log123"
        )
        self.assertEqual(str(log_data), "log123")

    def test_device_data_creation(self):
        log_data = LogData.objects.create(
            date=datetime.date.today(),
            time=datetime.datetime.now().time(),
            received_data="Log data",
            protocol="HTTP",
            topic_api="test/topic",
            data_id="log123"
        )
        device_data = DeviceData.objects.create(
            date=datetime.date.today(),
            time=datetime.datetime.now().time(),
            data={"key": "value"},
            device_id=self.device,
            protocol="HTTP",
            topic_api="test/topic",
            timestamp="2024-08-21 12:00:00",
            log_data_id=log_data
        )
        self.assertEqual(str(device_data), self.device.name)

    def test_machine_data_creation(self):
        log_data = LogData.objects.create(
            date=datetime.date.today(),
            time=datetime.datetime.now().time(),
            received_data="Log data",
            protocol="HTTP",
            topic_api="test/topic",
            data_id="log123"
        )
        machine_data = MachineData.objects.create(
            date=datetime.date.today(),
            time=datetime.datetime.now().time(),
            machine_id=self.machine,
            data={"key": "value"},
            device_id=self.device,
            timestamp="2024-08-21 12:00:00",
            log_data_id=log_data
        )
        self.assertEqual(str(machine_data), self.machine.machine_name)

    def test_production_data_creation(self):
        production_data = ProductionData.objects.create(
            date=datetime.date.today(),
            time=datetime.datetime.now().time(),
            shift_number=1,
            shift_name="Shift 1",
            target_production=100,
            machine_id="machine123",
            machine_name="Machine 1",
            production_count=50,
            production_date=datetime.date.today(),
            log_data_id=1,
            timestamp="2024-08-21 12:00:00"
        )
        self.assertEqual(str(production_data), str(production_data.shift_number))
