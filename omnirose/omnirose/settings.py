"""
Django settings for omnirose project.

Generated by 'django-admin startproject' using Django 1.8.1.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import local_settings

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_HOST = 'omnirose.com'
BASE_URL = 'http://www.' + BASE_HOST


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = local_settings.SECRET_KEY

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = local_settings.DEBUG

ALLOWED_HOSTS = [
    '.' + BASE_HOST,
]

AUTH_USER_MODEL = "accounts.User"
LOGIN_REDIRECT_URL = '/'
LOGIN_URL = '/accounts/enter/'

# Application definition

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'template_email',
    'bootstrapform',

    'omnirose',
    'accounts',
    'curve',
    'outputs',
    'swing',

    # Last so that the registration templates don't override those in accounts
    'django.contrib.admin',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
)

ROOT_URLCONF = 'omnirose.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'debug': local_settings.DEBUG,
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django_settings_export.settings_export',
            ],
        },
    },
]

WSGI_APPLICATION = 'omnirose.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME':     local_settings.DATABASE_NAME,
        'USER':     local_settings.DATABASE_USER,
        'PASSWORD': local_settings.DATABASE_PASSWORD,
    }
}

PASSWORD_HASHERS = (
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
)

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Security related
X_FRAME_OPTIONS = 'DENY'


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'collected_static')
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)

# Email (hence Postmark) related
EMAIL_BACKEND = 'postmark.django_backend.EmailBackend'

HELLO_EMAIL_ADDRESS  = 'hello@omnirose.com'
DEFAULT_FROM_EMAIL   = HELLO_EMAIL_ADDRESS
SERVER_EMAIL         = HELLO_EMAIL_ADDRESS

POSTMARK_API_KEY     = local_settings.POSTMARK_API_KEY
POSTMARK_TEST_MODE   = local_settings.POSTMARK_TEST_MODE
POSTMARK_SENDER      = HELLO_EMAIL_ADDRESS
POSTMARK_TRACK_OPENS = True

ADMINS = local_settings.ADMINS

# Google Analytics
GOOGLE_ANALYTICS_TRACKING_CODE = local_settings.GOOGLE_ANALYTICS_TRACKING_CODE

# Stripe related
STRIPE_SECRET_KEY=local_settings.STRIPE_SECRET_KEY
STRIPE_PUBLIC_KEY=local_settings.STRIPE_PUBLIC_KEY

# Rose purchasing
UNLOCK_CURVE_CURRENCY = "USD"
UNLOCK_CURVE_PRICE    = 800 # $8
UNLOCK_CURVE_FORMATTED_PRICE = "$8"


SETTINGS_EXPORT = [
    'BASE_URL',
    'HELLO_EMAIL_ADDRESS',
    'GOOGLE_ANALYTICS_TRACKING_CODE',
    'STRIPE_PUBLIC_KEY',
    'UNLOCK_CURVE_CURRENCY',
    'UNLOCK_CURVE_PRICE',
    'UNLOCK_CURVE_FORMATTED_PRICE',
]

