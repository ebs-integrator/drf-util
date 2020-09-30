from django.test import TestCase
from drf_util import models

from tests.models import Thing


class ModelsTests(TestCase):

    def test_get_default_languages(self):
        data = {
            'en': 'english',
            'ro': 'romanian',
        }

        self.assertEqual(models.get_default_languages(), {'en': None})
        self.assertEqual(models.get_lang_value(data), 'english')
        self.assertEqual(models.get_lang_value(data, 'ro'), 'romanian')
        self.assertIsNone(models.get_lang_value(data, 'ru'))

    def test_no_delete_model(self):
        first_thing = Thing.objects.create(title='First')

        self.assertEqual(None, first_thing.date_deleted)

        first_thing.delete()

        self.assertNotEqual(None, first_thing)
        self.assertNotEqual(None, first_thing.date_deleted)

        second_thing = Thing.objects.create(title='Second')

        self.assertEqual(None, second_thing.date_deleted)

        Thing.objects.all().delete()
        second_thing.refresh_from_db()

        self.assertNotEqual(None, second_thing)
        self.assertNotEqual(None, second_thing.date_deleted)

        self.assertEqual(0, Thing.objects.count())
        self.assertEqual(2, Thing.all_objects.count())

        # Check if test is running
        # self.assertEqual(True, False)
