
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

## Settings

To prevent DDOS attacks there is limit in the number of returned records (defaults to 20): it can be configured by overriding the settings in `settings_local.py` with:

```python
QGISFEED_MAX_RECORDS=40  # default value is 20
```

## Endpoint and accepted parameters

The application has a single endpoint available at the web server root `/` the reponse is in JSON format.

Example call: http://localhost:8000/

Returned data:
```json
[
  {
    "title": "QGIS acquired by ESRI",
    "image": "http://localhost:8000/media/feedimages/image.png",
    "content": "<p>QGIS is finally part of the ESRI ecosystem, it has been rebranded as CrashGIS to better integrate with ESRI products line.</p>",
    "url": "https://www.qgis.com",
    "sticky": true
  },
  {
    "title": "Null Island QGIS Meeting",
    "image": "",
    "content": "<p>Let's dive in the ocean together!</p>",
    "url": null,
    "sticky": false
  },
  {
    "title": "QGIS Italian Meeting",
    "image": "",
    "content": "<p>Ciao from Italy!</p>",
    "url": null,
    "sticky": false
  }
]
```

### Available parameters for filters

The following parameters can be passed by the client to filter available records.

Parameters are validated and in case they are not valid a `Bad Request` HTTP error code `400` is returned.

#### lang

When `lang` is passed, the records that have a different `lang` will be excluded from the results. Only the records with `null` `lang` and the records with a matching `lang` will be returned.

Accepted values: `ISO-939-1` two letters language code

Example call: http://localhost:8000/?lang=de

#### lat lon (location)

When `lat` **and** `long` are passed, the records that have a location filter set will be returned only if the point defined by `lat` and `lon` is within record's location.

Accepted values: `ESPG:4326` latitude and longitude

Example call: http://localhost:8000/?lat=44.5&lon=9.23


## Docker

For development purposes only, you can run this application in debug mode with docker compose:

```bash
$ docker compose up
```

A set of test data will be automatically loaded and the application will be available at http://localhost:8000

To enter the control panel http://localhost:8000/admin the credentials are `admin`/`admin`