from pathlib import Path
import os
from datetime import timedelta
# Add the Celery beat schedule for periodic tasks
from celery.schedules import crontab

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-a%xmc3o4xm!mc3djsja-z9#b#x8id8v#sr%syn+q0y$knv05=0"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "authentication_app",
    "admin_app",
    "feedback",
    "newsletter",
    "category",
    "data_scrape",
    "raw_food_item",
    "raw_food_price",
    "shopping_list",
    "rest_framework",
    "djoser",
    "rest_framework_simplejwt.token_blacklist",
    "corsheaders",
    "django_pandas",
]
    
AUTH_USER_MODEL = 'authentication_app.UserAccount'

REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated"
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
}

SIMPLE_JWT = {
    "AUTH_HEADER_TYPES": ("JWT",),

    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=1),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=90),
}

MIDDLEWARE = [

    "corsheaders.middleware.CorsMiddleware",

    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "backend.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, 'build')],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "backend.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "agrocost_db",
        "USER": "postgres",
        "PASSWORD": "shen",
        "HOST": "localhost",
    }
}

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'agrocost.info@gmail.com'
EMAIL_HOST_PASSWORD = 'qphb lers wtns jeaj'
EMAIL_USE_TLS = True



CELERY_TIMEZONE = 'Asia/Kathmandu'

# Django's timezone setting
TIME_ZONE = 'Asia/Kathmandu'

# Other Celery settings
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'

CELERY_BEAT_SCHEDULE = {
    'scrape-everyday': {
        'task': 'data_scrape.tasks.run_scraping_script',
        'schedule': crontab(hour=10, minute=46),  # Nepali time 11:00 AM
    },
}


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': 'celery.log',
        },
    },
    'loggers': {
        'celery': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
        },
    },
}



AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


LANGUAGE_CODE = "en-us"

USE_I18N = True

USE_TZ = True



STATIC_URL = "/static/"
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'build/static')
]

STATIC_ROOT = os.path.join(BASE_DIR, 'static')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

DJOSER = {
    'LOGIN_FIELD': 'email',
    'PASSWORD_RESET_CONFIRM_RETYPE': True,
    'USER_CREATE_PASSWORD_RETYPE': True,
    'USERNAME_CHANGED_EMAIL_CONFIRMATION': True,
    'PASSWORD_CHANGED_EMAIL_CONFIRMATION': True,
    'SEND_CONFIRMATION_EMAIL': True,
    'SET_USERNAME_RETYPE': True,
    'SET_PASSWORD_RETYPE': True,
    'PASSWORD_RESET_CONFIRM_URL': 'password/reset/confirm/{uid}/{token}',
    'USERNAME_RESET_CONFIRM_URL': 'email/reset/confirm/{uid}/{token}',
    'ACTIVATION_URL': 'activate/{uid}/{token}',
    'SEND_ACTIVATION_EMAIL': True,
    'SERIALIZERS': {
        'user_create': 'authentication_app.serializers.UserCreateSerializer',
        'user': 'authentication_app.serializers.UserCreateSerializer',
        'user_delete': 'djoser.serializers.UserDeleteSerializer',
    }
}


DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
]

# Use this during development, restrict in production
CORS_ORIGIN_ALLOW_ALL = True  
CORS_ALLOW_CREDENTIALS = True