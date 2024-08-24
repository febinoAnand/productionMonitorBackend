from django.apps import AppConfig

class MqttConnectionConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'mqttConnection'

    # def ready(self):
    #     import mqttConnection.mqtt as mqtt
        
    #     mqtt.start_mqtt_client()

        