import os

from django.core.exceptions import ImproperlyConfigured


def default_logging(DEBUG_LEVEL='INFO'):
    return {
        'version': 1,
        'disable_existing_loggers': True,
        'formatters': {
            'standard': {
                'format': '%(asctime)s [%(levelname)s]- %(message)s'}

        },
        'handlers': {
            'console': {
                'level': DEBUG_LEVEL,
                'class': 'logging.StreamHandler',
                'formatter': 'standard'
            }
        },
        'loggers': {
            'info': {
                'handlers': ["console"],
                'level': DEBUG_LEVEL,
                'propagate': True
            },
            'django': {
                'handlers': ['console'],
                'level': DEBUG_LEVEL,
                'propagate': True,
            },
            'django.request': {
                'handlers': ['console'],
                'level': DEBUG_LEVEL,
                'propagate': True,
            }
        },
    }


def load_environment(ENV_VARS: dict, local_vars):
    vars_not_filled = []

    ENV_VARS.setdefault('SECRET_KEY', {'required': True})
    ENV_VARS.setdefault('DEBUG', {'required': False, 'default': True, 'parse': lambda val: True if val == 'True' else False})

    for key, attrs in ENV_VARS.items():
        attrs.setdefault('default', '')
        attrs.setdefault('required', False)
        attrs.setdefault('parse', lambda val: str(val))

        tmp_value = os.environ.get(key, attrs.get('default'))

        if not isinstance(tmp_value, list):
            value = attrs.get('parse')(tmp_value)
        else:
            value = tmp_value

        if attrs.get('required') and not value:
            vars_not_filled.append(key)
        else:
            local_vars[key] = value

    if vars_not_filled:
        raise ImproperlyConfigured(f'Fill this {vars_not_filled} environment variables')

    return local_vars
