from __future__ import absolute_import

from os import environ, path, makedirs
from unipath import Path
from datetime import timedelta
import multiprocessing


PROJECT_DIR = Path(__file__).ancestor(3)
REPO_DIR = Path(__file__).ancestor(4)


DEBUG = False
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Devon Bleibtrey', 'devon@sagebrew.com'),
)
worker_count = (multiprocessing.cpu_count() *2) + 1
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
    '%s/sagebrew/static/' % PROJECT_DIR,
    '%s/plebs/static/' % PROJECT_DIR,
    '%s/sb_registration/static/' % PROJECT_DIR,
    #'%s/sb_comments/static/' % PROJECT_DIR,
    '%s/sb_posts/static/' % PROJECT_DIR,
    '%s/sb_relationships/static/' % PROJECT_DIR,
    '%s/sb_questions/static/' % PROJECT_DIR,
    '%s/sb_answers/static/' % PROJECT_DIR,
    '%s/sb_search/static/' % PROJECT_DIR,
    '%s/sb_tag/static/' % PROJECT_DIR,
    '%s/sb_flags/static/' % PROJECT_DIR,
    '%s/sb_votes/static/' % PROJECT_DIR,
    '%s/sb_edits/static/' % PROJECT_DIR
)

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
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    #'django.contrib.auth.middleware.SessionAuthenticationMiddleware'
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
)

AUTHENTICATION_BACKENDS = (
    "django.contrib.auth.backends.ModelBackend",
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
    '%s/help_center/templates/' % PROJECT_DIR,
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
    'rest_framework',
    'admin_honeypot',
    'provider',
    'provider.oauth2',
    'storages',
    'localflavor',
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
    'sb_tag',
    'sb_questions',
    'sb_answers',
    'sb_trends',
    'sb_search',
    'sb_votes',
    'sb_flags',
    'sb_edits',
    'sb_deletes',
    'elasticsearch',
    'textblob',
)
TEST_RUNNER = 'django.test.runner.DiscoverRunner'

EMAIL_VERIFICATION_TIMEOUT_DAYS = 1

SERVER_EMAIL = "service@sagebrew.com"
DEFAULT_FROM_EMAIL = "service@sagebrew.com"

LOGIN_URL = '/login/'
LOGOUT_URL = '/logout/'

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

CELERY_DISABLE_RATE_LIMITS = True
CELERY_ACCEPT_CONTENT = ['pickle', 'json']
CELERY_ALWAYS_EAGER = False
CELERY_IGNORE_RESULT = False
# AWS_S3_SECURE_URLS = True
AWS_STORAGE_BUCKET_NAME = environ.get("AWS_S3_BUCKET")

AWS_ACCESS_KEY_ID = environ.get("AWS_ACCESS_KEY_ID", "")
AWS_SECRET_ACCESS_KEY = environ.get("AWS_SECRET_ACCESS_KEY", "")
AWS_PROFILE_PICTURE_FOLDER_NAME = 'profile_pictures'
SECRET_KEY = environ.get("APPLICATION_SECRET_KEY", "")
BOMBERMAN_API_KEY = environ.get("BOMBERMAN_API_KEY", "")
LOG_TOKEN = environ.get("LOG_TOKEN", "")
ALCHEMY_API_KEY = environ.get("ALCHEMY_API_KEY", '')
ADDRESS_VALIDATION_ID = environ.get("ADDRESS_VALIDATION_ID", '')
ADDRESS_VALIDATION_TOKEN = environ.get("ADDRESS_VALIDATION_TOKEN", '')


CELERYBEAT_SCHEDULE = {
    'empty-garbage-can-minute': {
        'task': 'sb_garbage.tasks.empty_garbage_can',
        'schedule': timedelta(minutes=30),
    }
}
CELERY_TIMEZONE = 'UTC'


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


# TODO revisit search modifiers
OBJECT_SEARCH_MODIFIERS = {
    'post': 10, 'comment_on': 5, 'upvote': 3, 'downvote': -3,
    'time': -1, 'proximity_to_you': 10, 'proximity_to_interest': 10,
    'share': 7, 'flag_as_inappropriate': -5, 'flag_as_spam': -100,
    'flag_as_other': -10, 'answered': 50, 'starred': 150, 'seen_search': 5,
    'seen_page': 20
}

BASE_TAGS = ["fiscal", "foreign_policy", "social", "education", "science",
             "environment", "drugs", "agriculture", "defense", "energy",
             "health", "space"]


KNOWN_TYPES = [
    ("01bb301a-644f-11e4-9ad9-080027242395", "sb_posts.neo_models.SBPost"),
    ("02241aee-644f-11e4-9ad9-080027242395", "sb_answers.neo_models.SBAnswer"),
    ("0274a216-644f-11e4-9ad9-080027242395", "sb_questions.neo_models.SBQuestion"),
    ("02ba1c88-644f-11e4-9ad9-080027242395", "sb_comments.neo_models.SBComment")
]

# TODO When doing load testing and beta testing ensure that LOGGING of DB is on
# and at w/e level we need to check response times. We might be able to
# determine it from new relic but we should check into that prior to moving
# forward