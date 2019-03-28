from django.test import TestCase

from drf_util import models


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
