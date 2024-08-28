from django.test import TestCase
from django.urls import reverse, resolve
from rest_framework.test import APIClient
from smsgateway.views import SendReportViewSet, SettingViewSet


class URLTestCase(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_sendreport_viewset_url(self):
        url = reverse('sendreport-list')
        self.assertEqual(resolve(url).func.__name__, SendReportViewSet.__name__)

    def test_setting_viewset_url(self):
        url = reverse('setting-list')
        self.assertEqual(resolve(url).func.__name__, SettingViewSet.__name__)
