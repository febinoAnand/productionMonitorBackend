from django.contrib import admin
from .models import UART, MqttSettings, Port,HttpsSettings

class MqttSettingsAdmin(admin.ModelAdmin):
    list_display = ('server_name_alias', 'host', 'port', 'username', 'qos')
    search_fields = ('server_name_alias', 'host', 'username')

class HttpsSettingsAdmin(admin.ModelAdmin):
    list_display = ('api_path', 'auth_token')
    search_fields = ('api_path',)

admin.site.register(MqttSettings, MqttSettingsAdmin)
admin.site.register(HttpsSettings, HttpsSettingsAdmin)

