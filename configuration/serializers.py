from rest_framework import serializers
from .models import MqttSettings,UART,HttpsSettings, Setting

class MQTTSerializer(serializers.ModelSerializer):
    class Meta:
        model = MqttSettings
        fields = '__all__'

class UARTSerializer(serializers.ModelSerializer):
    class Meta:
        model = UART
        fields = '__all__'

class HttpsSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = HttpsSettings
        fields = '__all__'

class SettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Setting
        fields = ('__all__')