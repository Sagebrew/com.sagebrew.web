from __future__ import absolute_import

from os import environ, path, makedirs
from unipath import Path
from datetime import timedelta
import multiprocessing
from logentries import LogentriesHandler
import logging

PROJECT_DIR = Path(__file__).ancestor(3)
REPO_DIR = Path(__file__).ancestor(4)

DEBUG = False
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Devon Bleibtrey', 'devon@sagebrew.com'),
)
worker_count = (multiprocessing.cpu_count() * 2) + 1
if worker_count > 12 and environ.get("CIRCLECI", False):
    worker_count = 12
environ['WEB_WORKER_COUNT'] = str(worker_count)
environ['PROJECT_PATH'] = PROJECT_DIR

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

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/var/www/example.com/static/"

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    '%s/help_center/static/' % PROJECT_DIR,
    '%s/sagebrew/static/' % PROJECT_DIR,
    '%s/plebs/static/' % PROJECT_DIR,
    '%s/sb_solutions/static/' % PROJECT_DIR,
    '%s/sb_notifications/static/' % PROJECT_DIR,
    '%s/sb_privileges/static/' % PROJECT_DIR,
    '%s/sb_posts/static/' % PROJECT_DIR,
    '%s/sb_questions/static/' % PROJECT_DIR,
    '%s/sb_registration/static/' % PROJECT_DIR,
    '%s/sb_public_official/static/' % PROJECT_DIR,
    '%s/sb_search/static/' % PROJECT_DIR,
    '%s/sb_tags/static/' % PROJECT_DIR,
    '%s/sb_uploads/static/' % PROJECT_DIR,

)

HELP_DOCS_PATH = "%s/help_center/rendered_docs/" % PROJECT_DIR
ALLOWED_INCLUDE_ROOTS = (HELP_DOCS_PATH,)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    # 'django.contrib.staticfiles.finders.DefaultStorageFinder',
)


# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    # 'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'opbeat.contrib.django.middleware.OpbeatAPMMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'djangosecure.middleware.SecurityMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'oauth2_provider.middleware.OAuth2TokenMiddleware',
)

ROOT_URLCONF = 'sagebrew.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'sagebrew.wsgi.application'

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.request",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.core.context_processors.tz",
    "django.contrib.messages.context_processors.messages",
    "plebs.context_processors.request_profile",
)


TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates"
    # or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    '%s/help_center/templates/' % PROJECT_DIR,
    '%s/plebs/templates/' % PROJECT_DIR,
    '%s/sagebrew/templates/' % PROJECT_DIR,
    '%s/sb_solutions/templates/' % PROJECT_DIR,
    '%s/sb_badges/templates/' % PROJECT_DIR,
    '%s/sb_comments/templates/' % PROJECT_DIR,
    '%s/sb_flag/templates/' % PROJECT_DIR,
    '%s/sb_notifications/templates/' % PROJECT_DIR,
    '%s/sb_posts/templates/' % PROJECT_DIR,
    '%s/sb_privileges/templates/' % PROJECT_DIR,
    '%s/sb_public_official/templates/' % PROJECT_DIR,
    '%s/sb_questions/templates/' % PROJECT_DIR,
    '%s/sb_registration/templates/' % PROJECT_DIR,
    '%s/sb_requirements/templates/' % PROJECT_DIR,
    '%s/sb_search/templates/' % PROJECT_DIR,
    '%s/sb_tags/templates/' % PROJECT_DIR,
)


INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'djangosecure',
    'django_admin_bootstrapped',
    'django.contrib.admin',
    'django_ses',
    'rest_framework',
    'rest_framework.authtoken',
    'admin_honeypot',
    'oauth2_provider',
    'corsheaders',
    'storages',
    'localflavor',
    'plebs',
    'api',
    'govtrack',
    'neomodel',
    "opbeat.contrib.django",
    'sb_solutions',
    'sb_badges',
    'sb_base',
    'sb_comments',
    'sb_docstore',
    'sb_flags',
    'sb_notifications',
    'sb_posts',
    'sb_privileges',
    'sb_public_official',
    'sb_questions',
    'sb_registration',
    'sb_requirements',
    'sb_search',
    'sb_stats',
    'sb_tags',
    'sb_uploads',
    'sb_votes',
    'sb_wall',
    'sb_oauth',
    'elasticsearch',
    'textblob',
    'help_center'
)

TEST_RUNNER = 'django.test.runner.DiscoverRunner'

EMAIL_VERIFICATION_TIMEOUT_DAYS = 1


SERVER_EMAIL = "support@sagebrew.com"
DEFAULT_FROM_EMAIL = "support@sagebrew.com"

LOGIN_URL = '/login/'
LOGOUT_URL = '/logout/'

ANONYMOUS_USER_ID = -1
OAUTH2_PROVIDER_APPLICATION_MODEL = 'sb_oauth.SBApplication'
OAUTH2_PROVIDER = {
    'APPLICATION_MODEL': 'sb_oauth.SBApplication',
}
LOGIN_REDIRECT_URL = '/registration/profile_information/'
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

CELERY_DISABLE_RATE_LIMITS = True
CELERY_ACCEPT_CONTENT = ['pickle', 'json']
CELERY_ALWAYS_EAGER = False

# AWS_S3_SECURE_URLS = True
AWS_STORAGE_BUCKET_NAME = environ.get("AWS_S3_BUCKET")

AWS_ACCESS_KEY_ID = environ.get("AWS_ACCESS_KEY_ID", "")
AWS_SECRET_ACCESS_KEY = environ.get("AWS_SECRET_ACCESS_KEY", "")
AWS_PROFILE_PICTURE_FOLDER_NAME = 'profile_pictures'
AWS_UPLOAD_IMAGE_FOLDER_NAME = 'media'
SECRET_KEY = environ.get("APPLICATION_SECRET_KEY", "")
BOMBERMAN_API_KEY = environ.get("BOMBERMAN_API_KEY", "")
LOGENT_TOKEN = environ.get("LOGENT_TOKEN", "")
ALCHEMY_API_KEY = environ.get("ALCHEMY_API_KEY", '')
# Used for server side
ADDRESS_VALIDATION_ID = environ.get("ADDRESS_VALIDATION_ID", '')
ADDRESS_VALIDATION_TOKEN = environ.get("ADDRESS_VALIDATION_TOKEN", '')
# Used for JS
ADDRESS_AUTH_ID = environ.get("ADDRESS_AUTH_ID", '')

STRIPE_PUBLIC_KEY = environ.get("STRIPE_PUBLIC_KEY", '')
STRIPE_SECRET_KEY = environ.get("STRIPE_SECRET_KEY", '')
MASKED_NAME = environ.get("MASKED_NAME", "")
OAUTH_CLIENT_ID = environ.get("OAUTH_CLIENT_ID", '')
OAUTH_CLIENT_SECRET = environ.get("OAUTH_CLIENT_SECRET", "")
OAUTH_CLIENT_ID_CRED = environ.get("OAUTH_CLIENT_ID_CRED", '')
OAUTH_CLIENT_SECRET_CRED = environ.get("OAUTH_CLIENT_SECRET_CRED", "")

DYNAMO_IP = environ.get("DYNAMO_IP", None)

EMAIL_BACKEND = 'django_ses.SESBackend'

CELERY_TIMEZONE = 'UTC'
OPBEAT = {
    "ORGANIZATION_ID": environ.get("OPBEAT_ORG_ID", ""),
    "APP_ID": environ.get("OPBEAT_APP_ID", ""),
    "SECRET_TOKEN": environ.get("OPBEAT_SECRET_TOKEN", "")
}

CSV_FILES = '%s/csv_content/' % PROJECT_DIR

TEMP_FILES = '%s/temp_files/' % PROJECT_DIR
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
    ("sagas", "public_official")
]


BASE_REP_TYPES = [
    ("f2729db2-9da8-11e4-9233-080027242395",
     "sb_public_official.neo_models.USSenator"),
    ("f3aeebe0-9da8-11e4-9233-080027242395",
     "sb_public_official.neo_models.USPresident"),
    ("f46fbcda-9da8-11e4-9233-080027242395",
     "sb_public_official.neo_models.PublicOfficial"),
    ("628c138a-9da9-11e4-9233-080027242395",
     "sb_public_official.neo_models.USHouseRepresentative"),
    ("786dcf40-9da9-11e4-9233-080027242395",
     "sb_public_official.neo_models.Governor")
]

OPERATOR_TYPES = [
    ('coperator\neq\np0\n.', '='),
    ('coperator\nle\np0\n.', '<='),
    ('coperator\ngt\np0\n.', '>'),
    ('coperator\nne\np0\n.', '!='),
    ('coperator\nlt\np0\n.', '<'),
    ('coperator\nge\np0\n.', '>=')
]

NON_SAFE = ["REMOVE", "DELETE", "CREATE", "SET",
            "FOREACH", "MERGE", "MATCH", "START"]

REMOVE_CLASSES = ["SBVersioned", "SBPublicContent", "SBPrivateContent",
                  "VotableContent", "NotificationCapable", "TaggableContent",
                  "SBContent", "Searchable"]

QUERY_OPERATIONS = {
    "eq": "=",
    "le": "<=",
    "lt": "<",
    "ge": ">=",
    "gt": ">",
}

OPERATOR_DICT = {
    'coperator\neq\np0\n.': 'equal to',
    'coperator\nle\np0\n.': 'at most',
    'coperator\ngt\np0\n.': 'more than',
    'coperator\nne\np0\n.': 'not have',
    'coperator\nlt\np0\n.': 'less than',
    'coperator\nge\np0\n.': 'at least'
}

CORS_ORIGIN_ALLOW_ALL = True
