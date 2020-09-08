import os
import environ
import logging.config

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

env = environ.Env(
    # set casting, default value
    DEBUG=(bool, False),
    DJANGO_APP_LOG_LEVEL=(str, 'INFO'),
    CELERY_LOG_LEVEL=(str, 'INFO'),
    THIRD_PARTY_LOG_LEVEL=(str, 'INFO')
)

# reading .env file
environ.Env.read_env(os.path.join(BASE_DIR, '../env/.env'))

LOGGING_CONFIG = None

LOGGING= {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'timestamp': {
            'format': '{asctime} {name} {levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'timestamp'
        },
        'celery': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs/celery/celery.log'),
            'formatter': 'timestamp',
            'maxBytes': 1024*1024*10,
            'backupCount': 10
        },
        'django_app': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs/django_app/django_app.log'),
            'formatter': 'timestamp',
            'maxBytes': 1024*1024*10,
            'backupCount': 10
        },
        'third_party': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs/third_party/third_party.log'),
            'formatter': 'timestamp',
            'maxBytes': 1024*1024*10,
            'backupCount': 10
        },
    },
    'loggers': {
        '': {
            'handlers': ['console', 'third_party'],
            'level': env('THIRD_PARTY_LOG_LEVEL'),
        },
        'django': {
            'handlers': ['console', 'django_app'],
            'level': env('DJANGO_APP_LOG_LEVEL'),
            'propagate': False
        },
        'celery': {
            'handlers': ['console', 'celery'],
            'level': env('CELERY_LOG_LEVEL'),
            'propagate': False
        },
        'app': {
            'handlers': ['django_app'],
            'level': env('DJANGO_APP_LOG_LEVEL'),
            'propagate': False
        },
        'administration': {
            'handlers': ['django_app'],
            'level': env('DJANGO_APP_LOG_LEVEL'),
            'propagate': False
        },
        'assessment': {
            'handlers': ['django_app'],
            'level': env('DJANGO_APP_LOG_LEVEL'),
            'propagate': False
        },
        'data_source': {
            'handlers': ['django_app'],
            'level': env('DJANGO_APP_LOG_LEVEL'),
            'propagate': False
        },
        'export': {
            'handlers': ['django_app'],
            'level': env('DJANGO_APP_LOG_LEVEL'),
            'propagate': False
        },
    },
}

logging.config.dictConfig(LOGGING)

# Additional FileHandler in app.celery

# False if not in os.environ
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env('DJANGO_DEBUG')

# Raises django's ImproperlyConfigured exception if SECRET_KEY not in os.environ
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('DJANGO_SECRET_KEY')

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_ace',
    'django_celery_beat',
    'django_cassandra_engine',
    'rest_framework',
    # thanks to https://github.com/amancevice/docker-pandas
    'sklearn',

    #own
    'data_source',
    'administration',
    'assessment',
    'export',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'app.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, "templates")],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'app.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases
#
# adapted from https://dev.mysql.com/doc/connector-python/en/connector-python-django-backend.html

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'app_db.sqlite3'),
    },
    'moodle': {
        'ENGINE': env('DJANGO_MOODLE_DB_ENGINE'),
        'NAME': env('DJANGO_MOODLE_DB_NAME'),
        'HOST': env('DJANGO_MOODLE_DB_HOST'),
        'USER': env('DJANGO_MOODLE_DB_USER'),
        'PASSWORD': env('DJANGO_MOODLE_DB_PASSWORD'),
        'OPTIONS': {
            'raise_on_warnings': bool(env('DJANGO_MOODLE_DB_RAISE_ON_WARNINGS')),
        }
    }
}

# make connection to Cassandra optional at startup: try the connection with cassandra-driver, if successful add 'cassandra to DATABASES'

try:
    from cassandra.cluster import Cluster
    cluster = Cluster(contact_points=[env('DJANGO_EXPORT_DB_HOST')])
    session = cluster.connect()

    from export.db import update_connections
    update_connections()
except Exception:
    import logging
    log = logging.getLogger(__name__)
    log.info(f"Could not connect with database 'cassandra'. Please check connection data and status")

DATABASE_ROUTERS = ['app.db.Router']

FIXTURE_DIRS = ['./fixtures/']

# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'en-DE'

TIME_ZONE = 'Europe/Berlin'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = '/static/'