from django.urls import path,include
from .views import privacyView

urlpatterns = [
     path('',privacyView)
]
