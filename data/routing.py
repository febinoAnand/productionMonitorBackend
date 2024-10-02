from django.urls import re_path
from .consumers import DataConsumer, ProductionConsumer, ShiftReportConsumer

websocker_urlpatterns = [
    re_path(r'data/dashboard-data/',DataConsumer.as_asgi()),
    re_path(r'data/production/', ProductionConsumer.as_asgi()),
    # re_path(r'data/individual-report/', ShiftReportConsumer.as_asgi()),
    re_path(r'data/individual-report/(?P<machine_id>\w+)/$', ShiftReportConsumer.as_asgi()),
]
