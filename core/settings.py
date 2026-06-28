"""
Django settings for SMPI (Sistema de Manutenção Prescritiva Inteligente).
Uses django-environ for environment variable management.
"""

from pathlib import Path
import environ


def _read_secret(name: str) -> str:
    """Read a Docker Secret from /run/secrets/. Returns '' if file not found."""
    try:
        return (Path('/run/secrets') / name).read_text().strip()
    except OSError:
        return ''

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------------------
# django-environ setup
# ---------------------------------------------------------------------------
env = environ.Env(
    DEBUG=(bool, False),
    ALLOWED_HOSTS=(list, ['localhost', '127.0.0.1']),
    CSRF_TRUSTED_ORIGINS=(list, ['http://localhost:8000', 'http://127.0.0.1:8000']),
    TIME_ZONE=(str, 'America/Sao_Paulo'),
    LANGUAGE_CODE=(str, 'pt-br'),
    LLM_PROVIDER=(str, 'openai'),
    LLM_MODEL=(str, 'gpt-4o-mini'),
    EMBEDDINGS_MODEL=(str, 'text-embedding-3-small'),
    CELERY_BROKER_URL=(str, 'amqp://guest:guest@localhost:5672//'),
    CELERY_RESULT_BACKEND=(str, 'redis://localhost:6379/0'),
    REDIS_URL=(str, 'redis://localhost:6379/1'),
    EMAIL_BACKEND=(str, 'django.core.mail.backends.console.EmailBackend'),
    EMAIL_HOST=(str, 'smtp.gmail.com'),
    EMAIL_PORT=(int, 587),
    EMAIL_USE_TLS=(bool, True),
    EMAIL_HOST_USER=(str, ''),
    EMAIL_HOST_PASSWORD=(str, ''),
    EVOLUTION_API_URL=(str, 'http://localhost:8080'),
    EVOLUTION_API_KEY=(str, ''),
    EVOLUTION_INSTANCE=(str, 'smpi'),
)

environ.Env.read_env(BASE_DIR / '.env', overwrite=False)

# ---------------------------------------------------------------------------
# Core
# ---------------------------------------------------------------------------
SECRET_KEY = env('SECRET_KEY', default=None) or _read_secret('smpi_django_secret') or 'django-insecure-change-me-in-production'
DEBUG = env('DEBUG')
ALLOWED_HOSTS = env('ALLOWED_HOSTS')
CSRF_TRUSTED_ORIGINS = env('CSRF_TRUSTED_ORIGINS')

# ---------------------------------------------------------------------------
# Application definition
# ---------------------------------------------------------------------------
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.postgres',
    # Third-party
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    'django_celery_results',
    'django_celery_beat',
    'django_extensions',
    'drf_spectacular',
    'django_filters',
    # Project apps — foundation
    'base',
    'accounts',
    'assets',
    'faults',
    'monitoring',
    'api',
    'notifications',
    # Project apps — future sprints (stubs only, no models yet)
    'knowledge',
    'prescriptions',
    'analytics',
    'reports',
    'ai',
    'whatsapp',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'base.middleware.MediaProtectionMiddleware',
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'notifications.context_processors.unread_notifications',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'

# ---------------------------------------------------------------------------
# Database — PostgreSQL
# ---------------------------------------------------------------------------
if env('DATABASE_URL', default=''):
    DATABASES = {
        'default': env.db('DATABASE_URL')
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': env('POSTGRES_DB', default='smpi'),
            'USER': env('POSTGRES_USER', default='smpi'),
            'PASSWORD': _read_secret('smpi_db_password') or env('POSTGRES_PASSWORD', default='smpi'),
            'HOST': env('POSTGRES_HOST', default='localhost'),
            'PORT': env('POSTGRES_PORT', default='5432'),
        }
    }

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ---------------------------------------------------------------------------
# Authentication
# ---------------------------------------------------------------------------
AUTH_USER_MODEL = 'accounts.User'

AUTHENTICATION_BACKENDS = [
    'accounts.backends.EmailBackend',
    'django.contrib.auth.backends.ModelBackend',
]

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/accounts/login/'

# ---------------------------------------------------------------------------
# Internationalization
# ---------------------------------------------------------------------------
LANGUAGE_CODE = env('LANGUAGE_CODE')
TIME_ZONE = env('TIME_ZONE')
USE_I18N = True
USE_TZ = True

# ---------------------------------------------------------------------------
# Static & Media files
# ---------------------------------------------------------------------------
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ---------------------------------------------------------------------------
# Cache (Redis)
# ---------------------------------------------------------------------------
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': env('REDIS_URL'),
    }
}

# ---------------------------------------------------------------------------
# Celery
# ---------------------------------------------------------------------------
CELERY_BROKER_URL = env('CELERY_BROKER_URL')
CELERY_RESULT_BACKEND = env('CELERY_RESULT_BACKEND')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = env('TIME_ZONE')
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'
CELERY_RESULT_EXTENDED = True

# ---------------------------------------------------------------------------
# Docker Secrets — sobrescreve credenciais de conexão em produção
# ---------------------------------------------------------------------------
_redis_secret = _read_secret('smpi_redis_password')
_rabbit_secret = _read_secret('smpi_rabbit_password')
if _redis_secret:
    _rh = env('REDIS_HOST', default='redis')
    CELERY_RESULT_BACKEND = f'redis://:{_redis_secret}@{_rh}:6379/0'
    REDIS_URL = f'redis://:{_redis_secret}@{_rh}:6379/1'
    CACHES['default']['LOCATION'] = REDIS_URL
if _rabbit_secret:
    _rmq_user = env('RABBITMQ_DEFAULT_USER', default='smpi')
    _rmq_host = env('RABBITMQ_HOST', default='rabbitmq')
    CELERY_BROKER_URL = f'amqp://{_rmq_user}:{_rabbit_secret}@{_rmq_host}:5672/'

# ---------------------------------------------------------------------------
# Django REST Framework
# ---------------------------------------------------------------------------
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'api.authentication.ApiKeyAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 50,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

# ---------------------------------------------------------------------------
# drf-spectacular
# ---------------------------------------------------------------------------
SPECTACULAR_SETTINGS = {
    'TITLE': 'SMPI API',
    'DESCRIPTION': 'Sistema de Manutenção Prescritiva Inteligente - API',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}

# ---------------------------------------------------------------------------
# CORS
# ---------------------------------------------------------------------------
CORS_ALLOWED_ORIGINS = env('CSRF_TRUSTED_ORIGINS')
CORS_ALLOW_CREDENTIALS = True

# ---------------------------------------------------------------------------
# Email
# ---------------------------------------------------------------------------
EMAIL_BACKEND = env('EMAIL_BACKEND')
EMAIL_HOST = env('EMAIL_HOST')
EMAIL_PORT = env('EMAIL_PORT')
EMAIL_USE_TLS = env('EMAIL_USE_TLS')
EMAIL_HOST_USER = env('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = env('EMAIL_HOST_USER', default='noreply@smpi.local')

# ---------------------------------------------------------------------------
# AI / LLM
# ---------------------------------------------------------------------------
LLM_PROVIDER = env('LLM_PROVIDER')
LLM_MODEL = env('LLM_MODEL')
EMBEDDINGS_MODEL = env('EMBEDDINGS_MODEL')
OPENAI_API_KEY = env('OPENAI_API_KEY', default='') or _read_secret('smpi_openai_key')
ANTHROPIC_API_KEY = env('ANTHROPIC_API_KEY', default='')
LANGSMITH_API_KEY = env('LANGSMITH_API_KEY', default='')

# ---------------------------------------------------------------------------
# Evolution API (WhatsApp)
# ---------------------------------------------------------------------------
EVOLUTION_API_URL = env('EVOLUTION_API_URL')
EVOLUTION_API_KEY = env('EVOLUTION_API_KEY') or _read_secret('smpi_evolution_key')
EVOLUTION_INSTANCE = env('EVOLUTION_INSTANCE')

# ---------------------------------------------------------------------------
# ML Artifacts
# ---------------------------------------------------------------------------
SCALER_PATH = BASE_DIR / 'ml_artifacts' / 'scaler.pkl'

# ---------------------------------------------------------------------------
# Sessions
# ---------------------------------------------------------------------------
SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'
SESSION_COOKIE_AGE = 86400 * 7  # 7 days

# ---------------------------------------------------------------------------
# Segurança HTTP (produção — atrás do Traefik/proxy reverso)
# ---------------------------------------------------------------------------
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_REDIRECT_EXEMPT = [r'^health/$']
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
