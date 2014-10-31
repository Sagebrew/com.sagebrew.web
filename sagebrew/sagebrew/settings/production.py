from base import *
from os import environ

DEBUG = False
TEMPLATE_DEBUG = DEBUG
ALLOWED_HOSTS = ['beta.sagebrew.com', 'www.sagebrew.com', 'sagebrew.com']
WEB_ADDRESS = "https://sagebrew.com"
VERIFY_SECURE = True

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
        'BACKEND': 'django_elasticache.memcached.ElastiCache',
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

BROKER_TRANSPORT_OPTIONS = {'visibility_timeout': 43200}
CELERY_DEFAULT_QUEUE = "%s" % environ.get("CELERY_QUEUE", "")

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
        'logging.handlers.SysLogHandler': {
            'level': 'DEBUG',
            'class': 'logging.handlers.SysLogHandler',
            'facility': 'local5',
            'formatter': 'loggly',
        },
    },
    'loggers': {
        'django.db': {
            'handlers': ['logging.handlers.SysLogHandler'],
            'level': 'ERROR',
            'propagate': False,
        },
        'elasticsearch': {
            'handlers': ['logging.handlers.SysLogHandler'],
            'propagate': True,
            'format': 'loggly: %(message)s',
            'level': 'CRITICAL',
            'token': LOG_TOKEN
        },
        'loggly_logs': {
            'handlers': ['logging.handlers.SysLogHandler'],
            'propagate': True,
            'format': 'loggly: %(message)s',
            'level': 'ERROR',
            'token': LOG_TOKEN
        },
        'elasticsearch.trace': {
            'handlers': ['logging.handlers.SysLogHandler'],
            'propagate': True,
            'format': 'loggly: %(message)s',
            'level': 'CRITICAL',
            'token': LOG_TOKEN
        },
        'neomodel.properties': {
            'handlers': ['logging.handlers.SysLogHandler'],
            'propagate': True,
            'format': 'loggly: %(message)s',
            'level': 'CRITICAL',
            'token': LOG_TOKEN
        },
        'django.request': {
            'handlers': ['logging.handlers.SysLogHandler'],
            'level': 'ERROR',
            'propagate': False,
        },
    }
}