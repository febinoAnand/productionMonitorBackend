from rest_framework import serializers
from .models import MqttSettings,UART

class MQTTSerializer(serializers.ModelSerializer):
    class Meta:
        model = MqttSettings
        fields = '__all__'

class UARTSerializer(serializers.ModelSerializer):
    class Meta:
        model = UART
        fields = '__all__'