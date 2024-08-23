from django.test import TestCase
from events.models import ProblemCode, Indicator, Button, Event, EventGroup
from devices.models import MachineDetails, DeviceDetails
from django.contrib.auth.models import User

class ProblemCodeModelTest(TestCase):

    def setUp(self):
        ProblemCode.objects.create(
            problemCode="P001",
            problemName="Overheating",
            problemDescription="Machine is overheating",
            problemType="ISSUE"
        )

    def test_problem_code_creation(self):
        problem = ProblemCode.objects.get(problemCode="P001")
        self.assertEqual(problem.problemName, "Overheating")
        self.assertEqual(problem.problemDescription, "Machine is overheating")
        self.assertEqual(problem.problemType, "ISSUE")
        self.assertEqual(str(problem), "Overheating")

class IndicatorModelTest(TestCase):

    def setUp(self):
        Indicator.objects.create(
            indicatorID="I001",
            indicatorpin=1,
            indicatorColor="#FF0000",
            indicatorColorName="Red"
        )

    def test_indicator_creation(self):
        indicator = Indicator.objects.get(indicatorID="I001")
        self.assertEqual(indicator.indicatorpin, 1)
        self.assertEqual(indicator.indicatorColor, "#FF0000")
        self.assertEqual(indicator.indicatorColorName, "Red")
        self.assertEqual(str(indicator), "I001 - Red")

class ButtonModelTest(TestCase):

    def setUp(self):
        Button.objects.create(
            buttonID="B001",
            buttonName="Start",
            buttonColorName="Green",
            buttonColor="#00FF00",
            buttonDO=1,
            buttonMode="AUTO"
        )

    def test_button_creation(self):
        button = Button.objects.get(buttonID="B001")
        self.assertEqual(button.buttonName, "Start")
        self.assertEqual(button.buttonColorName, "Green")
        self.assertEqual(button.buttonColor, "#00FF00")
        self.assertEqual(button.buttonDO, 1)
        self.assertEqual(button.buttonMode, "AUTO")
        self.assertEqual(str(button), "Start")

class EventModelTest(TestCase):

    def setUp(self):
        user = User.objects.create_user(username="testuser", password="password")
        button = Button.objects.create(
            buttonID="B001",
            buttonName="Start",
            buttonColorName="Green",
            buttonColor="#00FF00",
            buttonDO=1,
            buttonMode="AUTO"
        )
        problem = ProblemCode.objects.create(
            problemCode="P001",
            problemName="Overheating",
            problemDescription="Machine is overheating",
            problemType="ISSUE"
        )
        indicator = Indicator.objects.create(
            indicatorID="I001",
            indicatorpin=1,
            indicatorColor="#FF0000",
            indicatorColorName="Red"
        )
        self.event = Event.objects.create(
            eventID="E001",
            button=button,
            problem=problem,
            indicator=indicator
        )
        self.event.acknowledgeUser.add(user)
        self.event.notifyUser.add(user)

    def test_event_creation(self):
        event = Event.objects.get(eventID="E001")
        self.assertEqual(event.button.buttonName, "Start")
        self.assertEqual(event.problem.problemName, "Overheating")
        self.assertEqual(event.indicator.indicatorColorName, "Red")
        self.assertEqual(event.acknowledgeUser.count(), 1)
        self.assertEqual(event.notifyUser.count(), 1)
        self.assertEqual(str(event), "E001")

class EventGroupModelTest(TestCase):

    def setUp(self):
        device = DeviceDetails.objects.create(device_name="Device001")

        button = Button.objects.create(
            buttonID="B001",
            buttonName="Start",
            buttonColorName="Green",
            buttonColor="#00FF00",
            buttonDO=1,
            buttonMode="AUTO"
        )

        problem = ProblemCode.objects.create(
            problemCode="P001",
            problemName="Overheating",
            problemDescription="Machine is overheating",
            problemType="ISSUE"
        )

        indicator = Indicator.objects.create(
            indicatorID="I001",
            indicatorpin=1,
            indicatorColor="#FF0000",
            indicatorColorName="Red"
        )

        event = Event.objects.create(
            eventID="E001",
            button=button,
            problem=problem,
            indicator=indicator
        )

        machine = MachineDetails.objects.create(
            device=device
        )

        self.event_group = EventGroup.objects.create(
            groupID="G001",
            groupName="Group 1"
        )
        self.event_group.events.add(event)
        self.event_group.machines.add(machine)

    def test_event_group_creation(self):
        group = EventGroup.objects.get(groupID="G001")
        self.assertEqual(group.groupName, "Group 1")
        self.assertEqual(group.events.count(), 1)
        self.assertEqual(group.machines.count(), 1)
        self.assertIn("E001", group.selectedEvents())
        self.assertEqual(str(group), "G001")