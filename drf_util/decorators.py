from functools import wraps
from rest_framework.request import Request

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
