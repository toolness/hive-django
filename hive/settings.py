"""
Django settings for hive project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import sys
import urlparse
import dj_database_url

from .settings_utils import set_default_env, set_default_db, \
                            parse_email_backend_url, \
                            parse_secure_proxy_ssl_header, \
                            is_running_test_suite

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
path = lambda *parts: os.path.join(BASE_DIR, *parts)

if os.path.basename(sys.argv[0]) == 'manage.py' or 'DEBUG' in os.environ:
    # Quick-start development settings - unsuitable for production
    # See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/
    set_default_env(
        SECRET_KEY='development mode',
        DEBUG='indeed',
        # TODO: Support any alternative port passed-in from the command-line.
        PORT='8000',
        # TODO: Set ORIGIN to include any passed-in IP address.
        EMAIL_BACKEND_URL='console:',
    )

if 'SECURE_PROXY_SSL_HEADER' in os.environ:
    SECURE_PROXY_SSL_HEADER = parse_secure_proxy_ssl_header(
        os.environ['SECURE_PROXY_SSL_HEADER']
    )

if 'DEFAULT_FROM_EMAIL' in os.environ:
    DEFAULT_FROM_EMAIL = SERVER_EMAIL = os.environ['DEFAULT_FROM_EMAIL']

if 'ADMIN_EMAIL' in os.environ:
    ADMINS = (('Administrator', os.environ['ADMIN_EMAIL']),)

GA_TRACKING_ID = os.environ.get('GA_TRACKING_ID')

if GA_TRACKING_ID:
    GA_HOSTNAME = os.environ['GA_HOSTNAME']

MINIGROUP_DIGESTIF_USERPASS = os.environ.get('MINIGROUP_DIGESTIF_USERPASS')
SECRET_KEY = os.environ['SECRET_KEY']
DEBUG = TEMPLATE_DEBUG = 'DEBUG' in os.environ
PORT = int(os.environ['PORT'])
DISCOURSE_SSO_SECRET = os.environ.get('DISCOURSE_SSO_SECRET')
DISCOURSE_SSO_ORIGIN = os.environ.get('DISCOURSE_SSO_ORIGIN')

if DEBUG: set_default_env(ORIGIN='http://localhost:%d' % PORT)

set_default_db('sqlite:///%s' % path('db.sqlite3'))

globals().update(parse_email_backend_url(os.environ['EMAIL_BACKEND_URL']))

ORIGIN = os.environ['ORIGIN']

ALLOWED_HOSTS = [urlparse.urlparse(ORIGIN).hostname]

# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.admindocs',
    'django.contrib.flatpages',
    'crispy_forms',
    'registration',
    'directory',
    'mentoring',
    'cityblogs',
) + EMAIL_BACKEND_INSTALLED_APPS

if MINIGROUP_DIGESTIF_USERPASS or is_running_test_suite():
    INSTALLED_APPS += ('minigroup_digestif',)

if DISCOURSE_SSO_SECRET or is_running_test_suite():
    INSTALLED_APPS += ('discourse_sso',)

MIDDLEWARE_CLASSES = (
    'hive.ssl.RedirectToHttpsMiddleware',
    'hive.ssl.HstsMiddleware',
    'csp.middleware.CSPMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.core.context_processors.tz",
    "django.core.context_processors.request",
    "django.contrib.messages.context_processors.messages",
    "hive.context_processors.origin",
    "hive.context_processors.site",
    "discourse_sso.context_processors.discourse_sso_origin",
)

if GA_TRACKING_ID:
    TEMPLATE_CONTEXT_PROCESSORS += ('hive.context_processors.ga',)

ROOT_URLCONF = 'hive.urls'

WSGI_APPLICATION = 'hive.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': dj_database_url.config()
}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

CSP_IMG_SRC = ('*')

CSP_SCRIPT_SRC = ("'self'",)

if GA_TRACKING_ID:
    CSP_SCRIPT_SRC += ('http://www.google-analytics.com',
                       'https://www.google-analytics.com')

CSP_FONT_SRC = ("'self'", 'http://themes.googleusercontent.com',
                'https://themes.googleusercontent.com')

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'

STATIC_ROOT = path('staticfiles')

STATICFILES_DIRS = (
    path('hive', 'static'),
)

ACCOUNT_ACTIVATION_DAYS = 3

TEMPLATE_DIRS = (
    path('hive', 'templates'),
)

SITE_ID = int(os.environ.get('SITE_ID', '1'))

LOGIN_URL = 'login'

LOGOUT_URL = 'logout'

LOGIN_REDIRECT_URL = 'home'

CRISPY_TEMPLATE_PACK = 'bootstrap3'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'stream': sys.stdout
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'include_html': False,
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['console', 'mail_admins'],
            'level': 'ERROR'
        }
    }
}

ABSOLUTE_URL_OVERRIDES = {
    'auth.user': lambda u: '/users/%s/' % u.username
}

if is_running_test_suite():
    PASSWORD_HASHERS = (
        'django.contrib.auth.hashers.MD5PasswordHasher',
    )
    SITE_ID = 1
