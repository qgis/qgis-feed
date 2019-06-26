
# Settings local for docker compose

DEBUG=False

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

MEDIA_ROOT = '/shared-volume/media/'
MEDIA_URL = '/media/'
STATIC_ROOT = '/shared-volume/static/'
STATIC_URL = '/static/'

