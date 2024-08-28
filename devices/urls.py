from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MachineViewSet, DeviceViewSet, UnRegisteredViewSet, MachineGroupViewSet, ShiftTimingViewSet, DeviceVerification, TokenAuthentication, UnRegisterViewSetPostMethod

router = DefaultRouter()
router.register(r'machine', MachineViewSet, basename='machine')
router.register(r'device', DeviceViewSet, basename='device')
router.register(r'unregister', UnRegisteredViewSet, basename='unregister')
router.register(r'machinegroup', MachineGroupViewSet, basename='machinegroup')
router.register(r'shifttimings', ShiftTimingViewSet, basename='shifttimings')

urlpatterns = [
    path('verify/', DeviceVerification.as_view(), name='verify'),
    path('getToken/', TokenAuthentication.as_view(), name='get-token'),
    path('register/', UnRegisterViewSetPostMethod.as_view(), name='register'),
    path('', include(router.urls)),
]

