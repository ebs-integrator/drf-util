from django.test import TestCase

from drf_util.tests import BaseTestCase, CRUDTestCase
from tests.models import Thing


class ViewsTestCase(BaseTestCase, TestCase):
    def test_swagger(self):
        response = self.client.get('/swagger/?format=openapi').json()
        self.assertEqual(len(response['schemes']), 2)


class ThingViewCRUDTestCase(CRUDTestCase, TestCase):
    fixtures = ['tests/fixtures.json']
    base_view = 'things'
    queryset = Thing.objects.all()
    fake_data = {
        'title': 'Thing name'
    }


class ThingRelatedRelatedCRUDTestCase(CRUDTestCase, TestCase):
    fixtures = ['tests/fixtures.json']
    base_view = 'things-related'
    queryset = Thing.objects.all()
    fake_data = {
        'title': 'Thing name'
    }
