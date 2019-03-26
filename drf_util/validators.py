from django.core.exceptions import ValidationError

DEFAULT_FIELD = "pk"


class ObjectExistValidator(object):
    def __init__(self, model, field=None):
        self.model = model
        self.field = field if field else DEFAULT_FIELD

    def __call__(self, value):
        message = "%s with %s:%s does not exists." % (self.model.__name__, self.field, value)
        try:
            if self.model.objects.filter(**{self.field: value}).exists():
                return value
        except ValidationError:
            message = "Validation error by this %s:%s" % (self.field, value)
        raise ValidationError(message)


class ObjectUniqueValidator(object):
    def __init__(self, model, field=None):
        self.model = model
        self.field = field if field else DEFAULT_FIELD

    def __call__(self, value):
        message = "%s with %s:%s already exists." % (self.model.__name__, self.field, value)
        try:
            if not self.model.objects.filter(**{self.field: value}).exists():
                return value
        except ValidationError:
            message = "Validation error by this %s:%s" % (self.field, value)
        raise ValidationError(message)


class PhoneValidator(object):
    def __init__(self):
        pass

    def __call__(self, value: str):
        list_approved = [" ", "(", ")", "+", "-"]
        check_value = value
        for key in list_approved:
            check_value = check_value.replace(key, "")
        try:
            int(check_value)
        except ValueError:
            raise ValidationError("Enter a valid phone number.")
        return value
