import requests
import socket
import os
from common import *

# DEBUG
# ------------------------------------------------------------------------------
DEBUG = True
TEMPLATES[0]['OPTIONS']['debug'] = DEBUG
ALLOWED_HOSTS = ['*']
CORS_ORIGIN_WHITELIST += ('localhost:4200', )
INTERNAL_IPS = ['192.168.56.1',
                '127.0.0.1',
                '192.168.56.101',
                '192.168.56.101:8080',
                '192.168.252.6:8000',
                'sagebrew.local.dev',
                '192.168.33.15',
                '10.0.2.2',
                ]

# tricks to have debug toolbar when developing with docker
if os.environ.get('USE_DOCKER') == 'yes':
    ip = socket.gethostbyname(socket.gethostname())
    INTERNAL_IPS += [ip[:-1] + "1"]

MIDDLEWARE += ('debug_toolbar.middleware.DebugToolbarMiddleware',)
INSTALLED_APPS += ('debug_toolbar', )

DEBUG_TOOLBAR_CONFIG = {
    'DISABLE_PANELS': [
        'debug_toolbar.panels.redirects.RedirectsPanel',
    ],
    'SHOW_TEMPLATE_CONTEXT': True,
}


WEB_ADDRESS = "https://sagebrew.local.dev"


# Mail settings
# ------------------------------------------------------------------------------
EMAIL_PORT = 1025
EMAIL_HOST = env("EMAIL_HOST", default='mailhog')


# CACHING
# ------------------------------------------------------------------------------
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': ''
    }
}

# SSL
# ------------------------------------------------------------------------------
# This is here because locally we do not have ssl certification.
# Please ensure you are never hardcoding False into the requests
# calls
VERIFY_SECURE = False
if not VERIFY_SECURE:
    from requests.packages.urllib3.exceptions import (InsecureRequestWarning,
                                                      InsecurePlatformWarning)

    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    requests.packages.urllib3.disable_warnings(InsecurePlatformWarning)

EMAIL_VERIFICATION_URL = "%s/registration/email_confirmation/" % WEB_ADDRESS
CELERY_IGNORE_RESULT = False


CORS_ALLOW_METHODS = (
    'GET',
    'POST',
    'PUT',
    'PATCH',
    'DELETE',
    'OPTIONS'
)

SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
