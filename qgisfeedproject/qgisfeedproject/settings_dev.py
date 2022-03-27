from .settings import *  # noqa

# Settings local for docker compose

ALLOWED_HOSTS=['*']

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'qgisfeed',
        'USER': 'docker',
        'PASSWORD': 'docker',
        'HOST': 'postgis',
        'PORT': '5432'
    }
}
