from django.urls import re_path
from .consumers import DataConsumer

websocker_urlpatterns = [
    re_path(r'data/dashboard-data/',DataConsumer.as_asgi())
]
