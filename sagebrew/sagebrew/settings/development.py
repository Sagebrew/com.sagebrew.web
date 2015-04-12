from fnmatch import fnmatch

from base import *

DEBUG = True
TEMPLATE_DEBUG = DEBUG
ALLOWED_HOSTS = ['*']
INTERNAL_IPS = ('192.168.56.1', '127.0.0.1', '192.168.56.101',
                '192.168.56.101:8080')
WEB_ADDRESS = "https://192.168.56.101"
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
CELERY_IGNORE_RESULT = False
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS':
        'rest_framework.pagination.PageNumberPagination',
    'PAGINATE_BY': 10,
    'PAGE_SIZE': 15,
    'MAX_PAGINATE_BY': 100,
    'PAGINATE_BY_PARAM': 'page_size',
    'EXCEPTION_HANDLER': 'sb_base.utils.custom_exception_handler',
    'DEFAULT_MODEL_SERIALIZER_CLASS':
        'rest_framework.serializers.HyperlinkedModelSerializer',
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
        'oauth2_provider.ext.rest_framework.OAuth2Authentication',
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