from django.utils.translation import gettext_lazy as _
from rest_framework import exceptions, status


class ValidationException(exceptions.ValidationError):
    def __init__(self, detail=None, code=None):
        if isinstance(detail, str):
            detail = {'detail': detail}

        super(ValidationException, self).__init__(detail, code)


class FailedDependency(exceptions.APIException):
    status_code = status.HTTP_424_FAILED_DEPENDENCY
    default_detail = _('Failed dependency.')
    default_code = 'failed_dependency'


class IMATeapot(exceptions.APIException):
    status_code = status.HTTP_418_IM_A_TEAPOT
    default_detail = _("I'm a teapot.")
    default_code = 'im_a_teapot'
