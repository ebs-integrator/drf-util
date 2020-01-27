from functools import wraps
from rest_framework.request import Request
from django.core.cache import cache
from datetime import datetime, timedelta
import time
from drf_util.exceptions import ValidationException


def serialize_decorator(serializer_method, preview_function=None, read_params=False, partial=False):
    def _new_decorator(view_func):
        def _decorator(*args, **kwargs):
            request = next(filter(lambda arg: isinstance(arg, Request), args))

            if request.method in ["POST", "PATCH", "PUT"]:
                data = request.query_params if read_params else request.data
            else:
                data = request.query_params

            # if need to change data before serialize
            if preview_function:
                data = data.copy()
                data = preview_function(data)

            # serialize data
            serializer = serializer_method(data=data, partial=partial, context={"request": request})
            if serializer.is_valid():
                request.valid = serializer.validated_data
                request.serializer = serializer
                return view_func(*args, **kwargs)

            # if data not is valid
            raise ValidationException(serializer.errors)

        return wraps(view_func)(_decorator)

    return _new_decorator


# ======================================================================================================================
# Semaphore decorator
# ======================================================================================================================
def await_checker(key, step):
    """
        Function for checking time for starting function
        @param {string} key - cache key, usually it's function name
        @param {integer} step - seconds to next usage
        @return None
    """
    now_date = datetime.now()
    # getting next date to using this function
    next_use_date = cache.get(key, datetime.now())
    # define how much seconds need to wait
    seconds = (next_use_date - now_date).total_seconds()
    if seconds < 0:
        # sleep can't be negative second, set 0
        seconds = 0
    # override next date to using this function
    set_await(key, seconds + step)
    time.sleep(seconds)


def set_await(key, seconds):
    """
        Function for define and override next date to using function
        @param {string} key
        @param {integer} seconds
        @return None
    """
    next_date = datetime.now() + timedelta(seconds=seconds)
    cache.set(key, next_date, seconds)


def await_process_decorator(rate=20, period=60):
    """
    decorator for some function, checking and updating time to waiting for use this function
    @param {integer} rate : count of usage some function, by default it's 20 times
    @param {integer} period : period of usage some function,  by default it's 1 minute
    """

    def decorator(function):
        def wrapper(*args, **kwargs):
            # define step, by default it's 20 times in 1 minute
            step = period / rate
            # checking time
            await_checker(function.__name__, step)
            # running function, after waiting
            return function(*args, **kwargs)

        return wrapper

    return decorator
