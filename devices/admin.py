from django.contrib import admin
from .models import *

# Register your models here.

# admin.site.register(Token)



# class RFIDAdmin(admin.ModelAdmin):
#     list_display = ["rfid","rfidUser"]
# admin.site.register(RFID,RFIDAdmin)

class UnRegisteredDeviceAdmin(admin.ModelAdmin):
    list_display = ["sessionID","deviceID","model","OTP","createdAt"]
    fields = ["sessionID","deviceID","devicePassword","model","hardwareVersion","softwareVersion","OTP","createdAt"]
    readonly_fields = ["createdAt","OTP","sessionID","deviceID"]
    list_filter = ["model", "createdAt"] 

    def has_add_permission(self, request):
        return False

admin.site.register(UnRegisteredDevice,UnRegisteredDeviceAdmin)


class TokenAdmin(admin.ModelAdmin):
    list_display = ["deviceID","token","createdAt"]
    fields = ["deviceID","token","createdAt"]
    readonly_fields = ["createdAt"]
    list_filter = ["createdAt"]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


admin.site.register(Token, TokenAdmin)


class DeviceDetailsAdmin(admin.ModelAdmin):
    list_display = ('device_name', 'device_token', 'hardware_version', 'software_version', 'protocol', 'create_date_time')
    search_fields = ('device_name', 'device_token', 'protocol')
    list_filter = ('device_name', 'device_token', 'protocol', 'create_date_time')

class MachineDetailsAdmin(admin.ModelAdmin):
    list_display = ('machine_id','machine_name', 'line', 'device', 'production_per_hour', 'create_date_time', 'status')
    search_fields = ('machine_id', 'line', 'manufacture', 'year')
    list_filter = ('machine_id', 'device', 'machine_name', 'create_date_time')


# class ShiftTimingsAdmin(admin.ModelAdmin):
#     list_display = ('shift_number','shift_name', 'start_time', 'end_time', 'create_date_time')
#     search_fields = ('shift_name',)


class ShiftTimingAdmin(admin.ModelAdmin):
    list_display = ('shift_number','shift_name', 'start_time', 'end_time', 'create_date_time')
    search_fields = ('shift_name',)
    list_filter = ('shift_number', 'shift_name', 'create_date_time')

class MachineGroupAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

    def save_related(self, request, form, formsets, change):
        form.instance.save()  
        super().save_related(request, form, formsets, change)
        form.instance.clean() 

    list_filter = ('group_name', 'machine_list')

admin.site.register(DeviceDetails, DeviceDetailsAdmin)
admin.site.register(MachineDetails, MachineDetailsAdmin)
admin.site.register(MachineGroup, MachineGroupAdmin)
admin.site.register(ShiftTiming, ShiftTimingAdmin)