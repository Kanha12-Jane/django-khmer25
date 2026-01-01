from pathlib import Path
import os
from dotenv import load_dotenv
import dj_database_url

# ====================
# Paths
# ====================
BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env
load_dotenv(BASE_DIR / ".env")

# ====================
# Secret & Debug
# ====================
SECRET_KEY = os.getenv("SECRET_KEY")
DEBUG = os.getenv("DEBUG") == "True"

ALLOWED_HOSTS = ["*"]  # or your Railway app URL in production

# ====================
# Cloudinary Storage
# ====================
CLOUDINARY_STORAGE = {
    "CLOUD_NAME": os.getenv("CLOUDINARY_CLOUD_NAME"),
    "API_KEY": os.getenv("CLOUDINARY_API_KEY"),
    "API_SECRET": os.getenv("CLOUDINARY_API_SECRET"),
}

# Use Cloudinary for media files
DEFAULT_FILE_STORAGE = "cloudinary_storage.storage.MediaCloudinaryStorage"

# Static files: collect locally, serve via WhiteNoise or Railway
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# Optional: if you want Cloudinary for static files too
# STATICFILES_STORAGE = "cloudinary_storage.storage.StaticCloudinaryStorage"

MEDIA_URL = "/media/"

# ====================
# Installed Apps
# ====================
INSTALLED_APPS = [
    "cloudinary",
    "cloudinary_storage",

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rest_framework',
    "rest_framework_simplejwt",
    'products',
    "users",
    "djoser",
]

# ====================
# Middleware
# ====================
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # Add WhiteNoise middleware if you want static serving in production
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# ====================
# URLs & Templates
# ====================
ROOT_URLCONF = 'crm.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'crm.wsgi.application'

# ====================
# Database (Railway)
# ====================
DATABASES = {
    "default": dj_database_url.parse(
        os.getenv("DATABASE_URL"),
        conn_max_age=600,
        ssl_require=True,
    )
}

# ====================
# Password validation
# ====================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
]

# ====================
# Internationalization
# ====================
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# ====================
# REST Framework + Djoser
# ====================
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticatedOrReadOnly",
    ),
}

DJOSER = {
    "SERIALIZERS": {
        "user": "users.serializers.CustomUserSerializer",
        "current_user": "users.serializers.CustomUserSerializer",
    }
}

# ====================
# WhiteNoise for static files in production
# ====================
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
