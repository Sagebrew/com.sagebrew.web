# Django settings for automated_test_client project.
from base import *

DEBUG = True
TEMPLATE_DEBUG = DEBUG
ALLOWED_HOSTS = ['sagebrew.com']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'sagebrew_prod_db',
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

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.solr_backend.SolrEngine',
        'URL': 'http://127.0.0.1:8983/solr'
    },
}

AWS_UPLOAD_BUCKET_NAME = "sagebrew"
AWS_UPLOAD_CLIENT_KEY = ""
AWS_UPLOAD_CLIENT_SECRET_KEY = ""

SECRET_KEY = "5fd&2wkqx8r!h2y1)j!izqi!982$p87)sred(5#x0mtqa^cbx)"

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
            'level': 'ERROR',
            'token': LOGGLY_TOKEN
        },
        'django.request': {
            'handlers': ['logging.handlers.SysLogHandler'],
            'level': 'ERROR',
            'propagate': False,
        },
    }
}