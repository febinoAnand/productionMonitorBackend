
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
    EmployeeDetailViewSet,
    TableReportViewSet,
    GroupWiseMachineDataViewSet,
    GroupMachineDataViewSet,
    ProductionViewSet,
    HourlyShiftReportViewSet,
    MachineHourlyDataViewSet,
    IndividualViewSet,
    ShiftDataViewSet,
    AchievementsViewSet,
    IndividualShiftReportViewSet
)
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'problems', ProblemViewSet, basename='problem')
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
router.register(r'table-report', TableReportViewSet, basename='TableReportViewSet')
router.register(r'group-wise-machine-data', GroupWiseMachineDataViewSet, basename='group-wise-machine-data')
router.register(r'group-machine-data', GroupMachineDataViewSet, basename='group-machine-data')
router.register(r'machine-hourly-data', MachineHourlyDataViewSet, basename='machine-hourly-data')
router.register(r'individual', IndividualViewSet, basename='individual')



router.register(r'dashboard-data', ShiftDataViewSet, basename='dashboard-data') #dashboard URL
router.register(r'individual-report', IndividualShiftReportViewSet, basename='individual-report'),  #individual dashbaord
router.register(r'production', ProductionViewSet, basename='production')    #production page
router.register(r'hourly-shift-report', HourlyShiftReportViewSet, basename='hourly-shift-report'),  #shift-report page
router.register(r'achievements', AchievementsViewSet, basename='achievements')  #achivements page







urlpatterns = [
    path('livedata', LiveDataViewset.as_view()),
    path('machinelivedata', MachineLiveDataViewset.as_view()),
    path('rawdata', RawGetMethod.as_view()),
    path('', include(router.urls)),
]
