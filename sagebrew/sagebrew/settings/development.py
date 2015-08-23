import requests
from base import *

DEBUG = True
TEMPLATE_DEBUG = DEBUG
ALLOWED_HOSTS = ['*']
TEST_RUNNER = 'sagebrew.test_runner.SBTestRunner'

INTERNAL_IPS = ('192.168.56.1',
                '127.0.0.1',
                '192.168.56.101',
                '192.168.56.101:8080',
                'sagebrew.local.dev',
                '192.168.33.15', ''
)

envips = environ.get("INTERNAL_IP", None)
if envips is not None:
    envips = envips.split("|")
    INTERNAL_IPS = INTERNAL_IPS + tuple(envips)

WEB_ADDRESS = "https://sagebrew.local.dev"

# This is here because locally we do not have ssl certification.
# Please ensure you are never hardcoding False into the requests
# calls
VERIFY_SECURE = False
if not VERIFY_SECURE:
    from requests.packages.urllib3.exceptions import (InsecureRequestWarning,
                                                      InsecurePlatformWarning)
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    requests.packages.urllib3.disable_warnings(InsecurePlatformWarning)

MEDIA_ROOT = PROJECT_DIR.child("media")
STATIC_ROOT = PROJECT_DIR.child("static")
STATIC_URL = '/static/'
MEDIA_URL = '/media/'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': environ.get("DATABASE_NAME", ""),
        'USER': environ.get("DATABASE_USER", ""),
        'PASSWORD': environ.get("DATABASE_PASSWORD", ""),
        'HOST': environ.get("DATABASE_IP", "127.0.0.1"),
        'PORT': '',
    }
}

CELERY_RESULT_BACKEND = 'redis://%s:%s/0' % (environ.get("REDIS_LOCATION", ""),
                                             environ.get("REDIS_PORT", ""))

EMAIL_VERIFICATION_URL = "%s/registration/email_confirmation/" % WEB_ADDRESS


BROKER_URL = 'amqp://%s:%s@%s:%s//' % (environ.get("QUEUE_USERNAME", ""),
                                        environ.get("QUEUE_PASSWORD", ""),
                                        environ.get("QUEUE_HOST", ""),
                                        environ.get("QUEUE_PORT", ""))
CELERY_IGNORE_RESULT = False
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS':
        'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 15,
    'MAX_PAGINATE_BY': 100,
    'PAGINATE_BY_PARAM': 'page_size',
    'EXCEPTION_HANDLER': 'sb_base.utils.custom_exception_handler',
    'DEFAULT_MODEL_SERIALIZER_CLASS':
        'rest_framework.serializers.HyperlinkedModelSerializer',
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
        'oauth2_provider.ext.rest_framework.OAuth2Authentication',
    )
}

ELASTIC_SEARCH_HOST = [{'host': environ.get("ELASTIC_SEARCH_HOST", "")}]


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
        'elasticsearch.trace': {
            'handlers': ['logentries_handler'],
            'propagate': True,
            'format': 'loggly: %(message)s',
            'level': 'CRITICAL',
        },
        'opbeat.errors': {
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
        'neomodel.util': {
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
