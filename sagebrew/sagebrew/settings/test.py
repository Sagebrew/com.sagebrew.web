from base import *
from os import environ

DEBUG = False

TEMPLATE_DEBUG = DEBUG
ALLOWED_HOSTS = ['*']
WEB_ADDRESS = "https://127.0.0.1:8080"
VERIFY_SECURE = False
CELERY_IGNORE_RESULT = False
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': environ.get("DB_DOCKER_NAME", 'circle_test'),
        'USER': environ.get("DB_USER", 'ubuntu'),
        'PASSWORD': environ.get("DB_PASSWORD", ''),
        'HOST': environ.get("DB_PORT_5432_TCP_ADDR", '127.0.0.1'),
        'PORT': environ.get("DB_PORT_5432_TCP_PORT", '5432')
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
    }
}



CELERY_RESULT_BACKEND = 'redis://127.0.0.1:6379/0'
DEFAULT_FILE_STORAGE = 'sagebrew.s3utils.MediaRootS3BotoStorage'
STATICFILES_STORAGE = 'sagebrew.s3utils.StaticRootS3BotoStorage'

S3_URL = 'https://%s.s3.amazonaws.com/' % (AWS_STORAGE_BUCKET_NAME)

STATIC_URL = "%s" % (S3_URL)
MEDIA_URL = "%s%s" % (S3_URL, "media/")
EMAIL_VERIFICATION_URL = "https://localhost/registration/email_confirmation/"
BROKER_URL = 'amqp://%s@%s:%s//' % (environ.get("QUEUE_USERNAME", ""),
                                    environ.get("QUEUE_HOST", ""),
                                    environ.get("QUEUE_PORT", ""))


REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS':
        'rest_framework.pagination.LimitOffsetPagination',
    'EXCEPTION_HANDLER': 'sb_base.utils.custom_exception_handler',
    'PAGE_SIZE': 25,
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    ),
    'DEFAULT_MODEL_SERIALIZER_CLASS':
        'rest_framework.serializers.HyperlinkedModelSerializer',
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'oauth2_provider.ext.rest_framework.OAuth2Authentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
}


ELASTIC_SEARCH_HOST = [{'host': '127.0.0.1'}]


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'loggly': {
            'format': 'loggly: %(message)s',
        },
    },
    'handlers': {
        'logentries_handler': {
            'token': LOGENT_TOKEN,
            'class': 'logentries.LogentriesHandler'
        },
    },
    'loggers': {
        'django.db': {
            'handlers': ['logentries_handler'],
            'level': 'ERROR',
            'propagate': False,
        },
        'loggly_logs': {
            'handlers': ['logentries_handler'],
            'propagate': True,
            'format': 'loggly: %(message)s',
            'level': 'DEBUG',
        },
        'elasticsearch': {
            'handlers': ['logentries_handler'],
            'propagate': True,
            'format': 'loggly: %(message)s',
            'level': 'CRITICAL',
        },
        'neomodel.properties': {
            'handlers': ['logentries_handler'],
            'propagate': True,
            'format': 'loggly: %(message)s',
            'level': 'CRITICAL',
        },
        'elasticsearch.trace': {
            'handlers': ['logentries_handler'],
            'propagate': True,
            'format': 'loggly: %(message)s',
            'level': 'CRITICAL',
        },
        'django.request': {
            'handlers': ['logentries_handler'],
            'level': 'ERROR',
            'propagate': False,
        },
    }
}