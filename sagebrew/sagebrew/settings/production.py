# Django settings for automated_test_client project.
from base import *
from os import environ

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

AWS_UPLOAD_BUCKET_NAME = "sagebrew"
AWS_UPLOAD_CLIENT_KEY = ""
AWS_UPLOAD_CLIENT_SECRET_KEY = ""


SECRET_KEY = "5fd&2wkqx8r!h2y1)j!izqi!982$p87)sred(5#x0mtqa^cbx)"