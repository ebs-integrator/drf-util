from datetime import datetime
from threading import Thread

from django.test import TestCase

from drf_util.decorators import await_process_decorator, await_checker, set_await


@await_process_decorator(5, 7)
def simple_print(text):
    print(datetime.now(), text)


class DecoratorsTests(TestCase):

    def test_await_process_decorator(self):
        result = set_await("test", 2)
        self.assertEqual(result, None)
        result = await_checker("test", 2)
        self.assertEqual(result, None)
        for i in range(5):
            thread = Thread(target=simple_print, kwargs={"text": "try #%s" % i})
            # thread starting
            print("start thread #", i)
            thread.start()
