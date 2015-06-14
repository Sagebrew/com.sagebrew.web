from base import *
from os import environ

DEBUG = False
TEMPLATE_DEBUG = DEBUG
ALLOWED_HOSTS = ['www.sagebrew.com', ]

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

ELASTIC_SEARCH_HOST = [
    {
        'host': environ.get("ELASTIC_SEARCH_HOST", ""),
        'port': environ.get("ELASTIC_SEARCH_PORT", ""),
        'use_ssl': True,
        'http_auth': (environ.get("ELASTIC_SEARCH_USER", ""),
                      environ.get("ELASTIC_SEARCH_KEY", ""))
    }
]


BROKER_URL = "sqs://%s:%s@" % (
    environ.get("AWS_ACCESS_KEY_ID", ""),
    environ.get("AWS_SECRET_ACCESS_KEY", ""))


DEFAULT_FILE_STORAGE = 'sagebrew.s3utils.MediaRootS3BotoStorage'
STATICFILES_STORAGE = 'sagebrew.s3utils.StaticRootS3BotoStorage'

S3_URL = 'https://dr2ldscuzcleg.cloudfront.net/'
AWS_S3_CUSTOM_DOMAIN = "dr2ldscuzcleg.cloudfront.net"
CELERY_IGNORE_RESULT = True
STATIC_URL = "%s%s" % (S3_URL, "static/")
MEDIA_URL = "%s%s" % (S3_URL, "media/")

BROKER_TRANSPORT_OPTIONS = {'visibility_timeout': 43200,
                            'polling_interval': 15}

CELERY_DEFAULT_QUEUE = "%s-%s-celery" % (environ.get("APP_NAME", ""),
                                         environ.get("CIRCLE_BRANCH", ""))

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    ),
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
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d '
                      '%(thread)d %(message)s'
        },
    },
    'handlers': {
        'logentries_handler': {
            'token': LOGENT_TOKEN,
            'class': 'logentries.LogentriesHandler'
        },
        'console': {
            'class': 'logging.StreamHandler',
        }
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
