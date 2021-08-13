SECRET_KEY = 'fake-key'
INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.auth',
    'tests',
]
ROOT_URLCONF = 'tests.urls'
DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3'}}
APPS_PATH = 'tests'
