from django.urls import re_path
from .consumers import DataConsumer, ProductionConsumer

websocker_urlpatterns = [
    re_path(r'data/dashboard-data/',DataConsumer.as_asgi()),
    re_path(r'data/production/$', ProductionConsumer.as_asgi()),
]
