
# QGIS Home Page News Feed

This application is the backend part that manages and serves news for the QGIS welcome page.


## Installation

- create a virtual env

    `$ virtualenv qgisfeedvenv`

- activate the virtual env:

    `$ source qgisfeedvenv/bin/activate`

- install dependencies:

    `$ pip install -r REQUIREMENTS.txt`

- create a postgresql DB:

    `$ createdb qgisfeed`

- enable postgis:

    `$ psql qgisfeed -c 'CREATE EXTENSION postgis;'`

- create `settings_local.py` and put your DB configuration as in the example below:

    ```python
    DATABASES = {
        'default': {
            'ENGINE': 'django.contrib.gis.db.backends.postgis',
            'NAME': 'qgisfeed',
            'USER': 'your_username',
            'PASSWORD': 'your_password',
            'HOST': 'localhost',
            'PORT': '5432'
        }
    }
    ```

- run migrations, from the `qgisfeedproject` directory:

    `python manage.py migrate`

- create an admin user and set a password:

    `$ python manage.py createsuperuser`

- start the development server:

    `python manage.py runserver`

