from django.contrib import admin
from .models import RawData,ProblemData,LastProblemData
from .models import LogData, DeviceData, MachineData, ProductionData
# Register your models here.
# class RawDataAdmin(admin.ModelAdmin):
#     list_display = ["datetime", "data"]
#     readonly_fields = ['datetime','data',]
#     fields = ['datetime','data']

#     def has_add_permission(self, request, obj=None):
#         return False

#     def has_change_permission(self, request, obj=None):
#         return False

#     # def has_delete_permission(self, request, obj=None):
#     #     return False


# class ProblemDataAdmin(admin.ModelAdmin):
#     list_display = ["dateTimeNow","eventID","eventGroupID","machineID","issueTime","acknowledgeTime","endTime"]
#     fields = ["dateTimeNow","date","time","eventID","eventGroupID","machineID","deviceID","issueTime","acknowledgeTime","endTime"]
#     readonly_fields = ["dateTimeNow"]

#     def has_add_permission(self, request):
#         return False
#     def has_change_permission(self, request, obj=None):
#         return False


# class LastProblemDataAdmin(admin.ModelAdmin):
#     list_display = ["dateTimeNow","eventID","eventGroupID","machineID","issueTime","acknowledgeTime","endTime"]
#     fields = ["dateTimeNow","date","time","eventID","eventGroupID","machineID","deviceID","issueTime","acknowledgeTime","endTime"]
#     readonly_fields = ["dateTimeNow"]

#     def has_add_permission(self, request):
#         return False
#     def has_change_permission(self, request, obj=None):
#         return False
    
class LogDataAdmin(admin.ModelAdmin):
    list_display = ('date', 'time', 'data_id', 'received_data')
    search_fields = ('data_id', 'protocol', 'topic_api')
    list_filter = ('date', 'protocol', 'data_id')

class DeviceDataAdmin(admin.ModelAdmin):
    list_display = ('date', 'time', 'device_id', "timestamp" ,'data')
    search_fields = ('device_id__device_token', 'protocol', 'topic_api')
    list_filter = ('date', 'device_id__device_token', 'protocol', 'device_id')


class MachineDataAdmin(admin.ModelAdmin):
    list_display = ( 'date', 'time','machine_id', 'device_id','data', 'create_date_time')
    search_fields = ('machine_id__machine_id', 'device_id__device_token')
    list_filter = ('date', 'machine_id__machine_id', 'device_id__device_token')

class ProductionDataAdmin(admin.ModelAdmin):
    list_display = ( 'date', 'time','shift_number', 'machine_id', 'production_count', 'target_production','production_date')
    search_fields = ('shift_name', 'machine_id')
    list_filter = ('date','time','shift_number')

admin.site.register(LogData, LogDataAdmin)
admin.site.register(DeviceData, DeviceDataAdmin)
admin.site.register(MachineData, MachineDataAdmin)
admin.site.register(ProductionData, ProductionDataAdmin)
# admin.site.register(RawData,RawDataAdmin)
# admin.site.register(ProblemData,ProblemDataAdmin)
# admin.site.register(LastProblemData,LastProblemDataAdmin)