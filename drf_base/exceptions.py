from rest_framework import exceptions


class ValidationException(exceptions.ValidationError):
    def __init__(self, detail=None, code=None):
        if isinstance(detail, str):
            detail = {'detail': detail}

        super(ValidationException, self).__init__(detail, code)
