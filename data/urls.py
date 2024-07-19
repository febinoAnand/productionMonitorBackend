from django.urls import path, include
from .views import \
    ProblemViewSet, \
    RawDataViewset, \
    LastProblemViewSet, \
    RawGetMethod,\
    LiveDataViewset,\
    MachineLiveDataViewset,\
    LogDataViewSet, \
    DeviceDataViewSet, \
    MachineDataViewSet, \
    ProductionDataViewSet

from rest_framework import routers


router = routers.DefaultRouter()
router.register('problem',ProblemViewSet)
router.register('lastproblem',LastProblemViewSet)

router.register('logdata', LogDataViewSet)
router.register('devicedata', DeviceDataViewSet)
router.register('machinedata', MachineDataViewSet)
router.register('productiondata', ProductionDataViewSet)
router.register('raw', RawDataViewset)

urlpatterns = [
    path('livedata',LiveDataViewset.as_view()),
    path('machinelivedata',MachineLiveDataViewset.as_view()),
    path('rawdata',RawGetMethod.as_view()),
    path('',include(router.urls)),
    # path('',)
]
