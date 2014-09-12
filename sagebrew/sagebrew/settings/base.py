' Django default settings for automated_test_client project.'
from __future__ import absolute_import

from os import environ, path, makedirs
from unipath import Path
from datetime import timedelta


PROJECT_DIR = Path(__file__).ancestor(3)
REPO_DIR = Path(__file__).ancestor(4)
MEDIA_ROOT = PROJECT_DIR.child("media")
STATIC_ROOT = PROJECT_DIR.child("static")

DEBUG = False
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Devon Bleibtrey', 'bleib1dj@gmail.com'),
)

environ['HTTPS'] = "on"
MANAGERS = ADMINS

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'UTC'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/var/www/example.com/media/"

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://example.com/media/", "http://media.example.com/"
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/var/www/example.com/static/"

# URL prefix for static files.
# Example: "http://example.com/static/", "http://static.example.com/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    '%s/sagebrew/static/' % PROJECT_DIR,
    '%s/plebs/static/' % PROJECT_DIR,
    '%s/sb_registration/static/' % PROJECT_DIR,
    '%s/sb_comments/static/' % PROJECT_DIR,
    '%s/sb_posts/static/' % PROJECT_DIR,
    '%s/sb_relationships/static/' % PROJECT_DIR,
    '%s/sb_questions/static/' % PROJECT_DIR,
    '%s/sb_answers/static/' % PROJECT_DIR,
    '%s/sb_search/static/' % PROJECT_DIR,
    '%s/sb_tag/static/' % PROJECT_DIR,
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    # 'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.


# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    # 'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'djangosecure.middleware.SecurityMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'sagebrew.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'sagebrew.wsgi.application'

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.core.context_processors.request",
    'django.contrib.auth.context_processors.auth',
    "allauth.account.context_processors.account",
    "allauth.socialaccount.context_processors.socialaccount",
)

AUTHENTICATION_BACKENDS = (
    # Needed to login by username in Django admin, regardless of `allauth`
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
)

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates"
    # or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    '%s/sagebrew/templates/' % PROJECT_DIR,
    '%s/sb_registration/templates/' % PROJECT_DIR,
    '%s/sb_wall/templates/' % PROJECT_DIR,
    '%s/plebs/templates/' % PROJECT_DIR,
    '%s/sb_questions/templates/' % PROJECT_DIR,
    '%s/sb_answers/templates/' % PROJECT_DIR,
    '%s/sb_search/templates/' % PROJECT_DIR,
)

FIXTURE_DIRS = (
    '%s/sagebrew/fixtures/' % PROJECT_DIR,
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'djangosecure',
    'django_admin_bootstrapped',
    'django.contrib.admin',
    'djcelery',
    'rest_framework',
    'admin_honeypot',
    'provider',
    'provider.oauth2',
    'storages',
    'localflavor',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.facebook',
    'plebs',
    'api',
    'govtrack',
    'neomodel',
    'sb_registration',
    'sb_comments',
    'sb_posts',
    'sb_wall',
    'sb_notifications',
    'sb_relationships',
    'sb_garbage',
    'sb_tag',
    'sb_questions',
    'sb_answers',
    'sb_trends',
    'sb_search',
    'elasticsearch',
    'textblob',
)

TEST_RUNNER = 'django.test.runner.DiscoverRunner'

ACCOUNT_AUTHENTICATION_METHOD = "email"
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = "optional"
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_SIGNUP_PASSWORD_VERIFICATION = False

SERVER_EMAIL = "service@sagebrew.com"
DEFAULT_FROM_EMAIL = "service@sagebrew.com"

EMAIL_BACKEND = "sgbackend.SendGridBackend"
SENDGRID_USER = "bleib1dj"
SENDGRID_PASSWORD = "wp*D8S@kRnc:6pA"

LOGIN_URL = '/accounts/login/'
LOGOUT_URL = '/accounts/logout/'

ANONYMOUS_USER_ID = -1

LOGIN_REDIRECT_URL = '/registration/profile_information/'
EMAIL_USE_TLS = True
#CSRF_COOKIE_HTTPONLY = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
ADMIN_HONEYPOT_EMAIL_ADMINS = False
SECURE_FRAME_DENY = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
APPEND_SLASH = True
OAUTH_SINGLE_ACCESS_TOKEN = False
OAUTH_ENFORCE_SECURE = True
OAUTH_EXPIRE_DELTA = timedelta(days=30, minutes=0, seconds=0)
OAUTH_EXPIRE_DELTA_PUBLIC = timedelta(days=30, minutes=0, seconds=0)
OAUTH_DELETE_EXPIRED = True

#SESSION_ENGINE = 'django.contrib.sessions.backends.cache'

CELERY_DISABLE_RATE_LIMITS = True
CELERY_ACCEPT_CONTENT = ['pickle', 'json']
BROKER_URL = 'amqp://sagebrew:this_is_the_sagebrew_password@localhost:5672//'
CELERY_RESULT_BACKEND = 'redis://127.0.0.1:6379/0'
CELERYBEAT_SCHEDULER = "djcelery.schedulers.DatabaseScheduler"
CELERY_IGNORE_RESULT = False

CELERYBEAT_SCHEDULE = {
    'empty-garbage-can-minute': {
        'task': 'sb_garbage.tasks.empty_garbage_can',
        'schedule': timedelta(minutes=30),
    }
}
CELERY_TIMEZONE = 'UTC'

BOMBERMAN_API_KEY = environ.get("BOMBERMAN_API_KEY",
                                '6a224aea0ecb3601ae9197c5762aef56')

LOG_TOKEN = environ.get("LOG_TOKEN", "4befe913-b753-4823-a844-193a41779000")

ALCHEMY_API_KEY = '9a65358c4596c05991a406c039281504a0d26bce'

CSV_FILES = '%s/csv_content/' % PROJECT_DIR

TEMP_FILES = '%s/temp_files/' % PROJECT_DIR
if not path.exists(TEMP_FILES):
    makedirs(TEMP_FILES)

import djcelery

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
    'flag_as_other': -10, 'answered': 50, 'starred': 150, 'seen_search': 5,
    'seen_page': 20
}


djcelery.setup_loader()

# TODO When doing load testing and beta testing ensure that LOGGING of DB is on
# and at w/e level we need to check response times. We might be able to
# determine it from new relic but we should check into that prior to moving
# forward