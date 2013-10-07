from settings import MEDIA_ROOT, STATICFILES_DIRS, INSTALLED_APPS

DEBUG = True
TEMPLATE_DEBUG = DEBUG
SERVE_MEDIA = True
COMPRESS_ENABLED = False
COMPRESS_OFFLINE = False # leaving this False makes it re-compress if any changes occur

COMPRESS_PRECOMPILERS = (
    ('text/coffeescript', 'coffee --compile --stdio'),
#    ('text/x-sass', 'sass {infile} {outfile}'),
)

TEMPLATE_LOADERS = [ # no cached loader in development
    "django.template.loaders.filesystem.Loader",
    "django.template.loaders.app_directories.Loader"
]

ACCOUNT_OPEN_SIGNUP = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'dev.db',                      # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

#EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
#EMAIL_HOST = ''
#EMAIL_PORT = None
EMAIL_HOST = 'localhost'
EMAIL_PORT = 1025
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
DEFAULT_FROM_EMAIL = 'testing@example.com'

# to start python smtp development server from command line:
# python -m smtpd -n -c DebuggingServer localhost:1025

CACHES = {'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
#CACHES = {'default': {'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
                      'OPTIONS': {
                          'MAX_ENTRIES': 1000
                      }}
}

INSTALLED_APPS += [
'devserver',
]