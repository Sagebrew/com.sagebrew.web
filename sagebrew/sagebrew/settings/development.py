# Django settings for automated_test_client project.
from base import *
from fnmatch import fnmatch
DEBUG = True

TEMPLATE_DEBUG = DEBUG
ALLOWED_HOSTS = ['sagebrew.com']

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

AWS_UPLOAD_BUCKET_NAME = "sagebrew"
AWS_UPLOAD_CLIENT_KEY = ""
AWS_UPLOAD_CLIENT_SECRET_KEY = "lHu/"


SECRET_KEY = "5fd&2wkqx8r!h2y1)j!izqi!982$p87)sred(5#x0mtqa^cbx)"

INTERNAL_IPS = ('127.0.0.1', 'localhost', '0.0.0.0')

DEBUG_TOOLBAR_PANELS = (
    'debug_toolbar.panels.version.VersionDebugPanel',
    'debug_toolbar.panels.timer.TimerDebugPanel',
    'debug_toolbar.panels.settings_vars.SettingsVarsDebugPanel',
    'debug_toolbar.panels.headers.HeaderDebugPanel',
    # Commented out because it causes multiple saves/adds to occur
    #'debug_toolbar.panels.profiling.ProfilingDebugPanel',
    'debug_toolbar.panels.request_vars.RequestVarsDebugPanel',
    'debug_toolbar.panels.sql.SQLDebugPanel',
    'debug_toolbar.panels.template.TemplateDebugPanel',
    'debug_toolbar.panels.cache.CacheDebugPanel',
    'debug_toolbar.panels.signals.SignalDebugPanel',
    'debug_toolbar.panels.logger.LoggingPanel',
    #'cache_panel.panel.CacheDebugPanel',
)


def custom_show_toolbar(request):
    if(fnmatch(request.path.strip(), '/admin*')):
        return False
    elif(fnmatch(request.path.strip(), '/secret/*')):
        return False
    return True # Always show toolbar, for example purposes only.


DEBUG_TOOLBAR_CONFIG = {
    'INTERCEPT_REDIRECTS': False,
    'SHOW_TOOLBAR_CALLBACK': custom_show_toolbar,
    'EXTRA_SIGNALS': [],
    'HIDE_DJANGO_SQL': False,
    'TAG': 'div',
    'ENABLE_STACKTRACES': True,
}

INSTALLED_APPS = INSTALLED_APPS + ('debug_toolbar', )
MIDDLEWARE_CLASSES = MIDDLEWARE_CLASSES + ('debug_toolbar.middleware.DebugToolbarMiddleware',)