import os
import dj_database_url
from dotenv import load_dotenv
from datetime import timedelta
from pathlib import Path
import sys
from corsheaders.defaults import default_headers
# Build paths inside the project like this: BASE_DIR / 'subdir'.

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(os.path.join(BASE_DIR, '.env'))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-u-e(&(%d#(e+gj+nel$(-gefvmg$uwr9v747d7c8^&hqo8amh@'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

IS_LOCAL = os.environ.get("IS_LOCAL", "False").strip().lower() == "true"

# print("IS_LOCAL raw:", os.environ.get("IS_LOCAL"))  # Debug line
# print("IS_LOCAL after parse:", IS_LOCAL)            # Debug line

if IS_LOCAL:
    TRAVELLER_DASHBOARD_URL = "http://192.168.68.111:3000/dashboard"
    API_SITE_URL = "http://0.0.0.0:8010"
    ADMIN_ALL_BOOKING_PAGE = "http://192.168.68.111:3010/apps/booking-management/bookings"
else:
    TRAVELLER_DASHBOARD_URL = "https://dreamziarah.com/dashboard"
    API_SITE_URL = "https://api.dreamziarah.com"
    ADMIN_ALL_BOOKING_PAGE = "https://admin.dreamziarah.com/apps/booking-management/bookings"

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # 3rd party
    'corsheaders',
    'rest_framework',
    'drf_spectacular',
    'phonenumber_field',
    'djoser',
    'django_filters',

    #local
    'authentication.apps.AuthenticationConfig',
    'cms.apps.CmsConfig',
    'site_settings.apps.SiteSettingsConfig',
    'support.apps.SupportConfig',
    'tour.apps.TourConfig',
    'payments.apps.PaymentsConfig',
    'scripts.apps.ScriptsConfig',
]	

INSTALLED_APPS += ['sequences.apps.SequencesConfig']

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_currentuser.middleware.ThreadLocalUserMiddleware',
]

# if DEBUG:
#     INSTALLED_APPS += ['silk',]
#     MIDDLEWARE += ['silk.middleware.SilkyMiddleware',]
#     SILKY_PYTHON_PROFILER = True
#     SILKY_PYTHON_PROFILER_BINARY = True
#     SILKY_META = True

ROOT_URLCONF = 'start_project.urls'


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'start_project.wsgi.application'

AUTH_USER_MODEL = 'authentication.User'


# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases


# test live db
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql_psycopg2',
#         'NAME': 'dreamtr_dream_ziarah_DB',
#         'USER': 'dreamtr_user',
#         'PASSWORD':'BBIT@7811',
#         'HOST': 'localhost'
#     }
# }

# SQLite db
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / "db.sqlite3",
    }
}

# test live db
# DATABASES = {
#     'default': dj_database_url.parse(os.getenv("DATABASE_URL"))
# }
# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]
###
CORS_ALLOW_ALL_ORIGINS = True

CORS_ALLOWED_ORIGINS = [
    # "http://localhost:3000",
    # "http://192.168.68.120:3000",
    # "http://192.168.68.111:3000",  # add any IP you're using for frontend
    # "https://dreamziarah.com",

]
# # Optional but useful
# CORS_ALLOW_HEADERS = [
#     "accept",
#     "accept-encoding",
#     "authorization",
#     "content-type",
#     "dnt",
#     "origin",
#     "user-agent",
#     "x-csrftoken",
#     "x-requested-with",
# ]

# SESSION_COOKIE_SAMESITE = 'Lax'
# SESSION_COOKIE_SECURE = not DEBUG
# CSRF_COOKIE_SAMESITE = 'Lax'
# CSRF_COOKIE_SECURE = not DEBUG

AUTHENTICATION_BACKENDS = [
    'authentication.backends.EmailOrUsernameBackend',  # your app name may differ
    'django.contrib.auth.backends.ModelBackend', # keep default as fallback
]
CORS_ALLOW_CREDENTIALS = True

STRIPE_PUBLIC_KEY = os.getenv("STRIPE_PUBLIC_KEY")
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
STRIPE_ENDPOINT_SECRET = os.getenv("STRIPE_ENDPOINT_SECRET")

# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Dhaka'

USE_I18N = True

USE_L10N = True

USE_TZ = True


WHITENOISE_USE_FINDERS = True
CORS_ALLOW_ALL_ORIGINS=True

# for avoiding warning for custom user model (email as username, but email is not globally unique)
SILENCED_SYSTEM_CHECKS = ["auth.W004"]

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/

STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATIC_URL = '/static/'
# STATICFILES_DIRS = [STATIC_DIR]

MEDIA_ROOT = os.path.join(BASE_DIR, 'media') # media files upload directory
MEDIA_URL = '/media/' # media files retrieve directory

# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# if 'loaddata' in sys.argv:
#     EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

if IS_LOCAL:
    # Default (local@dreamziarah.com)
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = 'smtp.titan.email'
    EMAIL_PORT = 587
    EMAIL_HOST_USER = "local@dreamziarah.com"
    EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD_FOR_LOCAL_DREAMZIARAH")
    EMAIL_USE_TLS = True

    DEFAULT_FROM_EMAIL = "local@dreamziarah.com"   # 👈 add this

    # Sales email config (local@dreamziarah.com)
    SALES_EMAIL_CONFIG = {
        "EMAIL_BACKEND" : 'django.core.mail.backends.smtp.EmailBackend',
        "EMAIL_HOST": "smtp.titan.email",
        "EMAIL_PORT": 587,
        "EMAIL_HOST_USER": "local@dreamziarah.com",
        "EMAIL_HOST_PASSWORD": os.getenv("EMAIL_HOST_PASSWORD_FOR_LOCAL_DREAMZIARAH"),
        "EMAIL_USE_TLS": True,
    }

    SALES_FROM_EMAIL = "local@dreamziarah.com"   # 👈 add this
else:
    # Default (noreply)
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = 'smtp.titan.email'
    EMAIL_PORT = 587
    EMAIL_HOST_USER = "noreply@dreamziarah.com"
    EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD_FOR_NO_REPLY")
    EMAIL_USE_TLS = True

    DEFAULT_FROM_EMAIL = "noreply@dreamziarah.com"   # 👈 add this

    # Sales email config (sales@dreamziarah.com)
    SALES_EMAIL_CONFIG = {
        "EMAIL_BACKEND" : 'django.core.mail.backends.smtp.EmailBackend',
        "EMAIL_HOST": "smtp.titan.email",
        "EMAIL_PORT": 587,
        "EMAIL_HOST_USER": "sales@dreamziarah.com",
        "EMAIL_HOST_PASSWORD": os.getenv("EMAIL_HOST_PASSWORD_FOR_ZIARAH"),
        "EMAIL_USE_TLS": True,
    }

    SALES_FROM_EMAIL = "sales@dreamziarah.com"   # 👈 add this


REST_FRAMEWORK = {
  'DEFAULT_AUTHENTICATION_CLASSES': (
    'rest_framework_simplejwt.authentication.JWTAuthentication',
  ),
  'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
  'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.MultiPartParser',
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
    ],
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
    ),
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'ZIARAH',
    'DESCRIPTION': '',
    'VERSION': '1.0.0',
    # OTHER SETTINGS
        # available SwaggerUI configuration parameters
    # https://swagger.io/docs/open-source-tools/swagger-ui/usage/configuration/
    "SWAGGER_UI_SETTINGS": {
        "deepLinking": True,
        "persistAuthorization": True,
        # "displayOperationId": True,
    },
    # available SwaggerUI versions: https://github.com/swagger-api/swagger-ui/releases
    "SWAGGER_UI_DIST": "//unpkg.com/swagger-ui-dist@3.35.1", # default
    # "SWAGGER_UI_FAVICON_HREF": STATIC_URL + "your_company_favicon.png", # default is swagger favicon
        # "APPEND_COMPONENTS": {
        # "securitySchemes": {
        # 		"ApiKeyAuth": {
        # 				"type": "apiKey",
        # 				"in": "header",
        # 				"name": "Authorization"
        # 		}
        # 	}
    # },
    # "SECURITY": [{"ApiKeyAuth": [], }],
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=7),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,

    'ALGORITHM': 'HS256',
    # 'SIGNING_KEY': settings.SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,

    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'USER_AUTHENTICATION_RULE': 'rest_framework_simplejwt.authentication.default_user_authentication_rule',

    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',

    'JTI_CLAIM': 'jti',

    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    'SLIDING_TOKEN_LIFETIME': timedelta(minutes=5),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=1),

    "AUTH_COOKIE_SECURE": False,
}

DJOSER = {

    'LOGIN_FIELD': 'email',
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
        'user_create': 'authentication.serializers.UserSerializer',
        'user': 'authentication.serializers.UserSerializer',
        'current_user': 'authentication.serializers.UserSerializer',
        'user_delete': 'djoser.  .UserDeleteSerializer',
        }
}

INTERNAL_IPS = [
    "127.0.0.1",
    "192.168.0.151",
    "192.168.0.116",
    "192.168.68.127",
]

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",  # Use DB 1 for cache
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}
# testing postgresql db 
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql_psycopg2',
#         'NAME': 'dream_ziarah_new',
#         'USER': 'postgres',
#         'PASSWORD':'12345',
#         'HOST': 'localhost',
#         'PORT': '5432',
#     }
# }
