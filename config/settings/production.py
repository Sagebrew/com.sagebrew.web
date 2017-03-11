from django.utils import six
from common import *

DEBUG = env.bool('DJANGO_DEBUG', False)
ALLOWED_HOSTS = ['www.sagebrew.com', ]

VERIFY_SECURE = True
WEB_ADDRESS = "https://www.sagebrew.com"
WEBHOSE_REQUEST_LIMIT = 30
CELERY_IGNORE_RESULT = True

# Needed for APM management via Opbeat web interface https://opbeat.com
MIDDLEWARE = ('opbeat.contrib.django.middleware.OpbeatAPMMiddleware', ) + \
             MIDDLEWARE
INSTALLED_APPS += ('gunicorn', 'opbeat.contrib.django',)

# Ensure any opbeat logs get pumped to logging agent
LOGGING['loggers']['opbeat.errors'] = {
    'handlers': ['console'],
    'propagate': True,
    'format': '%(message)s',
    'level': 'CRITICAL',
}

BROKER_TRANSPORT_OPTIONS = {'visibility_timeout': 43200}


EMAIL_VERIFICATION_URL = "%s/registration/email_confirmation/" % WEB_ADDRESS


# TEMPLATE CONFIGURATION
# ------------------------------------------------------------------------------
# See:
# https://docs.djangoproject.com/en/dev/ref/templates/api/#django.template.loaders.cached.Loader
TEMPLATES[0]['OPTIONS']['loaders'] = [
    ('django.template.loaders.cached.Loader', [
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader', ]),
]
TEMPLATES[0]['OPTIONS']['debug'] = DEBUG


# STORAGE CONFIGURATION
# ------------------------------------------------------------------------------

# Use Whitenoise to serve static files
# See: https://whitenoise.readthedocs.io/
WHITENOISE_MIDDLEWARE = ('whitenoise.middleware.WhiteNoiseMiddleware', )
MIDDLEWARE = WHITENOISE_MIDDLEWARE + MIDDLEWARE


# Uploaded Media Files
# ------------------------
# See: http://django-storages.readthedocs.io/en/latest/index.html
INSTALLED_APPS += (
    'storages',
)

DEFAULT_FILE_STORAGE = 'sagebrew.s3utils.MediaRootS3BotoStorage'
STATICFILES_STORAGE = 'sagebrew.s3utils.StaticRootS3BotoStorage'

S3_URL = 'https://dr2ldscuzcleg.cloudfront.net/'
AWS_S3_CUSTOM_DOMAIN = "dr2ldscuzcleg.cloudfront.net"
STATIC_URL = "%s%s" % (S3_URL, "static/")
MEDIA_URL = "%s%s" % (S3_URL, "media/")


# Opbeat APM Configuration - Used for All Applications, requires you to setup
# initial configuration at opbeat.com under ESG-Automotive Organization for a
# new application. It should be named the same as the repo. Ask your manager
# to grant you access to the org if you need it.
OPBEAT = {
    'ORGANIZATION_ID': env('OPBEAT_ORG_ID', default=''),
    'APP_ID': env('OPBEAT_APP_ID', default=''),
    'SECRET_TOKEN': env('OPBEAT_SECRET_TOKEN', default=''),
}

ELASTIC_SEARCH_HOST = [
    {
        'host': env.get("ELASTIC_SEARCH_HOST", default=''),
        'port': env.get("ELASTIC_SEARCH_PORT", default=''),
        'use_ssl': True,
        'http_auth': (env.get("ELASTIC_SEARCH_USER", default=''),
                      env.get("ELASTIC_SEARCH_KEY", default=''))
    }
]


# URL that handles the media served from MEDIA_ROOT, used for managing
# stored files.

#  See:http://stackoverflow.com/questions/10390244/
#
#from storages.backends.s3boto import S3BotoStorage
#StaticRootS3BotoStorage = lambda: S3BotoStorage(location='static')
#MediaRootS3BotoStorage = lambda: S3BotoStorage(location='media')
#DEFAULT_FILE_STORAGE = 'config.settings.production.MediaRootS3BotoStorage'
#MEDIA_URL = 'https://s3.amazonaws.com/%s/media/' % AWS_STORAGE_BUCKET_NAME

# Static Assets
# ------------------------
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
#STATIC_HOST = 'https://d4663kmspf1sqa.cloudfront.net' if not DEBUG else ''
#STATIC_URL = STATIC_HOST + '/static/'

# EMAIL
# ------------------------------------------------------------------------------
