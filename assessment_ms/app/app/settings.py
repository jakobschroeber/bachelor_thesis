import os
import environ

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

env = environ.Env(
    # set casting, default value
    DEBUG=(bool, False)
)

# reading .env file
environ.Env.read_env(os.path.join(BASE_DIR, '../env/.env'))

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
        'NAME': os.path.join(BASE_DIR, 'app_db_.sqlite3'),
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
    },
    'cassandra': {
        'ENGINE': env('DJANGO_EXPORT_DB_ENGINE'),
        'NAME': env('DJANGO_EXPORT_DB_NAME'),
        'HOST': env('DJANGO_EXPORT_DB_HOST'),
        'OPTIONS': {
            'replication': {
                'strategy_class': env('DJANGO_EXPORT_DB_REPLICATION_STRATEGY_CLASS'),
                'replication_factor': int(env('DJANGO_EXPORT_DB_REPLICATION_FACTOR')),
            },
            'connection': {
                'retry_connect': bool(env('DJANGO_EXPORT_DB_CONNECTION_RETRY_CONNECT')),
                # + All connection options for cassandra.cluster.Cluster()
            },
            'session': {
                'default_timeout': int(env('DJANGO_EXPORT_DB_SESSION_DEFAULT_TIMEOUT')),
                'default_fetch_size': int(env('DJANGO_EXPORT_DB_SESSION_DEFAULT_FETCH_SIZE')),
                # + All options for cassandra.cluster.Session()
            }
        }
    }
}

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
