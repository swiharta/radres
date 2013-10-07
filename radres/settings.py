import os.path
# import posixpath

SITE_NAME = "RadRes.Info"

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

DEBUG = False
TEMPLATE_DEBUG = DEBUG
COMPRESS_ENABLED = True
COMPRESS_OFFLINE = False

COMPRESS_PRECOMPILERS = (
  ('text/coffeescript', 'coffee --compile --stdio'),
)

COMPRESS_CSS_FILTERS = (
  'compressor.filters.css_default.CssAbsoluteFilter',
)

#COMPRESS_JS_FILTERS = ['compressor.filters.jsmin.SlimItFilter']

# Make this unique, and don't share it with anybody.
try:
  from secret_key import SECRET_KEY
except ImportError:
  from django.utils.crypto import get_random_string
  SETTINGS_DIR=os.path.abspath(os.path.dirname(__file__))
  f = open(os.path.join(SETTINGS_DIR, 'secret_key.py'), 'w')
  chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
  f.write('SECRET_KEY = "' + get_random_string(50, chars) + '"')
  f.close()
  from secret_key import SECRET_KEY

LOGIN_EXEMPT_URLS = (
  r'^$',
  r'^account/.+',
#  r'^account/signup',
  r'^fluoro',
  r'^mri-intensity',
  r'^calendar/.+',
  r'^site_media/.+',
  r'^favicon.ico',
  r'^404.html',
  r'^500.html',
)

INTERNAL_IPS = [
  "127.0.0.1",
]

ADMINS = [
  ("Your Name", "email@address.com"),
]

MANAGERS = ADMINS

DJANGO_MODERATION_MODERATORS = [
  "email@address.com",
]

#CACHE_BACKEND = 'memcached://unix:59135/home/swihart/memcached.sock'
# CACHE_BACKEND = 'memcached://127.0.0.1:59135'

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:59135', # change to the correct port number for your memcached
    }
}

# for django-memcached stats page
DJANGO_MEMCACHED_REQUIRE_STAFF = True

SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'

EMAIL_HOST = 'smtp.webfaction.com'
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
DEFAULT_FROM_EMAIL = ''
SERVER_EMAIL = ''

DATABASES = {
  "default": {
    "ENGINE": "django.db.backends.postgresql_psycopg2",
    # Add "postgresql_psycopg2", "postgresql", "mysql", "sqlite3" or "oracle".
    "NAME": "", # Or path to database file if using sqlite3.
    "USER": "", # Not used with sqlite3.
    "PASSWORD": "", # Not used with sqlite3.
    "HOST": "", # Set to empty string for localhost. Not used with sqlite3.
    "PORT": "", # Set to empty string for default. Not used with sqlite3.
  }
}

USE_TZ = True
TIME_ZONE = "US/Eastern"
LANGUAGE_CODE = "en-us"
SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

MEDIA_ROOT = os.path.join(PROJECT_ROOT, "site_media", "media")
MEDIA_URL = "/site_media/media/"

STATIC_ROOT = os.path.join(PROJECT_ROOT, "site_media", "static")
STATIC_URL = "/site_media/static/"

STATICFILES_FINDERS = (
  'django.contrib.staticfiles.finders.FileSystemFinder',
  'django.contrib.staticfiles.finders.AppDirectoriesFinder',
  'compressor.finders.CompressorFinder',
  )

# Additional directories which hold static files
STATICFILES_DIRS = [
  os.path.join(PROJECT_ROOT, "media"),
#  ADMIN_MEDIA_ROOT,
  ]

TEMPLATE_LOADERS = (
    ('django.template.loaders.cached.Loader', (
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
    )),
)

MIDDLEWARE_CLASSES = [
  "django.middleware.common.CommonMiddleware",
  "django.contrib.sessions.middleware.SessionMiddleware",
  "django.middleware.csrf.CsrfViewMiddleware",
  "django.contrib.auth.middleware.AuthenticationMiddleware",
  "django.contrib.messages.middleware.MessageMiddleware",
  "django.middleware.doc.XViewMiddleware",
  "debug_toolbar.middleware.DebugToolbarMiddleware",
  # "account.middleware.LocaleMiddleware",
  # "account.middleware.TimezoneMiddleware",
  "radres.middleware.LoginRequiredMiddleware", # http://djangosnippets.org/snippets/1179/
]

ROOT_URLCONF = "radres.urls"

TEMPLATE_DIRS = [
  os.path.join(PROJECT_ROOT, "templates"),
#  os.path.join(PINAX_ROOT, "templates", PINAX_THEME),
  ]

TEMPLATE_CONTEXT_PROCESSORS = [
#  "django.core.context_processors.auth",
  "django.contrib.auth.context_processors.auth",
  "django.core.context_processors.debug",
  "django.core.context_processors.i18n",
  "django.core.context_processors.media",
  'django.core.context_processors.static',
  "django.core.context_processors.request",
  "django.contrib.messages.context_processors.messages",

  "account.context_processors.account",
  "radres.context_processors.resolve_url_name",
]

INSTALLED_APPS = [
  # Django
  "django.contrib.admin",
  "django.contrib.auth",
  "django.contrib.contenttypes",
  "django.contrib.sessions",
  "django.contrib.sites",
  "django.contrib.messages",
  "django.contrib.humanize",
  "django.contrib.markup",
  "django.contrib.staticfiles",

  'raven.contrib.django',
  "crispy_forms",
  "debug_toolbar",
  "gunicorn",
  "south",
  "ajax_select",
  "imagekit",
  "django_extensions",
  "mptt",
  "taggit",
  'compressor',
  'django_memcached',
  # 'django_monitor',
#  'moderation',
  'django_cal',
  'tastypie', # using git package
  'backbone_tastypie',
  "django_forms_bootstrap",

  # project
  "account",
  "polls",
  "fixture_magic",
  "radres", # loads site-wide templatetags
  "radcal",
  "radprofile",
  "questions",
  "mri",
  "taxonomy",
  ]

FIXTURE_DIRS = [
  os.path.join(PROJECT_ROOT, "fixtures"),
  ]

MESSAGE_STORAGE = "django.contrib.messages.storage.session.SessionStorage"

ABSOLUTE_URL_OVERRIDES = {
  "auth.user": lambda o: "/profiles/profile/%s/" % o.username,
  }

AUTH_PROFILE_MODULE = "radprofile.Profile"

ACCOUNT_OPEN_SIGNUP = True
ACCOUNT_REQUIRED_EMAIL = False
ACCOUNT_EMAIL_VERIFICATION = False
ACCOUNT_EMAIL_AUTHENTICATION = False
ACCOUNT_EMAIL_UNIQUE = False

AUTHENTICATION_BACKENDS = [
  "account.auth_backends.UsernameAuthenticationBackend",
  ]

LOGIN_URL = "/account/login/" # @@@ any way this can be a url name?
ACCOUNT_LOGOUT_REDIRECT_URL = "/"

EMAIL_CONFIRMATION_DAYS = 365

ugettext = lambda s: s
LANGUAGES = [
  ("en", u"English"),
]

AJAX_LOOKUP_CHANNELS = {
  "user-select": ('radprofile.lookups', 'UserLookup'),
  }

AJAX_SELECT_BOOTSTRAP = True
AJAX_SELECT_INLINES = 'staticfiles'

DEBUG_TOOLBAR_CONFIG = {
  "INTERCEPT_REDIRECTS": False,
  }

# LOGGING = {
  # 'version': 1,
  # 'disable_existing_loggers': True,
  # 'root': {
    # 'level': 'WARNING',
    # 'handlers': ['sentry'],
    # },
  # 'formatters': {
    # 'verbose': {
      # 'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
    # },
    # },
  # 'handlers': {
    # 'sentry': {
      # 'level': 'ERROR',
      # 'class': 'raven.contrib.django.raven_compat.handlers.SentryHandler',
      # },
    # 'console': {
      # 'level': 'DEBUG',
      # 'class': 'logging.StreamHandler',
      # 'formatter': 'verbose'
    # }
  # },
  # 'loggers': {
    # 'django.db.backends': {
      # 'level': 'ERROR',
      # 'handlers': ['console'],
      # 'propagate': False,
      # },
    # 'raven': {
      # 'level': 'DEBUG',
      # 'handlers': ['console'],
      # 'propagate': False,
      # },
    # 'sentry.errors': {
      # 'level': 'DEBUG',
      # 'handlers': ['console'],
      # 'propagate': False,
      # },
    # },
  # }

# local_settings.py can be used to override environment-specific settings
# like database and email that differ between development and production.
try:
  from local_settings import *
except ImportError:
  pass
