from pathlib import Path
import os
from datetime import timedelta

from dotenv import load_dotenv
import dj_database_url
from django.templatetags.static import static

from corsheaders.defaults import default_headers

# ====================
# Paths
# ====================
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

# ====================
# Secret & Debug
# ====================
SECRET_KEY = os.getenv("SECRET_KEY", "unsafe-secret-key")
DEBUG = os.getenv("DEBUG", "False") == "True"

# ====================
# Allowed hosts
# ====================
ALLOWED_HOSTS = [
    "django-khmer25-production.up.railway.app",
    "localhost",
    "127.0.0.1",
    "192.168.78.250",
]

# ====================
# Applications
# ====================
INSTALLED_APPS = [
    "unfold",

    "cloudinary",
    "cloudinary_storage",

    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    "corsheaders",

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

    "corsheaders.middleware.CorsMiddleware",  # ✅ must be before CommonMiddleware

    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",

    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# ====================
# ✅ REQUIRED CORE SETTINGS (FIX ROOT_URLCONF ERROR)
# ====================
ROOT_URLCONF = "crm.urls"
WSGI_APPLICATION = "crm.wsgi.application"
ASGI_APPLICATION = "crm.asgi.application"

# ====================
# Templates (FIX admin.E403 too)
# ====================
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",  # ✅ required for admin
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# ====================
# Database
# ====================
DATABASE_URL = os.getenv("DATABASE_URL", "")
DATABASES = {
    "default": dj_database_url.parse(
        DATABASE_URL,
        conn_max_age=600,
        ssl_require=True if DATABASE_URL else False,
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
# i18n / tz
# ====================
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Phnom_Penh"
USE_I18N = True
USE_TZ = True

# ====================
# Static & Media
# ====================
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]

MEDIA_URL = "/media/"

# ====================
# Storage (Cloudinary + WhiteNoise)
# ====================
STORAGES = {
    "default": {"BACKEND": "cloudinary_storage.storage.MediaCloudinaryStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}

CLOUDINARY_STORAGE = {
    "CLOUD_NAME": os.getenv("CLOUDINARY_CLOUD_NAME"),
    "API_KEY": os.getenv("CLOUDINARY_API_KEY"),
    "API_SECRET": os.getenv("CLOUDINARY_API_SECRET"),
}

# ====================
# CSRF + CORS
# ====================
CSRF_TRUSTED_ORIGINS = [
    "https://django-khmer25-production.up.railway.app",
    "https://flutter-khmer25-xslz.vercel.app",
    "https://*.vercel.app",
    "http://192.168.78.250:8000",
    "http://localhost:52265",
]

CORS_ALLOWED_ORIGINS = [
    "http://localhost:52265",
    "https://flutter-khmer25-xslz.vercel.app",
]

CORS_ALLOWED_ORIGIN_REGEXES = [
    r"^https://.*\.vercel\.app$",
]

CORS_ALLOW_HEADERS = list(default_headers) + [
    "authorization",
]

# ====================
# SimpleJWT
# ====================
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=1),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=2),
    "ROTATE_REFRESH_TOKENS": False,
    "BLACKLIST_AFTER_ROTATION": False,
    "UPDATE_LAST_LOGIN": False,
    "AUTH_HEADER_TYPES": ("Bearer",),
}

# ====================
# REST Framework (ONLY ONCE)
# ====================
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticatedOrReadOnly",
    ),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
}

# ====================
# Djoser
# ====================
DJOSER = {
    "SERIALIZERS": {
        "user": "users.serializers.CustomUserSerializer",
        "current_user": "users.serializers.CustomUserSerializer",
    }
}

# ====================
# Railway proxy HTTPS
# ====================
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True

SECURE_SSL_REDIRECT = not DEBUG
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ====================
# UNFOLD
# ====================
UNFOLD = {
    "SITE_TITLE": "Khmer25 Admin",
    "SITE_HEADER": "Khmer25 Dashboard",
    "SITE_SUBHEADER": "E-Commerce Management System",
    "SITE_URL": "/admin/",
    "SITE_LOGO": {
        "light": lambda request: static("images/logo.png"),
        "dark": lambda request: static("images/logo.png"),
    },
    "SITE_ICON": {
        "light": lambda request: static("images/logo.png"),
        "dark": lambda request: static("images/logo.png"),
    },
    "LOGIN": {
        "image": lambda request: static("images/logo.png"),
    },
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": True,
    },
    "DASHBOARD": {"show_recent_actions": True},
}
