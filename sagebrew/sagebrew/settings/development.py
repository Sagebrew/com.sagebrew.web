import requests
from base import *

DEBUG = True
ALLOWED_HOSTS = ['*']
TEST_RUNNER = 'sagebrew.test_runner.SBTestRunner'

INTERNAL_IPS = ('192.168.56.1',
                '127.0.0.1',
                '192.168.56.101',
                '192.168.56.101:8080',
                'sagebrew.local.dev',
                '192.168.33.15', ''
                )

TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': (
        # Put strings here, like "/home/html/django_templates"
        # or "C:/www/django/templates".
        # Always use forward slashes, even on Windows.
        # Don't forget to use absolute paths, not relative paths.
        '%s/help_center/templates/' % PROJECT_DIR,
        '%s/plebs/templates/' % PROJECT_DIR,
        '%s/sagebrew/templates/' % PROJECT_DIR,
        '%s/sb_solutions/templates/' % PROJECT_DIR,
        '%s/sb_badges/templates/' % PROJECT_DIR,
        '%s/sb_quests/templates/' % PROJECT_DIR,
        '%s/sb_comments/templates/' % PROJECT_DIR,
        '%s/sb_council/templates' % PROJECT_DIR,
        '%s/sb_flag/templates/' % PROJECT_DIR,
        '%s/sb_notifications/templates/' % PROJECT_DIR,
        '%s/sb_posts/templates/' % PROJECT_DIR,
        '%s/sb_privileges/templates/' % PROJECT_DIR,
        '%s/sb_public_official/templates/' % PROJECT_DIR,
        '%s/sb_questions/templates/' % PROJECT_DIR,
        '%s/sb_registration/templates/' % PROJECT_DIR,
        '%s/sb_requirements/templates/' % PROJECT_DIR,
        '%s/sb_search/templates/' % PROJECT_DIR,
        '%s/sb_tags/templates/' % PROJECT_DIR,
        '%s/sb_uploads/templates/' % PROJECT_DIR
    ),
    'OPTIONS': {
        'loaders': [
            'django.template.loaders.filesystem.Loader',
            'django.template.loaders.app_directories.Loader',
        ],
        'context_processors': [
            "django.contrib.auth.context_processors.auth",
            "django.core.context_processors.request",
            "django.core.context_processors.debug",
            "django.core.context_processors.i18n",
            "django.core.context_processors.media",
            "django.core.context_processors.static",
            "django.core.context_processors.tz",
            "django.contrib.messages.context_processors.messages",
            "plebs.context_processors.request_profile",
            "sb_base.context_processors.js_settings",

        ],
        'allowed_include_roots': [HELP_DOCS_PATH, ]
    },
}]

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
STATIC_URL = 'https://sagebrew.local.dev/static/'
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
WEBHOSE_REQUEST_LIMIT = 25

BROKER_URL = 'amqp://%s:%s@%s:%s//' % (environ.get("QUEUE_USERNAME", ""),
                                       environ.get("QUEUE_PASSWORD", ""),
                                       environ.get("QUEUE_HOST", ""),
                                       environ.get("QUEUE_PORT", ""))
CELERY_IGNORE_RESULT = False


REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS':
        'sagebrew.pagination.StandardResultsSetPagination',
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
