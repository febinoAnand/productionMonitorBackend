from django.urls import path,include
from rest_framework import routers
from .views import MQTTViewSet,UARTViewSet,HttpsSettingsViewSet


router = routers.DefaultRouter()
# router.register('mqtt', MQTTViewSet)
# router.register('uart',UARTViewSet)
router.register('mqttsettings', MQTTViewSet)
router.register('httpsettings', HttpsSettingsViewSet)

urlpatterns = [
    path('',include(router.urls))
]