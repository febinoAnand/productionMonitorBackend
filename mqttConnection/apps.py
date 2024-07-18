from django.apps import AppConfig


class MqttconnectionConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'mqttConnection'

    def ready(self):
        from mqttConnection import mqtt
        mqtt.client.loop_start()
