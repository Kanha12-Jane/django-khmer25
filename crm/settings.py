from pathlib import Path
import os
from dotenv import load_dotenv
import dj_database_url

# ====================
# Paths
# ====================
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables
load_dotenv(BASE_DIR / ".env")

# ====================
# Secret & Debug
# ====================
SECRET_KEY = os.getenv("SECRET_KEY", "unsafe-secret-key")
DEBUG = os.getenv("DEBUG", "False") == "True"

# ====================
# Allowed hosts & CSRF
# ====================
ALLOWED_HOSTS = [
    "django-khmer25-production.up.railway.app",
    "localhost",
    "127.0.0.1",
]

# CSRF is mainly for cookie/session auth (admin forms).
# For JWT APIs it's usually not needed, but keep it safe:
CSRF_TRUSTED_ORIGINS = [
    "https://django-khmer25-production.up.railway.app",
    "https://flutter-khmer25-xslz.vercel.app",
    "https://*.vercel.app",
]

# ====================
# CORS (IMPORTANT for Flutter Web on Vercel)
# ====================
CORS_ALLOWED_ORIGINS = [
    "https://flutter-khmer25-xslz.vercel.app",
]

# Allow all Vercel preview domains too
CORS_ALLOWED_ORIGIN_REGEXES = [
    r"^https://.*\.vercel\.app$",
]

# If you use Authorization: Bearer ...
CORS_ALLOW_HEADERS = [
    "accept",
    "accept-encoding",
    "authorization",
    "content-type",
    "dnt",
    "origin",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
]

# If your frontend sends cookies (usually NO for JWT),
# you can enable this:
# CORS_ALLOW_CREDENTIALS = True

# ====================
# Cloudinary Storage
# ====================
CLOUDINARY_STORAGE = {
    "CLOUD_NAME": os.getenv("CLOUDINARY_CLOUD_NAME"),
    "API_KEY": os.getenv("CLOUDINARY_API_KEY"),
    "API_SECRET": os.getenv("CLOUDINARY_API_SECRET"),
}

DEFAULT_FILE_STORAGE = "cloudinary_storage.storage.MediaCloudinaryStorage"

# ====================
# Static & Media files
# ====================
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_URL = "/media/"

# ====================
# Installed Apps
# ====================
INSTALLED_APPS = [
    "cloudinary",
    "cloudinary_storage",

    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    "corsheaders",  # ✅ MUST be before DRF apps is ok

    "rest_framework",
    "rest_framework_simplejwt",
    "djoser",

    "products",
    "users",
]

# ====================
# Middleware
# ====================
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",

    # ✅ CORS middleware MUST be near the top (before CommonMiddleware)
    "corsheaders.middleware.CorsMiddleware",

    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",

    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# ====================
# URLs & Templates
# ====================
ROOT_URLCONF = "crm.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "crm.wsgi.application"

# ====================
# Database
# ====================
DATABASES = {
    "default": dj_database_url.parse(
        os.getenv("DATABASE_URL", ""),
        conn_max_age=600,
        ssl_require=True,
    )
}

# ====================
# Password validation
# ====================
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ====================
# Internationalization
# ====================
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
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
# Railway HTTPS / Proxy Fix (IMPORTANT)
# ====================
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True

# ====================
# Optional Security Settings
# ====================
SECURE_SSL_REDIRECT = not DEBUG
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
