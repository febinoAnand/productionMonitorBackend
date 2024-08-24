from django.contrib import admin
from .models import UART, MqttSettings, Port,HttpsSettings, Setting

class MqttSettingsAdmin(admin.ModelAdmin):
    list_display = ('server_name_alias', 'host', 'port', 'username', 'qos','keepalive')
    search_fields = ('server_name_alias', 'host', 'username')

class HttpsSettingsAdmin(admin.ModelAdmin):
    list_display = ('api_path', 'auth_token')
    search_fields = ('api_path',)

class SettingAdmin(admin.ModelAdmin):
    list_display = ('id', 'enable_printing')
    def has_add_permission(self, request) :
        if Setting.objects.count() > 0:
            return False
        return True

admin.site.register(MqttSettings, MqttSettingsAdmin)
admin.site.register(HttpsSettings, HttpsSettingsAdmin)
admin.site.register(Setting, SettingAdmin)

