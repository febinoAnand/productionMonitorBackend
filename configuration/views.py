from rest_framework import viewsets
from .serializers import MQTTSerializer, UARTSerializer, HttpsSettingsSerializer, SettingSerializer
from .models import MqttSettings, UART, HttpsSettings, Setting
from django.shortcuts import render
from rest_framework.response import Response

# Create your views here.
class MQTTViewSet(viewsets.ModelViewSet):
    schema = None
    serializer_class = MQTTSerializer
    queryset = MqttSettings.objects.all()
    http_method_names = ['get','put']

class UARTViewSet(viewsets.ModelViewSet):
    schema = None
    serializer_class = UARTSerializer
    queryset = UART.objects.all()
    http_method_names = ['get']

class HttpsSettingsViewSet(viewsets.ModelViewSet):
    queryset = HttpsSettings.objects.all()
    serializer_class = HttpsSettingsSerializer

class SettingViewSet(viewsets.ViewSet):
    serializer_class = SettingSerializer
    queryset = Setting.objects.all()