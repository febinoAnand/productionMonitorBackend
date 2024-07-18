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

    def has_add_permission(self, request):
        return False

admin.site.register(UnRegisteredDevice,UnRegisteredDeviceAdmin)


class TokenAdmin(admin.ModelAdmin):
    list_display = ["deviceID","token","createdAt"]
    fields = ["deviceID","token","createdAt"]
    readonly_fields = ["createdAt"]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


admin.site.register(Token, TokenAdmin)



class DeviceDetailsAdmin(admin.ModelAdmin):
    list_display = ('device_name', 'device_token', 'hardware_version', 'software_version', 'protocol', 'create_date_time')
    search_fields = ('device_name', 'device_token', 'protocol')

class MachineDetailsAdmin(admin.ModelAdmin):
    list_display = ('machine_id', 'line', 'manufacture', 'year', 'device', 'create_date_time')
    search_fields = ('machine_id', 'line', 'manufacture', 'year')

class MachineGroupAdmin(admin.ModelAdmin):
    list_display = ('group_name',)
    search_fields = ('group_name',)
    filter_horizontal = ('machine_list',)  

class ShiftTimingsAdmin(admin.ModelAdmin):
    list_display = ('shift_name', 'start_time', 'end_time', 'create_date_time')
    search_fields = ('shift_name',)

admin.site.register(DeviceDetails, DeviceDetailsAdmin)
admin.site.register(MachineDetails, MachineDetailsAdmin)
admin.site.register(MachineGroup, MachineGroupAdmin)
admin.site.register(ShiftTimings, ShiftTimingsAdmin)