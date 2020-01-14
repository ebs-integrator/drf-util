from django.test import TestCase

from drf_util import utils


class UtilsTests(TestCase):

    def test_dict_merge(self):
        a = {'a': {'c': 1, 'd': {'x': 1}}}
        b = {'a': {'e': 1, 'd': {'y': 1}}}
        c = {'a': {'c': 1, 'e': 1, 'd': {'x': 1, 'y': 1}}}
        self.assertEqual(utils.dict_merge(a, b), c)
        self.assertEqual(utils.dict_merge(a, {}), a)
        self.assertEqual(utils.dict_merge({}, b), b)

    def test_gt(self):
        data = {"a": {"b": 1, "c": [{"d": 2}, {"d": 3}]}}
        self.assertEqual(utils.gt(data, 'a.b'), 1)
        self.assertEqual(utils.gt(data, 'a.c.0.d'), 2)
        self.assertIsNone(utils.gt(data, 'a.b.c'))
        self.assertEqual(utils.gt(data, 'a.c.*.d'), [2, 3])

    def test_sf(self):
        def func():
            raise Exception('Test')

        def func_return():
            return 1

        self.assertIsNone(utils.sf(func))
        self.assertEqual(utils.sf(func_return), 1)

    def test_join_url(self):
        self.assertEqual(utils.join_url('http://test.com/', '/page.html'), 'http://test.com/page.html')
        self.assertEqual(utils.join_url('http://test.com/', 'page.html'), 'http://test.com/page.html')
        self.assertEqual(utils.join_url('http://test.com', '/page.html'), 'http://test.com/page.html')

    def test_get_object_labels(self):
        data = {"a": {"b": 'title'}, "c": 'test'}

        self.assertEqual(sorted(utils.get_object_labels(data)), sorted(['title', 'test']))
        self.assertEqual(utils.get_object_labels(data, ['c']), ['test'])

    def test_min_next(self):
        items = [4, 6, 1]
        self.assertEqual(utils.min_next(items, 2), 4)

    def test_date(self):
        self.assertEqual(utils.date('2019-03-18T09:28:29.540898+00:00').year, 2019)
        self.assertEqual(utils.date('2019-03-18T09:28:29.540898+00:00').month, 3)
        self.assertEqual(utils.date('2019-03-18T09:28:29.540898+00:00').day, 18)
        self.assertEqual(utils.date('2019-03-18T09:28:29.540898+00:00').hour, 9)
        self.assertEqual(utils.date('2019-03-18T09:28:29.540898+00:00').minute, 28)
        self.assertEqual(utils.date('2019-03-18T09:28:29.540898+00:00').second, 29)
        self.assertEqual(utils.date('2019-03-18T09:28:29.540898+00:00').microsecond, 540898)
