#!/usr/bin/env python
# -*- coding: utf-8 -*-
# coding=utf-8
from __future__ import absolute_import
import environ
import re
from celery.schedules import crontab
from os import path, makedirs
from datetime import datetime

# LOCATION VARS
# ------------------------------------------------------------------------------
# (project_name/config/settings/common.py - 3 = project_name/)
ROOT_DIR = environ.Path(__file__) - 3
APPS_DIR = ROOT_DIR.path('sagebrew')

env = environ.Env()
env.read_env()

# APP CONFIGURATION
# ------------------------------------------------------------------------------
DJANGO_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.sitemaps',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',

)

THIRD_PARTY_APPS = (
    'django_extensions',
    'corsheaders',
    'revproxy',
    'localflavor',
    'rest_framework',
    'rest_framework.authtoken',
    'oauth2_provider',
    'rest_framework_jwt',
    'rest_framework_auth0',
    'dry_rest_permissions',
    'rest_framework_docs',
    'annoying',
    'clear_cache',
    'googleplaces',
    "amazon",
    'elasticsearch',
    'django_neomodel'
)

ADMIN_APPS = (
    'material',
    'material.admin',
    'django.contrib.admin',
)

LOCAL_APPS = (
    'sagebrew.plebs',
    'sagebrew.api',
    'sagebrew.govtrack',
    'sagebrew.sb_solutions',
    'sagebrew.sb_accounting',
    'sagebrew.sb_address',
    'sagebrew.sb_badges',
    'sagebrew.sb_base',
    'sagebrew.sb_comments',
    'sagebrew.sb_contributions',
    'sagebrew.sb_council',
    'sagebrew.sb_docstore',
    'sagebrew.sb_donations',
    'sagebrew.sb_flags',
    'sagebrew.sb_gifts',
    'sagebrew.sb_locations',
    'sagebrew.sb_missions',
    'sagebrew.sb_news',
    'sagebrew.sb_notifications',
    'sagebrew.sb_orders',
    'sagebrew.sb_posts',
    'sagebrew.sb_privileges',
    'sagebrew.sb_public_official',
    'sagebrew.sb_questions',
    'sagebrew.sb_quests',
    'sagebrew.sb_registration',
    'sagebrew.sb_requirements',
    'sagebrew.sb_search',
    'sagebrew.sb_stats',
    'sagebrew.sb_tags',
    'sagebrew.sb_uploads',
    'sagebrew.sb_updates',
    'sagebrew.sb_volunteers',
    'sagebrew.sb_votes',
    'sagebrew.sb_wall',
    'sagebrew.sb_oauth',
    'sagebrew.help_center'
)

INSTALLED_APPS = DJANGO_APPS + ADMIN_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# MIDDLEWARE CONFIGURATION
# ------------------------------------------------------------------------------
MIDDLEWARE = (
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'crum.CurrentRequestUserMiddleware',
    'oauth2_provider.middleware.OAuth2TokenMiddleware',
)

# DATABASE CONFIGURATION
# ------------------------------------------------------------------------------
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': env("DATABASE_NAME",  default=""),
        'USER': env("DATABASE_USER",  default=""),
        'PASSWORD': env("DATABASE_PASSWORD",  default=""),
        'HOST': env("DATABASE_HOST",  default=""),
        'PORT': 5432,
    }
}

NEOMODEL_NEO4J_BOLT_URL = env(
    'NEO4J_BOLT_URL',  default='bolt://neo4j:password@neo4j_db:7687')

# Cache
# ------------------------------------------------------------------------------
REDIS_LOCATION = '{0}/{1}'.format(env('REDIS_URL',
                                      default='redis://127.0.0.1:6379'), 0)
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': REDIS_LOCATION,
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'IGNORE_EXCEPTIONS': True,  # mimics memcache behavior.
                                        # http://niwenz.github.io/django-redis/latest/#_memcached_exceptions_behavior
        }
    }
}

# MANAGER CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#admins
ADMINS = (
    ('Devon Bleibtrey', 'devon@sagebrew.com'),
    ('Tyler Wiersing', 'tyler@sagebrew.com')
)

# See: https://docs.djangoproject.com/en/dev/ref/settings/#managers
MANAGERS = ADMINS

# STATIC FILE CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#static-root
STATIC_ROOT = str(ROOT_DIR('staticfiles'))

# See: https://docs.djangoproject.com/en/dev/ref/settings/#static-url
STATIC_URL = '/static/'

# See: https://docs.djangoproject.com/en/dev/ref/
# contrib/staticfiles/#std:setting-STATICFILES_DIRS
STATICFILES_DIRS = (
    str(APPS_DIR.path('static')),
    str(ROOT_DIR.path('frontend/build')),
)
# See: https://docs.djangoproject.com/en/dev/ref/
# contrib/staticfiles/#staticfiles-finders
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

# MEDIA CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#media-root
MEDIA_ROOT = str(APPS_DIR('media'))

# See: https://docs.djangoproject.com/en/dev/ref/settings/#media-url
MEDIA_URL = '/media/'

# URL Configuration
# ------------------------------------------------------------------------------
ROOT_URLCONF = 'config.urls'

# See: https://docs.djangoproject.com/en/dev/ref/settings/#wsgi-application
WSGI_APPLICATION = 'config.wsgi.application'


DEBUG = True

AWS_ACCESS_ID = env("AWS_ACCESSID", default='')
AWS_SECRET_KEY = env("AWS_SECRETKEY", default='')

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'UTC'

# See: https://docs.djangoproject.com/en/dev/ref/settings/#language-code
LANGUAGE_CODE = 'en-us'

# See: https://docs.djangoproject.com/en/dev/ref/settings/#site-id
SITE_ID = 1

# See: https://docs.djangoproject.com/en/dev/ref/settings/#use-i18n
USE_I18N = True

# See: https://docs.djangoproject.com/en/dev/ref/settings/#use-l10n
USE_L10N = True

# See: https://docs.djangoproject.com/en/dev/ref/settings/#use-tz
USE_TZ = True
HELP_DOCS_PATH = "%s/help_center/rendered_docs/" % APPS_DIR
# TEMPLATE CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#templates
TEMPLATES = [
    {
        # See: https://docs.djangoproject.com/en/dev/ref/
        # settings/#std:setting-TEMPLATES-BACKEND
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # See: https://docs.djangoproject.com/en/dev/ref/settings/#template-dirs
        'DIRS': [
            str(APPS_DIR.path('templates'))
        ],
        'OPTIONS': {
            # See: https://docs.djangoproject.com/en/dev/ref/
            # settings/#template-debug
            'debug': DEBUG,
            # See: https://docs.djangoproject.com/en/dev/ref/
            # settings/#template-loaders
            # https://docs.djangoproject.com/en/dev/ref/templates/api/#loader-types
            'loaders': [
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
            ],
            # See: https://docs.djangoproject.com/en/dev/ref/
            # settings/#template-context-processors
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
                "sagebrew.plebs.context_processors.request_profile",
                "sagebrew.sb_base.context_processors.js_settings",
            ]
        },
    },
]

# CELERY
# ------------------------------------------------------------------------------
INSTALLED_APPS += ('sagebrew.tasks.celery.CeleryConfig',)
BROKER_URL = '{0}/{1}'.format(env(
    'REDIS_URL', default='redis://127.0.0.1:6379'), 1)
CELERY_RESULT_BACKEND = '{0}/{1}'.format(
    env('REDIS_URL', default='redis://127.0.0.1:6379'), 1)
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'America/Detroit'
CELERY_DISABLE_RATE_LIMITS = True
CELERY_ACCEPT_CONTENT = ['pickle', 'application/json']
CELERY_ALWAYS_EAGER = False
TEST_RUNNER = 'django.test.runner.DiscoverRunner'
EMAIL_VERIFICATION_TIMEOUT_DAYS = 1
SERVER_EMAIL = "support@sagebrew.com"
DEFAULT_FROM_EMAIL = "support@sagebrew.com"
OAUTH2_PROVIDER_APPLICATION_MODEL = 'sb_oauth.SBApplication'
OAUTH2_PROVIDER = {
    'APPLICATION_MODEL': 'sb_oauth.SBApplication',
}
LOGIN_REDIRECT_URL = '/registration/profile_information/'
LOGIN_URL = '/login/'
LOGOUT_URL = '/logout/'
ANONYMOUS_USER_ID = -1
EMAIL_USE_TLS = True

# CSRF_COOKIE_HTTPONLY = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
ADMIN_HONEYPOT_EMAIL_ADMINS = False
SECURE_FRAME_DENY = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
APPEND_SLASH = True
SECRET_KEY = env("APPLICATION_SECRET_KEY", default="DcRVjf7vxkya952j9wO5")

# API CONFIGURATION
# ------------------------------------------------------------------------------
REST_FRAMEWORK = {
    #    'DEFAULT_RENDERER_CLASSES': (
    #        'rest_framework.renderers.JSONRenderer',
    #    ),
    'DEFAULT_PAGINATION_CLASS':
        'config.pagination.StandardResultsSetPagination',
    'EXCEPTION_HANDLER': 'sagebrew.sb_base.utils.custom_exception_handler',
    'DEFAULT_MODEL_SERIALIZER_CLASS':
        'rest_framework.serializers.HyperlinkedModelSerializer',
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
        'oauth2_provider.ext.rest_framework.OAuth2Authentication',
    ),
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.BrowsableAPIRenderer',
    ),
}


JSON_API_FORMAT_KEYS = 'dasherize'
JSON_API_FILTER_KEYWORD = 'filter\[(?P<field>\w+)\]'

CORS_ORIGIN_WHITELIST = (
    'sagebrew.com',
    'www.sagebrew.com',
    'staging.sagebrew.com'
)

CORS_ALLOW_METHODS = (
    'GET',
    'POST',
    'PUT',
    'PATCH',
    'DELETE',
    'OPTIONS'
)

AUTH0_API_TOKEN = env("AUTH0_API_TOKEN", default="")
AUTH0_API_DOMAIN = env("AUTH0_API_DOMAIN", default="mvcs.auth0.com")

AUTH0 = {
    'AUTH0_CLIENT_ID': env("AUTH0_CLIENT_ID", default=""),
    'AUTH0_CLIENT_SECRET': env("AUTH0_CLIENT_SECRET", default=""),
    'AUTH0_ALGORITHM': 'HS256',
    'JWT_AUTH_HEADER_PREFIX': 'Bearer',
    'AUTHORIZATION_EXTENSION': False,
    'CLIENT_SECRET_BASE64_ENCODED': False,
    'USERNAME_FIELD': 'sub',
}

if not DEBUG:
    CELERYBEAT_SCHEDULE = {
        'check-closed-reputation-changes': {
            'task': 'sagebrew.sb_council.tasks.'
                    'check_closed_reputation_changes_task',
            'schedule': crontab(minute=0, hour=6),
            'args': ()
        },
        'find-tag-news': {
            'task': 'sagebrew.sb_news.tasks.find_tag_news',
            'schedule': crontab(minute=0, hour=6),
            'args': ()
        },
        'check-unverified-quests': {
            'task': 'sagebrew.sb_accounting.tasks.check_unverified_quest',
            'schedule': crontab(minute=0, hour=3),
            'args': ()
        }
    }


# AWS_S3_SECURE_URLS = True
AWS_STORAGE_BUCKET_NAME = env("AWS_S3_BUCKET", default="")

AWS_ACCESS_KEY_ID = env("AWS_ACCESS_KEY_ID", default="")
AWS_SECRET_ACCESS_KEY = env("AWS_SECRET_ACCESS_KEY", default="")
AWS_PROFILE_PICTURE_FOLDER_NAME = 'profile_pictures'
AWS_UPLOAD_IMAGE_FOLDER_NAME = 'media'
LOGENT_TOKEN = env("LOGENT_TOKEN", default="")
ALCHEMY_API_KEY = env("ALCHEMY_API_KEY", default="")
# Used for server side
ADDRESS_VALIDATION_ID = env("ADDRESS_VALIDATION_ID", default="")
ADDRESS_VALIDATION_TOKEN = env("ADDRESS_VALIDATION_TOKEN", default="")
# Used for JS
ADDRESS_AUTH_ID = env("ADDRESS_AUTH_ID", default="")
# Intercom
INTERCOM_API_KEY = env("INTERCOM_API_KEY", default="")
INTERCOM_APP_ID = env("INTERCOM_APP_ID", default="")
INTERCOM_ADMIN_ID_DEVON = env("INTERCOM_ADMIN_ID_DEVON", default="")
INTERCOM_USER_ID_DEVON = "devon_bleibtrey"
LONG_TERM_STATIC_DOMAIN = "https://d2m0mj9tyf6rjw.cloudfront.net"
WEBHOSE_KEY = env("WEBHOSE_KEY", default="")
WEBHOSE_FREE = True
EMBEDLY_KEY = env("EMBEDLY_KEY", default='808adeb9c5da4db7a4eb359c242cdada')
STRIPE_PUBLIC_KEY = env("STRIPE_PUBLIC_KEY", default="")
STRIPE_SECRET_KEY = env("STRIPE_SECRET_KEY", default="")
STRIPE_TRANSACTION_PERCENT = .029
STRIPE_PAID_ACCOUNT_FEE = .021
STRIPE_FREE_ACCOUNT_FEE = .021
STRIPE_API_VERSION = '2016-03-07'
MASKED_NAME = env("MASKED_NAME", default="")
OAUTH_CLIENT_ID = env("OAUTH_CLIENT_ID", default="")
OAUTH_CLIENT_SECRET = env("OAUTH_CLIENT_SECRET", default="")
OAUTH_CLIENT_ID_CRED = env("OAUTH_CLIENT_ID_CRED", default="")
OAUTH_CLIENT_SECRET_CRED = env("OAUTH_CLIENT_SECRET_CRED", default="")
OAUTH_CLIENT_ID_CRED_PUBLIC = env(
    "OAUTH_CLIENT_ID_CRED_PUBLIC", default="")
OAUTH_CLIENT_SECRET_CRED_PUBLIC = env(
    "OAUTH_CLIENT_SECRET_CRED_PUBLIC", default="")
GOOGLE_MAPS_API_SERVER = env(
    "GOOGLE_MAPS_API", default="AIzaSyA0oDFTNqlan-vNsGvJv9HckKoMqlV5Nqo")
DYNAMO_IP = env("DYNAMO_IP", default=None)

AMAZON_PROMOTION_API_KEY = env("AMAZON_PROMOTION_API_KEY", default="")
AMAZON_PROMOTION_API_SECRET_KEY = env(
    "AMAZON_PROMOTION_API_SECRET_KEY", default="")
AMAZON_ASSOCIATE_TAG = env("AMAZON_ASSOCIATE_TAG", default="")

EMAIL_BACKEND = 'django_ses.SESBackend'


# LOGGING CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#logging
# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'loggly': {
            'format': 'loggly: %(message)s',
        },
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d '
                      '%(thread)d %(message)s'
        },
    },
    'handlers': {
        'logentries_handler': {
            'token': LOGENT_TOKEN,
            'class': 'logentries.LogentriesHandler'
        },
        'console': {
            'class': 'logging.StreamHandler',
        }
    },
    'loggers': {
        'django.db': {
            'handlers': ['logentries_handler'],
            'level': 'ERROR',
            'propagate': False,
        },
        'elasticsearch': {
            'handlers': ['logentries_handler'],
            'propagate': True,
            'format': 'loggly: %(message)s',
            'level': 'CRITICAL',
        },
        'loggly_logs': {
            'handlers': ['logentries_handler'],
            'propagate': True,
            'format': 'loggly: %(message)s',
            'level': 'ERROR',
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
        'django.request': {
            'handlers': ['logentries_handler'],
            'level': 'ERROR',
            'propagate': False,
        },
    }
}

CSV_FILES = '%s/csv_content/' % APPS_DIR
YAML_FILES = '%s/yaml_content/' % APPS_DIR

TEMP_FILES = '%s/temp_files/' % APPS_DIR
if not path.exists(TEMP_FILES):
    makedirs(TEMP_FILES)

USER_RELATIONSHIP_BASE = {
    'seen': 150, 'blocked_user': 0, 'friend_of_friend': 100,
    'friend_requested': 200, 'extended_family': 300,
    'friends': 500, 'congressman': 750, 'admin': 750, 'senators': 850,
    'sage': 850, 'tribune': 850, 'close_friends': 1000,
    'significant_other': 1200, 'president': 1500
}

USER_RELATIONSHIP_MODIFIER = {
    'page_seen': 25, 'friend_request_denied': -25, 'state': 10,
    'county': 20, 'district': 50, 'city': 100, 'constituents': 50,
    'search_seen': 10
}

OBJECT_RELATIONSHIP_BASE = {
    'seen': 20
}


OBJECT_SEARCH_MODIFIERS = {
    'post': 10, 'comment_on': 5, 'upvote': 3, 'downvote': -3,
    'time': -1, 'proximity_to_you': 10, 'proximity_to_interest': 10,
    'share': 7, 'flag_as_inappropriate': -5, 'flag_as_spam': -100,
    'flag_as_other': -10, 'solution': 50, 'starred': 150, 'seen_search': 5,
    'seen_page': 20
}

BASE_TAGS = ["fiscal", "foreign_policy", "social", "education", "science",
             "environment", "drugs", "agriculture", "defense", "energy",
             "health", "space"]

PAYMENT_PLANS = [
    ("free", "Free"),
    ("sub", "Subscription")
]

SEARCH_TYPES = [
    ("general", "general"),
    ("conversations", "question"),
    ("people", "profile"),
    ("quests", ["campaign", "politicalcampaign", "quest"]),
    ("missions", "mission")
]

SEARCH_FIELDS = [
    "username", "first_name", "last_name", "content", "title", "tags",
    "full_name", "owner_username", "focused_on"
]


BASE_REP_TYPES = [
    ("f2729db2-9da8-11e4-9233-080027242395",
     "sagebrew.sb_public_official.neo_models.USSenator"),
    ("f3aeebe0-9da8-11e4-9233-080027242395",
     "sagebrew.sb_public_official.neo_models.USPresident"),
    ("f46fbcda-9da8-11e4-9233-080027242395",
     "sagebrew.sb_public_official.neo_models.PublicOfficial"),
    ("628c138a-9da9-11e4-9233-080027242395",
     "sagebrew.sb_public_official.neo_models.USHouseRepresentative"),
    ("786dcf40-9da9-11e4-9233-080027242395",
     "sagebrew.sb_public_official.neo_models.Governor")
]

OPERATOR_TYPES = [
    ('coperator\neq\np0\n.', '='),
    ('coperator\nle\np0\n.', '<='),
    ('coperator\ngt\np0\n.', '>'),
    ('coperator\nne\np0\n.', '!='),
    ('coperator\nlt\np0\n.', '<'),
    ('coperator\nge\np0\n.', '>='),
    ('coperator\nnot_\np0\n.', 'not'),
    ('coperator\nis_not\np0\n.', 'is_not'),
    ('coperator\nis_\np0\n.', 'is'),
    ('coperator\ntruth\np0\n.', 'truth')
]

ALLOWED_IMAGE_FORMATS = ['gif', 'jpeg', 'jpg', 'png', 'GIF', 'JPEG', 'JPG',
                         'PNG']

ALLOWED_IMAGE_SIZE = 20000000  # 20 MB

NON_SAFE = ["REMOVE", "DELETE", "CREATE", "SET",
            "FOREACH", "MERGE", "MATCH", "START"]

REMOVE_CLASSES = ["SBVersioned", "SBPublicContent", "SBPrivateContent",
                  "VotableContent", "NotificationCapable", "TaggableContent",
                  "SBContent", "Searchable", "Term", "TitledContent",
                  "SBObject"]

QUERY_OPERATIONS = {
    "eq": "=",
    "le": "<=",
    "lt": "<",
    "ge": ">=",
    "gt": ">",
}

STRIPE_FIELDS_NEEDED = {
    "external_account": "Bank Account",
    "legal_entity.address.city": "City",
    "legal_entity.address.line1": "Street Address",
    "legal_entity.address.postal_code": "ZIP Code",
    "legal_entity.address.state": "State",
    "legal_entity.business_name": "Name of Entity Managing Bank Account",
    "legal_entity.business_tax_id": "EIN of Managing Bank Account",
    "legal_entity.dob.day": "Birth Day",
    "legal_entity.dob.month": "Birth Month",
    "legal_entity.dob.year": "Birth Year",
    "legal_entity.first_name": "First Name",
    "legal_entity.last_name": "Last Name",
    "legal_entity.personal_id_number": "SSN",
    "legal_entity.ssn_last_4": "Last 4 Digits of SSN",
    "legal_entity.type": "Type (Individual or Company)",
    "tos_acceptance.date": "Terms of Service Acceptance Date",
    "tos_acceptance.ip": "Terms of Service Acceptance IP",
    "legal_entity.verification.document": "Verification Document"
}

FREE_MISSIONS = 5

OPERATOR_DICT = {
    'coperator\neq\np0\n.': 'equal to',
    'coperator\nle\np0\n.': 'at most',
    'coperator\ngt\np0\n.': 'more than',
    'coperator\nne\np0\n.': 'not have',
    'coperator\nlt\np0\n.': 'less than',
    'coperator\nge\np0\n.': 'at least',
    'coperator\nnot_\np0\n.': 'not',
    'coperator\nis_not\np0\n.': 'is not',
    'coperator\nis_\np0\n.': 'is',
    'coperator\ntruth\np0\n.': 'truth'
}

SUNLIGHT_FOUNDATION_KEY = env("SUNLIGHT_FOUNDATION_KEY")
OPENSTATES_DISTRICT_SEARCH_URL = "http://openstates.org/api/v1/legislators/" \
                                 "geo/?lat=%f&long=%f"
PRO_QUEST_PROMOTION = True
PRO_QUEST_END_DATE = datetime(2016, 11, 9)
PROMOTION_KEYS = ["8UN96FNPP8ntv8JeaOyP", ]

CORS_ORIGIN_ALLOW_ALL = True
DEFAULT_WALLPAPER = 'images/wallpaper_capitol_2.jpg'
REVIEW_FEEDBACK_OPTIONS = [
    ('too_short', "Add additional content to your Epic. There isn't enough "
                  "information for donors to understand what their donations "
                  "will be going towards."),
    ('no_action_items', "Add actionable tasks that you can accomplish "
                        "so you can showcase progress to contributors."),
    ('malicious', "Remove malicious content"),
    ('porn', "Remove pornography")
]
# Titles for onboarding since they must be indexes and they are used in
# multiple locations to determine what to set to completed.
# If we change these we'll need to run a query to update all the existing
# onboarding tasks with that title.
MISSION_ABOUT_TITLE = "Mission About"
QUEST_WALLPAPER_TITLE = "Quest Wallpaper"
BANK_SETUP_TITLE = "Banking Setup"
QUEST_ABOUT_TITLE = "Quest About"
MISSION_SETUP_TITLE = "Mission Setup"
EPIC_TITLE = "Create Epic"
MISSION_WALLPAPER_TITLE = "Mission Wallpaper"
SUBMIT_FOR_REVIEW = "Submit For Review"
SHARE_ON_FACEBOOK = "Share on Facebook"
SHARE_ON_TWITTER = "Share on Twitter"
ONBOARDING_TASKS = [
    {
        "title": MISSION_SETUP_TITLE,
        "completed_title": "Mission Created",
        "content": "Define your mission's level, name, and location.",
        "icon": "fa fa-check-circle",
        "priority": 1,
        "url": "%s/missions/%s/%s/manage/general/",
        'type': 'mission',
        'completed': True
    },
    {
        "title": BANK_SETUP_TITLE,
        "completed_title": "Bank Confirmed",
        "content": "Allow contributors to donate to you.",
        "icon": "fa fa-university",
        "priority": 2,
        "url": "%s/quests/%s/manage/banking/#bank",
        'type': 'quest'
    },
    {
        "title": EPIC_TITLE,
        "completed_title": "Epic Published",
        "content": "Share your platform, goals, and mission with the world.",
        "icon": "fa fa-font",
        "priority": 3,
        "url": "%s/missions/%s/%s/manage/epic/edit/",
        'type': 'mission'
    },
    {
        "title": SUBMIT_FOR_REVIEW,
        "completed_title": "Submitted For Review",
        "content": "Take the final step needed to share your mission "
                   "with the world.",
        "icon": "fa fa-star",
        "priority": 4,
        "url": "%s/missions/%s/%s/",
        'type': 'mission'
    },
    {
        "title": SHARE_ON_FACEBOOK,
        "completed_title": "Shared on Facebook",
        "content": "Get the word out about your Mission by sharing it "
                   "on Facebook",
        "icon": "fa fa-facebook",
        "priority": 5,
        "url": "%s/missions/%s/%s/manage/general/",
        'type': 'mission'
    },
    {
        "title": SHARE_ON_TWITTER,
        "completed_title": "Shared on Twitter",
        "content": "Get the word out about your Mission by sharing it "
                   "on Twitter",
        "icon": "fa fa-twitter",
        "priority": 6,
        "url": "%s/missions/%s/%s/manage/general/",
        'type': 'mission'
    },
    {
        "title": MISSION_WALLPAPER_TITLE,
        "completed_title": "Mission Wallpaper Set",
        "content": "Replace the default image "
                   "with one that reflects your Mission.",
        "icon": "fa fa-picture-o",
        "priority": 7,
        "url": "%s/missions/%s/%s/manage/general/#wallpaper",
        'type': 'mission'
    },
    {
        "title": MISSION_ABOUT_TITLE,
        "completed_title": "Summary Created",
        "content": "Attract users at a glance by summarizing your Mission",
        "icon": "fa fa-font",
        "priority": 8,
        "url": "%s/missions/%s/%s/manage/general/#about",
        'type': 'mission'
    },
    {
        "title": QUEST_WALLPAPER_TITLE,
        "completed_title": "Quest Wallpaper Set",
        "content": "Replace the default image with one "
                   "that reflects yourself or your organization.",
        "icon": "fa fa-picture-o",
        "priority": 9,
        "url": "%s/quests/%s/manage/general/#wallpaper",
        'type': 'quest'
    },
    {
        "title": QUEST_ABOUT_TITLE,
        "completed_title": "Quest Summarized",
        "content": "Build contributor confidence by describing yourself "
                   "or your organization.",
        "icon": "fa fa-font",
        "priority": 10,
        "url": "%s/quests/%s/manage/general/#about",
        'type': 'quest'
    }
]

VOLUNTEER_ACTIVITIES = [
    ("get_out_the_vote", "Get Out The Vote"),
    ("assist_with_an_event", "Assist With An Event"),
    ("leaflet_voters", "Leaflet Voters"),
    ("write_letters_to_the_editor", "Write Letters To The Editor"),
    ("work_in_a_campaign_office", "Work In A Campaign Office"),
    ("table_at_events", "Table At Events"),
    ("call_voters", "Call Voters"),
    ("data_entry", "Data Entry"),
    ("host_a_meeting", "Host A Meeting"),
    ("host_a_fundraiser", "Host A Fundraiser"),
    ("host_a_house_party", "Host A House Party"),
    ("attend_a_house_party", "Attend A House Party"),
    ("other", "Other")
]


TOPICS_OF_INTEREST = [
    ("foreign_policy", "Foreign Policy"),
    ("education", "Education"),
    ("environment", "Environment"),
    ("agriculture", "Agriculture"),
    ("energy", "Energy"),
    ("space", "Space"),
    ("fiscal", "Fiscal"),
    ("social", "Social"),
    ("science", "Science"),
    ("drugs", "Drugs"),
    ("defense", "Defense"),
    ("health", "Health")
]

DEFAULT_SENTENCE_COUNT = 7
DEFAULT_SUMMARY_LENGTH = 250
TIME_EXCLUSION_REGEX = re.compile(
    r'(1[012]|[1-9]):[0-5][0-9](\\s)?(?i)\s?(am|pm|AM|PM)')
URL_REGEX = r'\b((?:https?:(?:|[a-z0-9%])|[a-z0-9.\-]+[.](?:com|net|org|edu' \
            r'|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name' \
            r'|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar' \
            r'|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs' \
            r'|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu' \
            r'|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi' \
            r'|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs' \
            r'|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it' \
            r'|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk' \
            r'|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr' \
            r'|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz' \
            r'|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru' \
            r'|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su' \
            r'|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw' \
            r'|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za' \
            r'|zm|zw))(?:[^\s()<>{}\[\]]+|\([^\s()]*?\([^\s()]+\)[^\s()]*?' \
            r'\)|\([^\s]+?\))+(?:\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s' \
            r']+?\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’])|(?:[a-z0-9]+(?:[.\-][a" \
            r'-z0-9]+)*[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop' \
            r'|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad' \
            r'|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|' \
            r'bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|' \
            r'ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|' \
            r'dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|' \
            r'gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|' \
            r'id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|' \
            r'kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|' \
            r'mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|' \
            r'ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|' \
            r'pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|' \
            r'Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|' \
            r'tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|' \
            r'vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)\b(?!@)))'
DEFAULT_EXCLUDE_SENTENCES = ["Story highlights", "#", "##", "Discover Dubai",
                             "By ", "Caption", "caption", "photos:", "1 of ",
                             'JPG', 'jpg', 'png', "PNG", "ID:", "(REUTERS)",
                             "Image", "BREAKING", "FORM", "1.", "by",
                             "FFFD", "Fuck", "Shit", "Ass", "Cunt", "Jizz",
                             '[', ']', '{', '}', '*', 'Related Topics:',
                             'related topics:', '+', '=', 'free',
                             'RELATED ARTICLES',
                             'Continue reading', 'http', 'GODDAMMIT', 'hr',
                             'min', 'main story', 'main', '(', ')', '/', '\\',
                             'Advertisement', 'Photo', 'Erectile Dysfunction']

DEFAULT_EXCLUDE_ARTICLES = ['Discover Dubai', 'become a millionaire',
                            'Burn More Calories and Lose Weight',
                            'Burn More Calories', 'Lose Weight',
                            "lose weight",
                            "No one wants to adopt Rory the cat: "
                            "Called 'Cat Dracula' | Examiner.com",
                            "Petition:", "petition:", "Petition",
                            "Sex Positions", "sex positions", "Orgasm",
                            "orgasm", "Fuck", "Shit", "Ass", "Cunt",
                            "Jizz", 'free']
BLOCKED_SITE = ['wnd.com', 'nationalenquirer.com']
UNSUPPORTED_UPLOAD_SITES = ['theguardian.com', 'circleci.com', 'wnd.com']
COMPANY_ACRONYMS = [
    ('ABC', 'Abc'), ('CNN', 'Cnn'), ('CBS', 'Cbs'),
    ('MSNBC', 'Msnbc'), ('BBC', 'Bbc'), ('CBC', 'Cbc'), ('CBS', 'Cbs'),
    ('NBC', 'Nbc'), ('NYT', 'Nyt'), ('PBS', 'Pbs'),
    ('cnnpolitics.com', 'Cnnpolitics.com'),
    ('NPR', 'Npr'), ('N.P.R.', 'N.p.r'), ('N.P.R', 'N.p.r'), ('N.Y.T', 'N.y.t'),
    ('N.Y.T.', 'N.y.t.'), ('TYT', 'Tyt'), ('T.Y.T.', 'T.y.t.'), ('FBI', 'Fbi'),
    ('F.B.I', 'F.b.i'), ('F.B.I.', 'F.b.i.'), ('CIA', 'Cia'),
    ('C.I.A.', 'C.i.a.'), ('C.I.A', 'C.i.a'), ('NSA', 'Nsa'),
    ('N.S.A', 'N.s.a'), ('N.S.A.', 'N.s.a.'), ('NASA', 'Nasa'),
    ('N.A.S.A', 'N.a.s.a'), ('N.A.S.A.', 'N.a.s.a.'), ('FEMA', 'Fema'),
    ('F.E.M.A.', 'F.e.m.a.'), ('F.E.M.A', 'F.e.m.a'), ('DOJ', 'Doj'),
    ('D.O.J', 'D.o.j'), ('D.O.J.', 'D.o.j.'), ('CDC', 'Cdc'),
    ('C.D.C', 'C.d.c'), ('C.D.C.', 'C.d.c.'), ('HEPA', 'Hepa'),
    ('H.E.P.A', 'H.e.p.a'), ('H.E.P.A.', 'H.e.p.a.'), ('U.S.', 'U.s.'),
    ('US', 'Us'), ('USA', 'Usa'), ('U.S.A.', 'U.s.a.'), ('U.S.A', 'U.s.a'),
    ('APC', 'Apc'), ('PDP', 'Pdp'), ('ISIS', 'Isis'), ('.com', '.Com'),
    ('abc7.com', 'Abc7.com'), ('cnn.com', 'Cnn.com'), ('ft.com', 'Ft.com'),
    ('World War II', 'World War Ii'), ('World War I', 'World War i'),
    ('DC', 'Dc'), ('D.C.', 'D.c.'), ('DMV', 'Dmv'), ('DNC', 'Dnc'),
    ('RNC', 'Rnc'), ('D.N.C.', 'D.n.c.'), ('R.N.C.', 'R.n.c.'),
    ('PC', 'Pc'), ('P.C.', 'P.c.'), ('LGBT', 'Lgbt'),
    ('L.G.B.T.', 'L.g.b.t.'), ('L.G.B.T', 'L.g.b.t'),
    ('LA Times', 'La Times'), ('L.A. Times', 'L.a. Times'),
    ('9th', '9Th'), ('ITV', 'Itv'), ('DNA', 'Dna'),
    ('AG', 'Ag'),  (u'AL', u'Al'), (u'AK', u'Ak'),
    (u'AZ', u'Az'), (u'AR', u'Ar'), (u'CA', u'Ca'),
    (u'CO', u'Co'), (u'CT', u'Ct'), (u'DK', u'Dk'), (u'DE', u'De'),
    (u'DC', u'Dc'), (u'FL', u'Fl'), (u'GA', u'Ga'), (u'GU', u'Gu'),
    (u'HI', u'Hi'), (u'ID', u'Id'), (u'IL', u'Il'),
    (u'IA', u'Ia'), (u'KS', u'Ks'), (u'KY', u'Ky'),  (u'LA', u'La'),
    (u'MD', u'Md'), (u'MI', u'Mi'), ('NRA', 'Nra'), ('N.R.A.', 'N.r.a.'),
    ('N.R.A', 'N.r.a'), ('UN', 'Un'), ('U.N.', 'U.n.'), ('U.N', 'U.n'),
    ('UNICEF', 'Unicef'), ('U.N.I.C.E.F.', 'U.n.i.c.e.f.'),
    ('U.N.I.C.E.F', 'U.n.i.c.e.f'),
    (u'MN', u'Mn'), (u'MO', u'Mo'), (u'MT', u'Mt'),
    (u'NE', u'Ne'), (u'NV', u'Nv'), (u'NH', u'Nh'), (u'NJ', u'Nj'),
    (u'NM', u'Nm'), (u'NY', u'Ny'), (u'NC', u'Nc'), (u'ND', u'Nd'),
    (u'MP', u'Mp'), ('EU', 'Eu'), ('UK', 'Uk'), ('De', 'DE'),
    (u'OL', u'Ol'), (u'PA', u'Pa'), (u'PI', u'Pi'), (u'PR', u'Pr'),
    (u'RI', u'Ri'), (u'SC', u'Sc'), (u'SD', u'Sd'), (u'TN', u'Tn'),
    (u'TX', u'Tx'), (u'UT', u'Ut'), (u'VT', u'Vt'), (u'VI', u'Vi'),
    (u'VA', u'Va'), (u'WA', u'Wa'), (u'WV', u'Wv'), (u'WI', u'Wi'),
    (u'WY', u'Wy')
]


EXPLICIT_SITES = ['xvideos.com', 'xhamster.com', 'pornhub.com', 'xnxx.com',
                  'redtube.com', 'youporn.com', 'tube8.com', 'youjizz.com',
                  'hardsextube.com', 'beeg.com', 'motherless.com',
                  'drtuber.com', 'nuvid.com', 'pornerbros.com',
                  'spankwire.com', 'keezmovies.com', 'sunporno.com',
                  'porn.com', '4tube.com', 'alphaporno.com', 'xtube.com',
                  'pornoxo.com', 'yobt.com', 'tnaflix.com', 'pornsharia.com',
                  'brazzers.com', 'extremetube.com', 'slutload.com',
                  'fapdu.com', 'empflix.com', 'alotporn.com', 'vid2c.com',
                  'Shufuni.com', 'cliphunter.com', 'xxxbunker.com',
                  'madthumbs.com', 'deviantclip.com', 'twilightsex.com',
                  'pornhost.com', 'fux.com', 'jizzhut.com', 'spankbang.com',
                  'eporner.com', 'orgasm.com', 'yuvutu.com', 'kporno.com',
                  'definebabe.com', 'secret.shooshtime.com', 'mofosex.com',
                  'hotgoo.com', 'submityourflicks.com', 'xxx.com',
                  'bigtits.com', 'media.xxxaporn.com', 'bonertube.com',
                  'userporn.com', 'jizzonline.com', 'pornotube.com',
                  'fookgle.com', 'free18.net', 'tub99.com', 'nonktube.com',
                  'mastishare.com', 'tjoob.com', 'rude.com', 'bustnow.com',
                  'pornrabbit.com', 'pornative.com', 'sluttyred.com',
                  'boysfood.com', 'moviefap.com', 'lubetube.com',
                  'submityourtapes.com', 'megafilex.com', 'hdpornstar.com',
                  'al4a.com', 'stileproject.com', 'xogogo.com', 'filthyrx.com',
                  'jizzbo.com', '5ilthy.com', '91porn.com',
                  'lesbianpornvideos.com', 'eroxia.com', 'iyottube.com',
                  'yourfreeporn.us', 'sexoasis.com', 'fucktube.com',
                  'pornomovies.com', 'clearclips.com', 'moviesand.com',
                  'tubixe.com', 'pornjog.com', 'sextv1.pl', 'desihoes.com',
                  'pornupload.com', 'kosimak.com', 'videocasalinghi.com',
                  'lubeyourtube.com', 'freudbox.com', 'moviesguy.com',
                  'motherofporn.com', '141tube.com', 'my18tube.com',
                  'bigupload.com xvds.com', 'fastjizz.com', 'tubeland.com',
                  'ultimatedesi.net', 'teenporntube.com', 'tubave.com',
                  'afunnysite.com', 'sexe911.com', 'megaporn.com',
                  'porntitan.com', 'pornheed.com', 'youhot.gr',
                  'videolovesyou.com', 'onlymovies.com', 'hdporn.net',
                  'adultvideodump.com', 'suzisporn.com', 'xfilmes.tv',
                  'pornwall.com', 'silverdaddiestube.com',
                  'sextube.sweetcollegegirls.com', 'ipadporn.com',
                  'youporns.org', 'movietitan.com', 'yaptube.com', 'jugy.com',
                  'chumleaf.com', 'panicporn.com', 'milfporntube.com',
                  'timtube.com', 'wetpussy.com', 'whoreslag.com',
                  'xfapzap.com', 'xvideohost.com', 'tuberip.com',
                  'dirtydirtyangels.com', 'bigerotica.com', 'pk5.net',
                  'theamateurzone.info', 'triniporn.org', 'youbunny.com',
                  'isharemybitch.com', 'morningstarclub.com', 'sexkate.com',
                  'kuntfutube.com', 'porncor.com', 'thegootube.com',
                  'tubeguild.com', 'fuckuh.com', 'tube.smoder.com',
                  'zuzandra.com', 'nextdoordolls.com', 'myjizztube.com',
                  'homesexdaily.com', 'thetend.com', 'yourpornjizz.com',
                  'tgirls.com', 'pornwaiter.com', 'pornhub.pl',
                  'nurglestube.com', 'brazzershdtube.com', 'upthevideo.com',
                  'sexzworld.com', 'cuntest.com', 'ahtube.com',
                  'free2peek.com', 'freeamatube.com', 'thexxxtube.net',
                  'yazum.com', 'tubesexes.com', 'pornload.com', 'vankoi.com',
                  'dailee.com', 'ejason21.com', 'openpunani.com',
                  'porntubexl.nl', 'scafy.com', 'bangbull.com', 'vidxnet.com',
                  'yteenporn.com', 'tubethumbs.com', 'faptv.com', 'nasty8.com',
                  'maxjizztube.com', 'pornunder.com', '24h-porn.net',
                  'xclip.tv', 'jerkersworld.com', 'desibomma.com',
                  'jizzbox.com', 'theyxxx.com', 'bonkwire.com',
                  'PornTelecast.com', 'pornsitechoice.com', 'yporn.tv',
                  'girlsongirlstube.com', 'famouspornstarstube.com',
                  'sexfans.org', 'youpornxl.com', 'rudeshare.com',
                  'efuckt.com', 'koostube.com', 'amateursex.com',
                  'moviegator.com', 'cobramovies.com', 'cantoot.com',
                  'yourhottube.com', 'teentube18.com', 'youxclip.com',
                  'flicklife.com', 'nastyrat.tv', 'freepornfox.com',
                  'freeadultwatch.com', 'fucked.tv', 'sextube.si',
                  'pornrater.com', 'wheresmygf.com', 'xfanny.com',
                  'pornorake.com', 'untouched.tv', 'guppyx.com',
                  'mylivesex.tv', 'pervaliscious.com', 'sex2ube.com',
                  'suckjerkcock.com', 'netporn.nl', 'exgfvid.com',
                  'koalaporn.com', 'bbhgvidz.com', 'evilhub.com',
                  'celebritytubester.com', 'pornfish.com', 'jrkn.com',
                  'bootyclips.com', 'tubeguide.info', 'realhomemadetube.com',
                  'tokenxxxporn.com', 'pornvideoflix.com', 'sinfultube.net',
                  'pornler.com', 'sharexvideo.com', '69youPorn.com',
                  'submitmyvideo.com', 'kastit.com', 'pornini.com',
                  'hd4sex.com', 'laftube.com', 'mosestube.com',
                  'dutchxtube.com', 'porncastle.net', 'tubedatbooty.com',
                  'pornvie.com', 'pornopantry.com', 'springbreaktubegirls.com',
                  'tube4u.net', 'nsfwftw.com', 'pornozabava.com',
                  'tgutube.com', 'celebritynudez.com', 'teeztube.com',
                  'collegefucktube.com', 'adultvideomate.com',
                  'porntubemoviez.com', 'bigjuggs.com', 'hornypickle.com',
                  'mypornow.com', 'pushingpink.com', 'xxxshare.ru',
                  'nuuporn.com', 'melontube.com', 'myamateurporntube.com',
                  'soyouthinkyourapornstar.com', 'porntubestreet.com',
                  'pornogoddess.com', 'cumsnroses.com', 'porntubeclipz.com',
                  'lcgirls.com', 'housewifes.com', 'cactarse.com',
                  'cumfox.com', 'tube17.com', 'teenbrosia.com',
                  'lesbiantubemovies.com', 'xxxset.com', 'gagahub.com',
                  'jugland.com', 'porntubesurf.com', 'freakybuddy.com',
                  'sexdraw.com', 'sexovirtual.com', 'pornsmack.com',
                  'gratisvideokijken.nl', 'eroticadulttube.com',
                  'bharatporn.com', 'fmeporn.com', 'darkpost.com',
                  'sexporndump.com', 'sexandporn.org', 'jezzytube.com',
                  'justpornclip.com', 'xxxpornow.com', 'inseks.com',
                  'freeporn777.com', 'porndisk.com', 'adultfunnow.com',
                  'youporn.us.com', 'babecumtv.com',
                  'girlskissinggirlsvideos.com', 'specialtytubeporn.com',
                  'teentube.be', 'www.xvideos.com', 'www.xhamster.com',
                  'www.pornhub.com', 'www.xnxx.com', 'www.redtube.com',
                  'www.youporn.com', 'www.tube8.com', 'www.youjizz.com',
                  'www.hardsextube.com', 'www.beeg.com', 'www.motherless.com',
                  'www.drtuber.com', 'www.nuvid.com', 'www.pornerbros.com',
                  'www.spankwire.com', 'www.keezmovies.com',
                  'www.sunporno.com', 'www.porn.com', '4tube.com',
                  'www.alphaporno.com', 'www.xtube.com', 'www.pornoxo.com',
                  'www.yobt.com', 'www.tnaflix.com', 'www.pornsharia.com',
                  'www.brazzers.com', 'www.extremetube.com',
                  'www.slutload.com', 'www.fapdu.com', 'www.empflix.com',
                  'www.alotporn.com', 'www.vid2c.com', 'www.Shufuni.com',
                  'www.cliphunter.com', 'www.xxxbunker.com',
                  'www.madthumbs.com', 'www.deviantclip.com',
                  'www.twilightsex.com', 'www.pornhost.com', 'www.fux.com',
                  'www.jizzhut.com', 'www.spankbang.com', 'www.eporner.com',
                  'www.orgasm.com', 'www.yuvutu.com', 'www.kporno.com',
                  'www.definebabe.com', 'secret.shooshtime.com',
                  'www.mofosex.com', 'www.hotgoo.com',
                  'www.submityourflicks.com', 'www.xxx.com', 'www.bigtits.com',
                  'media.xxxaporn.com', 'www.bonertube.com',
                  'www.userporn.com', 'www.jizzonline.com',
                  'www.pornotube.com', 'www.fookgle.com', 'free18.net',
                  'www.tub99.com', 'www.nonktube.com', 'www.mastishare.com',
                  'www.tjoob.com', 'www.rude.com', 'www.bustnow.com',
                  'www.pornrabbit.com', 'www.pornative.com',
                  'www.sluttyred.com', 'www.boysfood.com', 'www.moviefap.com',
                  'www.lubetube.com', 'www.submityourtapes.com',
                  'www.megafilex.com', 'www.hdpornstar.com', 'www.al4a.com',
                  'www.stileproject.com', 'www.xogogo.com', 'www.filthyrx.com',
                  'www.jizzbo.com', '5ilthy.com', '91porn.com',
                  'www.lesbianpornvideos.com', 'www.eroxia.com',
                  'www.iyottube.com', 'yourfreeporn.us', 'www.sexoasis.com',
                  'www.fucktube.com', 'www.pornomovies.com',
                  'www.clearclips.com', 'www.moviesand.com', 'www.tubixe.com',
                  'www.pornjog.com', 'sextv1.pl', 'www.desihoes.com',
                  'www.pornupload.com', 'www.kosimak.com',
                  'www.videocasalinghi.com', 'www.lubeyourtube.com',
                  'www.freudbox.com', 'www.moviesguy.com',
                  'www.motherofporn.com', '141tube.com', 'www.my18tube.com',
                  'bigupload.com xvds.com', 'www.fastjizz.com',
                  'www.tubeland.com', 'ultimatedesi.net',
                  'www.teenporntube.com', 'www.tubave.com',
                  'www.afunnysite.com', 'www.sexe911.com', 'www.megaporn.com',
                  'www.porntitan.com', 'www.pornheed.com', 'youhot.gr',
                  'www.videolovesyou.com', 'www.onlymovies.com', 'hdporn.net',
                  'www.adultvideodump.com', 'www.suzisporn.com', 'xfilmes.tv',
                  'www.pornwall.com', 'www.silverdaddiestube.com',
                  'sextube.sweetcollegegirls.com', 'www.ipadporn.com',
                  'youporns.org', 'www.movietitan.com', 'www.yaptube.com',
                  'www.jugy.com', 'www.chumleaf.com', 'www.panicporn.com',
                  'www.milfporntube.com', 'www.timtube.com',
                  'www.wetpussy.com', 'www.whoreslag.com', 'www.xfapzap.com',
                  'www.xvideohost.com', 'www.tuberip.com',
                  'www.dirtydirtyangels.com', 'www.bigerotica.com', 'pk5.net',
                  'theamateurzone.info', 'triniporn.org', 'www.youbunny.com',
                  'www.isharemybitch.com', 'www.morningstarclub.com',
                  'www.sexkate.com', 'www.kuntfutube.com', 'www.porncor.com',
                  'www.thegootube.com', 'www.tubeguild.com', 'www.fuckuh.com',
                  'tube.smoder.com', 'www.zuzandra.com',
                  'www.nextdoordolls.com', 'www.myjizztube.com',
                  'www.homesexdaily.com', 'www.thetend.com',
                  'www.yourpornjizz.com', 'www.tgirls.com',
                  'www.pornwaiter.com', 'pornhub.pl', 'www.nurglestube.com',
                  'www.brazzershdtube.com', 'www.upthevideo.com',
                  'www.sexzworld.com', 'www.cuntest.com', 'www.ahtube.com',
                  'www.free2peek.com', 'www.freeamatube.com', 'thexxxtube.net',
                  'www.yazum.com', 'www.tubesexes.com', 'www.pornload.com',
                  'www.vankoi.com', 'www.dailee.com', 'www.ejason21.com',
                  'www.openpunani.com', 'porntubexl.nl', 'www.scafy.com',
                  'www.bangbull.com', 'www.vidxnet.com', 'www.yteenporn.com',
                  'www.tubethumbs.com', 'www.faptv.com', 'www.nasty8.com',
                  'www.maxjizztube.com', 'www.pornunder.com', '24h-porn.net',
                  'xclip.tv', 'www.jerkersworld.com', 'www.desibomma.com',
                  'www.jizzbox.com', 'www.theyxxx.com', 'www.bonkwire.com',
                  'www.PornTelecast.com', 'www.pornsitechoice.com', 'yporn.tv',
                  'www.girlsongirlstube.com', 'www.famouspornstarstube.com',
                  'sexfans.org', 'www.youpornxl.com', 'www.rudeshare.com',
                  'www.efuckt.com', 'www.koostube.com', 'www.amateursex.com',
                  'www.moviegator.com', 'www.cobramovies.com',
                  'www.cantoot.com', 'www.yourhottube.com',
                  'www.teentube18.com', 'www.youxclip.com',
                  'www.flicklife.com', 'nastyrat.tv', 'www.freepornfox.com',
                  'www.freeadultwatch.com', 'fucked.tv', 'sextube.si',
                  'www.pornrater.com', 'www.wheresmygf.com', 'www.xfanny.com',
                  'www.pornorake.com', 'untouched.tv', 'www.guppyx.com',
                  'mylivesex.tv', 'www.pervaliscious.com', 'www.sex2ube.com',
                  'www.suckjerkcock.com', 'netporn.nl', 'www.exgfvid.com',
                  'www.koalaporn.com', 'www.bbhgvidz.com', 'www.evilhub.com',
                  'www.celebritytubester.com', 'www.pornfish.com',
                  'www.jrkn.com', 'www.bootyclips.com', 'tubeguide.info',
                  'www.realhomemadetube.com', 'www.tokenxxxporn.com',
                  'www.pornvideoflix.com', 'sinfultube.net', 'www.pornler.com',
                  'www.sharexvideo.com', '69youPorn.com',
                  'www.submitmyvideo.com', 'www.kastit.com', 'www.pornini.com',
                  'www.hd4sex.com', 'www.laftube.com', 'www.mosestube.com',
                  'www.dutchxtube.com', 'porncastle.net',
                  'www.tubedatbooty.com', 'www.pornvie.com',
                  'www.pornopantry.com', 'www.springbreaktubegirls.com',
                  'tube4u.net', 'www.nsfwftw.com', 'www.pornozabava.com',
                  'www.tgutube.com', 'www.celebritynudez.com',
                  'www.teeztube.com', 'www.collegefucktube.com',
                  'www.adultvideomate.com', 'www.porntubemoviez.com',
                  'www.bigjuggs.com', 'www.hornypickle.com',
                  'www.mypornow.com', 'www.pushingpink.com', 'xxxshare.ru',
                  'www.nuuporn.com', 'www.melontube.com',
                  'www.myamateurporntube.com',
                  'www.soyouthinkyourapornstar.com', 'www.porntubestreet.com',
                  'www.pornogoddess.com', 'www.cumsnroses.com',
                  'www.porntubeclipz.com', 'www.lcgirls.com',
                  'www.housewifes.com', 'www.cactarse.com', 'www.cumfox.com',
                  'www.tube17.com', 'www.teenbrosia.com',
                  'www.lesbiantubemovies.com', 'www.xxxset.com',
                  'www.gagahub.com', 'www.jugland.com', 'www.porntubesurf.com',
                  'www.freakybuddy.com', 'www.sexdraw.com',
                  'www.sexovirtual.com', 'www.pornsmack.com',
                  'gratisvideokijken.nl', 'www.eroticadulttube.com',
                  'www.bharatporn.com', 'www.fmeporn.com', 'www.darkpost.com',
                  'www.sexporndump.com', 'sexandporn.org', 'www.jezzytube.com',
                  'www.justpornclip.com', 'www.xxxpornow.com',
                  'www.inseks.com', 'www.freeporn777.com', 'www.porndisk.com',
                  'www.adultfunnow.com', 'youporn.us.com', 'www.babecumtv.com',
                  'www.girlskissinggirlsvideos.com',
                  'www.specialtytubeporn.com']

COUNTRIES = [
    (u'US', u'United States of America'),
    (u'BD', u'Bangladesh'),
    (u'BE', u'Belgium'),
    (u'BF', u'Burkina Faso'),
    (u'BG', u'Bulgaria'),
    (u'BA', u'Bosnia and Herzegovina'),
    (u'BB', u'Barbados'),
    (u'WF', u'Wallis and Futuna'),
    (u'BL', u'Saint Barth\xe9lemy'),
    (u'BM', u'Bermuda'),
    (u'BN', u'Brunei'),
    (u'BO', u'Bolivia'),
    (u'BH', u'Bahrain'),
    (u'BI', u'Burundi'),
    (u'BJ', u'Benin'),
    (u'BT', u'Bhutan'),
    (u'JM', u'Jamaica'),
    (u'BV', u'Bouvet Island'),
    (u'BW', u'Botswana'),
    (u'WS', u'Samoa'),
    (u'BQ', u'Bonaire, Sint Eustatius and Saba'),
    (u'BR', u'Brazil'),
    (u'BS', u'Bahamas'),
    (u'JE', u'Jersey'),
    (u'BY', u'Belarus'),
    (u'BZ', u'Belize'),
    (u'RU', u'Russia'),
    (u'RW', u'Rwanda'),
    (u'RS', u'Serbia'),
    (u'TL', u'Timor-Leste'),
    (u'RE', u'R\xe9union'),
    (u'TM', u'Turkmenistan'),
    (u'TJ', u'Tajikistan'),
    (u'RO', u'Romania'),
    (u'TK', u'Tokelau'),
    (u'GW', u'Guinea-Bissau'),
    (u'GU', u'Guam'),
    (u'GT', u'Guatemala'),
    (u'GS', u'South Georgia and the South Sandwich Islands'),
    (u'GR', u'Greece'),
    (u'GQ', u'Equatorial Guinea'),
    (u'GP', u'Guadeloupe'),
    (u'JP', u'Japan'),
    (u'GY', u'Guyana'),
    (u'GG', u'Guernsey'),
    (u'GF', u'French Guiana'),
    (u'GE', u'Georgia'),
    (u'GD', u'Grenada'),
    (u'GB', u'United Kingdom'),
    (u'GA', u'Gabon'),
    (u'GN', u'Guinea'),
    (u'GM', u'Gambia'),
    (u'GL', u'Greenland'),
    (u'GI', u'Gibraltar'),
    (u'GH', u'Ghana'),
    (u'OM', u'Oman'),
    (u'TN', u'Tunisia'),
    (u'JO', u'Jordan'),
    (u'HR', u'Croatia'),
    (u'HT', u'Haiti'),
    (u'HU', u'Hungary'),
    (u'HK', u'Hong Kong'),
    (u'HN', u'Honduras'),
    (u'HM', u'Heard Island and McDonald Islands'),
    (u'VE', u'Venezuela'),
    (u'PR', u'Puerto Rico'),
    (u'PS', u'Palestine, State of'),
    (u'PW', u'Palau'),
    (u'PT', u'Portugal'),
    (u'KN', u'Saint Kitts and Nevis'),
    (u'PY', u'Paraguay'),
    (u'IQ', u'Iraq'),
    (u'PA', u'Panama'),
    (u'PF', u'French Polynesia'),
    (u'PG', u'Papua New Guinea'),
    (u'PE', u'Peru'),
    (u'PK', u'Pakistan'),
    (u'PH', u'Philippines'),
    (u'PN', u'Pitcairn'),
    (u'PL', u'Poland'),
    (u'PM', u'Saint Pierre and Miquelon'),
    (u'ZM', u'Zambia'),
    (u'EH', u'Western Sahara'),
    (u'EE', u'Estonia'),
    (u'EG', u'Egypt'),
    (u'ZA', u'South Africa'),
    (u'EC', u'Ecuador'),
    (u'IT', u'Italy'),
    (u'VN', u'Vietnam'),
    (u'SB', u'Solomon Islands'),
    (u'ET', u'Ethiopia'),
    (u'SO', u'Somalia'),
    (u'ZW', u'Zimbabwe'),
    (u'SA', u'Saudi Arabia'),
    (u'ES', u'Spain'),
    (u'ER', u'Eritrea'),
    (u'ME', u'Montenegro'),
    (u'MD', u'Moldova'),
    (u'MG', u'Madagascar'),
    (u'MF', u'Saint Martin (French part)'),
    (u'MA', u'Morocco'),
    (u'MC', u'Monaco'),
    (u'UZ', u'Uzbekistan'),
    (u'MM', u'Myanmar'),
    (u'ML', u'Mali'),
    (u'MO', u'Macao'),
    (u'MN', u'Mongolia'),
    (u'MH', u'Marshall Islands'),
    (u'MK', u'Macedonia'),
    (u'MU', u'Mauritius'),
    (u'MT', u'Malta'),
    (u'MW', u'Malawi'),
    (u'MV', u'Maldives'),
    (u'MQ', u'Martinique'),
    (u'MP', u'Northern Mariana Islands'),
    (u'MS', u'Montserrat'),
    (u'MR', u'Mauritania'),
    (u'IM', u'Isle of Man'),
    (u'UG', u'Uganda'),
    (u'TZ', u'Tanzania'),
    (u'MY', u'Malaysia'),
    (u'MX', u'Mexico'),
    (u'IL', u'Israel'),
    (u'FR', u'France'),
    (u'AW', u'Aruba'),
    (u'SH', u'Saint Helena, Ascension and Tristan da Cunha'),
    (u'SJ', u'Svalbard and Jan Mayen'),
    (u'FI', u'Finland'),
    (u'FJ', u'Fiji'),
    (u'FK', u'Falkland Islands  [Malvinas]'),
    (u'FM', u'Micronesia (Federated States of)'),
    (u'FO', u'Faroe Islands'),
    (u'NI', u'Nicaragua'),
    (u'NL', u'Netherlands'),
    (u'NO', u'Norway'),
    (u'NA', u'Namibia'),
    (u'VU', u'Vanuatu'),
    (u'NC', u'New Caledonia'),
    (u'NE', u'Niger'),
    (u'NF', u'Norfolk Island'),
    (u'NG', u'Nigeria'),
    (u'NZ', u'New Zealand'),
    (u'NP', u'Nepal'),
    (u'NR', u'Nauru'),
    (u'NU', u'Niue'),
    (u'CK', u'Cook Islands'),
    (u'CI', u"C\xf4te d'Ivoire"),
    (u'CH', u'Switzerland'),
    (u'CO', u'Colombia'),
    (u'CN', u'China'),
    (u'CM', u'Cameroon'),
    (u'CL', u'Chile'),
    (u'CC', u'Cocos (Keeling) Islands'),
    (u'CA', u'Canada'),
    (u'CG', u'Congo'),
    (u'CF', u'Central African Republic'),
    (u'CD', u'Congo (the Democratic Republic of the)'),
    (u'CZ', u'Czech Republic'),
    (u'CY', u'Cyprus'),
    (u'CX', u'Christmas Island'),
    (u'CR', u'Costa Rica'),
    (u'CW', u'Cura\xe7ao'),
    (u'CV', u'Cabo Verde'),
    (u'CU', u'Cuba'),
    (u'SZ', u'Swaziland'),
    (u'SY', u'Syria'),
    (u'SX', u'Sint Maarten (Dutch part)'),
    (u'KG', u'Kyrgyzstan'),
    (u'KE', u'Kenya'),
    (u'SS', u'South Sudan'),
    (u'SR', u'Suriname'),
    (u'KI', u'Kiribati'),
    (u'KH', u'Cambodia'),
    (u'SV', u'El Salvador'),
    (u'KM', u'Comoros'),
    (u'ST', u'Sao Tome and Principe'),
    (u'SK', u'Slovakia'),
    (u'KR', u'South Korea'),
    (u'SI', u'Slovenia'),
    (u'KP', u'North Korea'),
    (u'KW', u'Kuwait'),
    (u'SN', u'Senegal'),
    (u'SM', u'San Marino'),
    (u'SL', u'Sierra Leone'),
    (u'SC', u'Seychelles'),
    (u'KZ', u'Kazakhstan'),
    (u'KY', u'Cayman Islands'),
    (u'SG', u'Singapore'),
    (u'SE', u'Sweden'),
    (u'SD', u'Sudan'),
    (u'DO', u'Dominican Republic'),
    (u'DM', u'Dominica'),
    (u'DJ', u'Djibouti'),
    (u'DK', u'Denmark'),
    (u'VG', u'Virgin Islands (British)'),
    (u'DE', u'Germany'),
    (u'YE', u'Yemen'),
    (u'DZ', u'Algeria'),
    (u'UY', u'Uruguay'),
    (u'YT', u'Mayotte'),
    (u'UM', u'United States Minor Outlying Islands'),
    (u'LB', u'Lebanon'),
    (u'LC', u'Saint Lucia'),
    (u'LA', u'Laos'),
    (u'TV', u'Tuvalu'),
    (u'TW', u'Taiwan'),
    (u'TT', u'Trinidad and Tobago'),
    (u'TR', u'Turkey'),
    (u'LK', u'Sri Lanka'),
    (u'LI', u'Liechtenstein'),
    (u'LV', u'Latvia'),
    (u'TO', u'Tonga'),
    (u'LT', u'Lithuania'),
    (u'LU', u'Luxembourg'),
    (u'LR', u'Liberia'),
    (u'LS', u'Lesotho'),
    (u'TH', u'Thailand'),
    (u'TF', u'French Southern Territories'),
    (u'TG', u'Togo'),
    (u'TD', u'Chad'),
    (u'TC', u'Turks and Caicos Islands'),
    (u'LY', u'Libya'),
    (u'VA', u'Holy See'),
    (u'VC', u'Saint Vincent and the Grenadines'),
    (u'AE', u'United Arab Emirates'),
    (u'AD', u'Andorra'),
    (u'AG', u'Antigua and Barbuda'),
    (u'AF', u'Afghanistan'),
    (u'AI', u'Anguilla'),
    (u'VI', u'Virgin Islands (U.S.)'),
    (u'IS', u'Iceland'),
    (u'IR', u'Iran'),
    (u'AM', u'Armenia'),
    (u'AL', u'Albania'),
    (u'AO', u'Angola'),
    (u'AQ', u'Antarctica'),
    (u'AS', u'American Samoa'),
    (u'AR', u'Argentina'),
    (u'AU', u'Australia'),
    (u'AT', u'Austria'),
    (u'IO', u'British Indian Ocean Territory'),
    (u'IN', u'India'),
    (u'AX', u'\xc5land Islands'),
    (u'AZ', u'Azerbaijan'),
    (u'IE', u'Ireland'),
    (u'ID', u'Indonesia'),
    (u'UA', u'Ukraine'),
    (u'QA', u'Qatar'),
    (u'MZ', u'Mozambique')
]
