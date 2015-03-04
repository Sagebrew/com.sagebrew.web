from base import *
from os import environ

DEBUG = False
TEMPLATE_DEBUG = DEBUG
ALLOWED_HOSTS = ['beta.sagebrew.com', 'www.sagebrew.com', 'sagebrew.com']
VERIFY_SECURE = True
WEB_ADDRESS = "https://www.sagebrew.com"

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': environ.get("RDS_DB_NAME", ""),
        'USER': environ.get("RDS_USERNAME", ""),
        'PASSWORD': environ.get("RDS_PASSWORD", ""),
        'HOST': environ.get("RDS_HOSTNAME", ""),
        'PORT': environ.get("RDS_PORT", ""),
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': environ.get("CACHE_LOCATION", "127.0.0.1:11211"),
    }
}

ELASTIC_SEARCH_HOST = [{'host': environ.get("ELASTIC_SEARCH_HOST", ""),
                        'port': environ.get("ELASTIC_SEARCH_PORT", ""),
                        'use_ssl': True,
                        'http_auth': (environ.get("ELASTIC_SEARCH_USER", ""),
                                      environ.get("ELASTIC_SEARCH_KEY", ""))
                       }]

CELERY_RESULT_BACKEND = 'redis://%s:%s/0' % (
    environ.get("REDIS_LOCATION", ""), environ.get("REDIS_PORT", ""))

BROKER_URL = "sqs://%s:%s@" % (
    environ.get("AWS_ACCESS_KEY_ID", ""),
    environ.get("AWS_SECRET_ACCESS_KEY", ""))


DEFAULT_FILE_STORAGE = 'sagebrew.s3utils.MediaRootS3BotoStorage'
STATICFILES_STORAGE = 'sagebrew.s3utils.StaticRootS3BotoStorage'

S3_URL = 'https://%s.s3.amazonaws.com/' % (AWS_STORAGE_BUCKET_NAME)
CELERY_IGNORE_RESULT = True
STATIC_URL = "%s" % (S3_URL)
MEDIA_URL = "%s%s" % (S3_URL, "media/")

BROKER_TRANSPORT_OPTIONS = {'visibility_timeout': 43200,
                            'polling_interval': 15}

CELERY_DEFAULT_QUEUE = "%s-%s-celery" % (environ.get("APP_NAME", ""),
                                         environ.get("CIRCLE_BRANCH", ""))

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    ),
    'DEFAULT_MODEL_SERIALIZER_CLASS':
        'rest_framework.serializers.HyperlinkedModelSerializer',
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.OAuth2Authentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
}


EMAIL_VERIFICATION_URL = "%s/registration/email_confirmation/" % WEB_ADDRESS

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
        'elasticsearch': {
            'handlers': ['logentries_handler'],
            'propagate': True,
            'format': 'loggly: %(message)s',
            'level': 'CRITICAL',
        },
        'loggly_logs': {
            'handlers': ['logentries_handler'],
            'propagate': True,
            'format': 'loggly: %(message)s',
            'level': 'ERROR',
        },
        'elasticsearch.trace': {
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
        'django.request': {
            'handlers': ['logentries_handler'],
            'level': 'ERROR',
            'propagate': False,
        },
    }
}