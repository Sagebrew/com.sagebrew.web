from development import *
from os import environ, path, makedirs

environ['HTTPS'] = "off"

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    #'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    #'djangosecure.middleware.SecurityMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    #'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    #'djangosecure',
    'django_admin_bootstrapped',
    'django.contrib.admin',
    'south',
    'haystack',
    'djcelery',
    'rest_framework',
    'admin_honeypot',
    'provider',
    'provider.oauth2',
    'storages',
    'localflavor',
    'crispy_forms',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.facebook',
    'photologue',
    'sortedm2m',
    'guardian',
    'address',
    'plebs',
    'notifications',
    'user_profiles',
    'api',
    'govtrack',
    'neomodel',
    'sb_registration',
    'sb_comments',
    'sb_posts',
)


LOGIN_REDIRECT_URL = '/registration/profile_information/'
EMAIL_USE_TLS = True
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
ADMIN_HONEYPOT_EMAIL_ADMINS = False
SECURE_FRAME_DENY = False
SECURE_CONTENT_TYPE_NOSNIFF = False
SECURE_BROWSER_XSS_FILTER = False
SECURE_PROXY_SSL_HEADER = ()
OAUTH_ENFORCE_SECURE = False