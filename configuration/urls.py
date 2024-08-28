from django.urls import path, include
from rest_framework.routers import DefaultRouter
from configuration.views import MQTTViewSet, HttpsSettingsViewSet

router = DefaultRouter()
router.register(r'mqttsettings', MQTTViewSet, basename='mqttsettings')
router.register(r'httpsettings', HttpsSettingsViewSet, basename='httpsettings')

urlpatterns = [
    path('',include(router.urls))
]