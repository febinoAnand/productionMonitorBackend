from django.test import TestCase
from django.core.exceptions import ValidationError
from configuration.models import Port, UART, MqttSettings, HttpsSettings

class PortModelTest(TestCase):
    def setUp(self):
        self.port = Port.objects.create(portname="COM1")

    def test_port_creation(self):
        self.assertTrue(isinstance(self.port, Port))
        self.assertEqual(str(self.port), "COM1")

class UARTModelTest(TestCase):
    def setUp(self):
        self.port = Port.objects.create(portname="COM1")
        self.uart = UART.objects.create(
            comport=self.port,
            baudrate=9600,
            parity="none",
            databit=8,
            stopbit=1.0,
            CTS=True,
            DTR=True,
            XON=True
        )

    def test_uart_creation(self):
        self.assertTrue(isinstance(self.uart, UART))
        self.assertEqual(str(self.uart), "COM1")

    def test_uart_default_values(self):
        self.assertEqual(self.uart.baudrate, 9600)
        self.assertEqual(self.uart.parity, "none")
        self.assertEqual(self.uart.databit, 8)
        self.assertEqual(self.uart.stopbit, 1.0)
        self.assertTrue(self.uart.CTS)
        self.assertTrue(self.uart.DTR)
        self.assertTrue(self.uart.XON)

class MqttSettingsModelTest(TestCase):
    def setUp(self):
        self.mqtt_settings = MqttSettings.objects.create(
            server_name_alias="TestServer",
            host="localhost",
            port=1883,
            username="user",
            password="pass",
            qos=1,
            keepalive=30,
            pub_topic="test/pub/topic",
            sub_topic="test/sub/topic"
        )

    def test_mqtt_settings_creation(self):
        self.assertTrue(isinstance(self.mqtt_settings, MqttSettings))
        self.assertEqual(str(self.mqtt_settings), "TestServer")

    def test_mqtt_settings_unique_instance(self):
        with self.assertRaises(ValidationError):
            MqttSettings.objects.create(
                server_name_alias="AnotherServer",
                host="localhost",
                port=1883,
                username="user",
                password="pass",
                qos=1,
                keepalive=30,
                pub_topic="another/pub/topic",
                sub_topic="another/sub/topic"
            ).save()

class HttpsSettingsModelTest(TestCase):
    def setUp(self):
        self.https_settings = HttpsSettings.objects.create(
            auth_token="12345",
            api_path="/api/v1/resource"
        )

    def test_https_settings_creation(self):
        self.assertTrue(isinstance(self.https_settings, HttpsSettings))
        self.assertEqual(str(self.https_settings), "/api/v1/resource")

    def test_https_settings_default_values(self):
        https_settings_without_path = HttpsSettings.objects.create()
        self.assertEqual(str(https_settings_without_path), "No API Path")
