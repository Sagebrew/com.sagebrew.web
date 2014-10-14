# Django settings for automated_test_client project.
from fnmatch import fnmatch

from base import *


DEBUG = True

TEMPLATE_DEBUG = DEBUG
ALLOWED_HOSTS = ['*']

WEB_ADDRESS = "https://192.168.56.101"

API_PASSWORD = "admin"

VERIFY_SECURE = False
'''
# TODO this makes it so we cannot run tests concurrently (parallel processing in
# circle. This is because the test db gets created on this server and then
# if another one starts running it fails. Might want to look into making a
# separate test config again that uses a local psql db based on circles docs.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'sagebrewdb',
        'USER': 'sagedev',
        'PASSWORD': 'thisisthesagebrewpassword',
        'HOST': 'sagebrewdb.clkvngd3diph.us-west-2.rds.amazonaws.com',
        'PORT': '5432',
    }
}
'''
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'sagebrew_db',
        'USER': 'admin',
        'PASSWORD': 'admin',
        'HOST': 'localhost',
        'PORT': '',
    }
}


CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
    }
}

AWS_BUCKET_NAME = "sagebrew"
AWS_ACCESS_KEY_ID = "AKIAJIWX3E2JPTBS6CRA"
AWS_SECRET_ACCESS_KEY = "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"
AWS_PROFILE_PICTURE_FOLDER_NAME = 'profile_pictures'

SECRET_KEY = "5fd&2wkqx8r!h2y1)j!izqi!982$p87)sred(5#x0mtqa^cbx)"

INTERNAL_IPS = ('127.0.0.1', 'localhost', '0.0.0.0', '192.168.56.101',
                '192.168.56.102')

REST_FRAMEWORK = {
    # Use hyperlinked styles by default.
    # Only used if the `serializer_class` attribute is not set on a view.
    'DEFAULT_MODEL_SERIALIZER_CLASS':
        'rest_framework.serializers.HyperlinkedModelSerializer',
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.OAuth2Authentication',
        'rest_framework.authentication.SessionAuthentication',
    )
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
}

DEBUG_TOOLBAR_PANELS = (
    'debug_toolbar.panels.version.VersionDebugPanel',
    'debug_toolbar.panels.timer.TimerDebugPanel',
    'debug_toolbar.panels.settings_vars.SettingsVarsDebugPanel',
    'debug_toolbar.panels.headers.HeaderDebugPanel',
    # Commented out because it causes multiple saves/adds to occur
    # 'debug_toolbar.panels.profiling.ProfilingDebugPanel',
    'debug_toolbar.panels.request_vars.RequestVarsDebugPanel',
    'debug_toolbar.panels.sql.SQLDebugPanel',
    'debug_toolbar.panels.template.TemplateDebugPanel',
    'debug_toolbar.panels.cache.CacheDebugPanel',
    'debug_toolbar.panels.signals.SignalDebugPanel',
    'debug_toolbar.panels.logger.LoggingPanel',
    # 'cache_panel.panel.CacheDebugPanel',
)

ELASTIC_SEARCH_HOST = [{'host': 'dwalin-us-east-1.searchly.com',
                        'port':443, 'use_ssl': True,
                        'http_auth': ('site',
                                      '6495ff8387e86cb755da1f45da88b475')
                       }]


def custom_show_toolbar(request):
    if (fnmatch(request.path.strip(), '/admin*')):
        return False
    elif (fnmatch(request.path.strip(), '/secret/*')):
        return False
    return True  # Always show toolbar, for example purposes only.


DEBUG_TOOLBAR_CONFIG = {
    'INTERCEPT_REDIRECTS': False,
    'SHOW_TOOLBAR_CALLBACK': custom_show_toolbar,
    'EXTRA_SIGNALS': [],
    'HIDE_DJANGO_SQL': False,
    'TAG': 'div',
    'ENABLE_STACKTRACES': True,
}

#INSTALLED_APPS = INSTALLED_APPS + ('debug_toolbar', )
# MIDDLEWARE_CLASSES = MIDDLEWARE_CLASSES + (
# 'debug_toolbar.middleware.DebugToolbarMiddleware',)

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
        'loggly_logs': {
            'handlers': ['logging.handlers.SysLogHandler'],
            'propagate': True,
            'format': 'loggly: %(message)s',
            'level': 'DEBUG',
            'token': LOG_TOKEN
        },
        'elasticsearch': {
            'handlers': ['logging.handlers.SysLogHandler'],
            'propagate': True,
            'format': 'loggly: %(message)s',
            'level': 'DEBUG',
            'token': LOG_TOKEN
        },
        'django.request': {
            'handlers': ['logging.handlers.SysLogHandler'],
            'level': 'ERROR',
            'propagate': False,
        },
    }
}