from fnmatch import fnmatch

from base import *

DEBUG = True
TEMPLATE_DEBUG = DEBUG
ALLOWED_HOSTS = ['*']
WEB_ADDRESS = "https://192.168.56.101"
API_PASSWORD = "admin"
VERIFY_SECURE = False
MEDIA_ROOT = PROJECT_DIR.child("media")
STATIC_ROOT = PROJECT_DIR.child("static")
STATIC_URL = '/static/'
MEDIA_URL = '/media/'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'sagebrew_db',
        'USER': 'admin',
        'PASSWORD': 'admin',
        'HOST': '192.168.56.101',
        'PORT': '',
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '192.168.56.101:11211',
    }
}

CELERY_RESULT_BACKEND = 'redis://%s:%s/0' % (environ.get("REDIS_LOCATION", ""),
                                             environ.get("REDIS_PORT", ""))

EMAIL_VERIFICATION_URL = "%s/registration/email_confirmation/" % WEB_ADDRESS


BROKER_URL = 'amqp://%s:%s@%s:%s//' % (environ.get("QUEUE_USERNAME", ""),
                                       environ.get("QUEUE_PASSWORD", ""),
                                       environ.get("QUEUE_HOST", ""),
                                       environ.get("QUEUE_PORT", ""))

REST_FRAMEWORK = {
    'DEFAULT_MODEL_SERIALIZER_CLASS':
        'rest_framework.serializers.HyperlinkedModelSerializer',
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.OAuth2Authentication',
        'rest_framework.authentication.SessionAuthentication',
    )
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

ELASTIC_SEARCH_HOST = [{'host': environ.get("ELASTIC_SEARCH_HOST", "")
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
        'logentries_handler': {
            'token': LOGENT_TOKEN,
            'class': 'logentries.LogentriesHandler'
        },
    },
    'loggers': {
        'django.db': {
            'handlers': ['logging.handlers.SysLogHandler',
                         'logentries_handler'],
            'level': 'ERROR',
            'propagate': False,
        },
        'loggly_logs': {
            'handlers': ['logging.handlers.SysLogHandler',
                         'logentries_handler'],
            'propagate': True,
            'format': 'loggly: %(message)s',
            'level': 'DEBUG',
            'token': LOG_TOKEN
        },
        'elasticsearch': {
            'handlers': ['logging.handlers.SysLogHandler',
                         'logentries_handler'],
            'propagate': True,
            'format': 'loggly: %(message)s',
            'level': 'CRITICAL',
            'token': LOG_TOKEN
        },
        'elasticsearch.trace': {
            'handlers': ['logging.handlers.SysLogHandler',
                         'logentries_handler'],
            'propagate': True,
            'format': 'loggly: %(message)s',
            'level': 'CRITICAL',
            'token': LOG_TOKEN
        },
        'neomodel.properties': {
            'handlers': ['logging.handlers.SysLogHandler',
                         'logentries_handler'],
            'propagate': True,
            'format': 'loggly: %(message)s',
            'level': 'CRITICAL',
            'token': LOG_TOKEN
        },
        'django.request': {
            'handlers': ['logging.handlers.SysLogHandler',
                         'logentries_handler'],
            'level': 'ERROR',
            'propagate': False,
        },
    }
}