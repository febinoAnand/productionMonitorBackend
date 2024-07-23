
from django.urls import path, include
from .views import (
    ProblemViewSet, 
    RawDataViewset, 
    LastProblemViewSet, 
    RawGetMethod,
    LiveDataViewset,
    MachineLiveDataViewset,
    LogDataViewSet, 
    DeviceDataViewSet, 
    MachineDataViewSet, 
    ProductionDataViewSet, 
    DashboardViewSet,
    ProductionMonitorViewSet,
    ShiftReportViewSet,
    SummaryReportViewSet,
    ShiftwiseReportGenerateViewSet,
    ListAchievementsViewSet,
    EmployeeDetailViewSet
)
from rest_framework import routers

router = routers.DefaultRouter()
router.register('problem', ProblemViewSet)
router.register('lastproblem', LastProblemViewSet)
router.register('logdata', LogDataViewSet)
router.register('devicedata', DeviceDataViewSet)
router.register('machinedata', MachineDataViewSet)
router.register('productiondata', ProductionDataViewSet)
router.register('raw', RawDataViewset)
router.register('dashboard', DashboardViewSet, basename='dashboard')
router.register('production-monitor', ProductionMonitorViewSet, basename='production-monitor')
router.register(r'shift-report', ShiftReportViewSet, basename='shift-report')
router.register(r'summary-report', SummaryReportViewSet, basename='summary-report')
router.register(r'shiftwise-report', ShiftwiseReportGenerateViewSet, basename='shiftwise-report-generate')
router.register(r'list_achievements', ListAchievementsViewSet, basename='list_achievements')
router.register(r'employee-Detail', EmployeeDetailViewSet,basename="employee-Detail")
urlpatterns = [
    path('livedata', LiveDataViewset.as_view()),
    path('machinelivedata', MachineLiveDataViewset.as_view()),
    path('rawdata', RawGetMethod.as_view()),
    path('', include(router.urls)),
]
