from django.urls import path,include
from rest_framework import routers
from .views import MachineViewSet, DeviceViewSet, RFIDViewSet, UnRegisteredViewSet, DeviceVerification, TokenAuthentication, UnRegisterViewSetPostMethod, MachineGroupViewSet, ShiftTimingViewSet,MachineViewSetUpdated



router = routers.DefaultRouter()
router.register('machine',MachineViewSetUpdated)
router.register('device',DeviceViewSet)
# router.register('rfid',RFIDViewSet)
router.register('unregister', UnRegisteredViewSet)
router.register('machinegroup', MachineGroupViewSet)
router.register('shifttimings', ShiftTimingViewSet)

urlpatterns = [
    path('',include(router.urls)),
    path('verify/', DeviceVerification.as_view()),
    path('getToken/', TokenAuthentication.as_view()),
    path('register/', UnRegisterViewSetPostMethod.as_view()),


]
