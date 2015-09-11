from __future__ import absolute_import

from os import environ, path, makedirs
from unipath import Path
import multiprocessing
from celery.schedules import crontab
from logentries import LogentriesHandler
import logging

PROJECT_DIR = Path(__file__).ancestor(3)
REPO_DIR = Path(__file__).ancestor(4)

DEBUG = False

ADMINS = (
    ('Devon Bleibtrey', 'devon@sagebrew.com'),
    ('Tyler Wiersing', 'tyler@sagebrew.com')
)
worker_count = (multiprocessing.cpu_count() * 2) + 2
if worker_count > 12 and environ.get("CIRCLECI", "false").lower() == "true":
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
    '%s/sb_campaigns/static/' % PROJECT_DIR,
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
    '%s/sb_updates/static/' % PROJECT_DIR,

)

HELP_DOCS_PATH = "%s/help_center/rendered_docs/" % PROJECT_DIR

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    # 'django.contrib.staticfiles.finders.DefaultStorageFinder',
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

TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': (
        # Put strings here, like "/home/html/django_templates"
        # or "C:/www/django/templates".
        # Always use forward slashes, even on Windows.
        # Don't forget to use absolute paths, not relative paths.
        '%s/help_center/templates/' % PROJECT_DIR,
        '%s/plebs/templates/' % PROJECT_DIR,
        '%s/sagebrew/templates/' % PROJECT_DIR,
        '%s/sb_solutions/templates/' % PROJECT_DIR,
        '%s/sb_badges/templates/' % PROJECT_DIR,
        '%s/sb_campaigns/templates/' % PROJECT_DIR,
        '%s/sb_comments/templates/' % PROJECT_DIR,
        '%s/sb_council/templates' % PROJECT_DIR,
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
        '%s/sb_uploads/templates/' % PROJECT_DIR
    ),
    'OPTIONS': {
        'loaders': [
            ('django.template.loaders.cached.Loader', [
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
            ]),
        ],
        'context_processors': [
            "django.contrib.auth.context_processors.auth",
            "django.core.context_processors.request",
            "django.core.context_processors.debug",
            "django.core.context_processors.i18n",
            "django.core.context_processors.media",
            "django.core.context_processors.static",
            "django.core.context_processors.tz",
            "django.contrib.messages.context_processors.messages",
            "plebs.context_processors.request_profile",
        ],
        'allowed_include_roots': [HELP_DOCS_PATH,],
    },
}]


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
    'django.contrib.sitemaps',
    'django_ses',
    'rest_framework',
    'rest_framework.authtoken',
    'oauth2_provider',
    'corsheaders',
    'storages',
    'localflavor',
    'clear_cache',
    'plebs',
    'api',
    'govtrack',
    'neomodel',
    "opbeat.contrib.django",
    'sb_solutions',
    'sb_badges',
    'sb_base',
    'sb_campaigns',
    'sb_comments',
    'sb_council',
    'sb_docstore',
    'sb_donations',
    'sb_flags',
    'sb_locations',
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
OAUTH_CLIENT_ID_CRED_PUBLIC = environ.get("OAUTH_CLIENT_ID_CRED_PUBLIC", '')
OAUTH_CLIENT_SECRET_CRED_PUBLIC = environ.get(
    "OAUTH_CLIENT_SECRET_CRED_PUBLIC", '')

DYNAMO_IP = environ.get("DYNAMO_IP", None)

EMAIL_BACKEND = 'django_ses.SESBackend'

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': environ.get("CACHE_LOCATION", "127.0.0.1:11211"),
        'TIMEOUT': 172800,
        'OPTIONS': {
            'MAX_ENTRIES': 2500
        }
    }
}

CELERYBEAT_SCHEDULE = {
    'check-closed-reputation-changes': {
        'task': 'sb_council.tasks.check_closed_reputation_changes_task',
        'schedule': crontab(minute=0, hour=3),
        'args': ()
    }
}

CELERY_TIMEZONE = 'UTC'
OPBEAT = {
    "ORGANIZATION_ID": environ.get("OPBEAT_ORG_ID", ""),
    "APP_ID": environ.get("OPBEAT_APP_ID", ""),
    "SECRET_TOKEN": environ.get("OPBEAT_SECRET_TOKEN", ""),
    'PROCESSORS': (
        'opbeat.processors.SanitizePasswordsProcessor',
    ),
}

CSV_FILES = '%s/csv_content/' % PROJECT_DIR
YAML_FILES = '%s/yaml_content/' % PROJECT_DIR

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
    ("quests", ["campaign", "politicalcampaign"])
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
    ('coperator\nge\np0\n.', '>='),
    ('coperator\nnot_\np0\n.', 'not'),
    ('coperator\nis_not\np0\n.', 'is_not'),
    ('coperator\nis_\np0\n.', 'is'),
    ('coperator\ntruth\np0\n.', 'truth')
]

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

CORS_ORIGIN_ALLOW_ALL = True

EXPLICIT_STIES = ['xvideos.com', 'xhamster.com', 'pornhub.com', 'xnxx.com',
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