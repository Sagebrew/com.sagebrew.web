# Development settings for pscore project.
from base import *

DEBUG = True
TEMPLATE_DEBUG = DEBUG
ALLOWED_HOSTS = ['*']

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
        "USER": "",
        "PASSWORD": "",
        "HOST": "",
        "PORT": "",
    },
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

SECRET_KEY = 'ka)zzd@k7csfj+r#jm#gyu*q#xciu0hq=)@z#8^!ul5q3(j@#d'
INTERNAL_IPS = ('127.0.0.1', 'localhost', '0.0.0.0')

PYLINT_RCFILE = '%s/pylintconf/config.txt' % PROJECT_DIR

JENKINS_TASKS = (
    'django_jenkins.tasks.with_coverage',
    'django_jenkins.tasks.run_pylint',
    'django_jenkins.tasks.run_pep8',
    'django_jenkins.tasks.run_csslint',
)

INSTALLED_APPS = INSTALLED_APPS + ( 'django_jenkins', )
MIDDLEWARE_CLASSES = MIDDLEWARE_CLASSES + (
'debug_toolbar.middleware.DebugToolbarMiddleware',)
