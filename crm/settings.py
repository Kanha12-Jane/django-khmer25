from pathlib import Path
import os
from datetime import timedelta

from dotenv import load_dotenv
import dj_database_url

from django.templatetags.static import static  # ✅ for UNFOLD logo


# ====================
# Paths
# ====================
BASE_DIR = Path(__file__).resolve().parent.parent

# Load local .env (Railway uses Variables, but safe for local)
load_dotenv(BASE_DIR / ".env")


# ====================
# Secret & Debug
# ====================
SECRET_KEY = os.getenv("SECRET_KEY", "unsafe-secret-key")
DEBUG = os.getenv("DEBUG", "False") == "True"


# ====================
# SimpleJWT
# ====================
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=1),   # ✅ 1 day
    "REFRESH_TOKEN_LIFETIME": timedelta(days=2),  # ✅ 2 days
    "ROTATE_REFRESH_TOKENS": False,
    "BLACKLIST_AFTER_ROTATION": False,
    "UPDATE_LAST_LOGIN": False,
}


# ====================
# Hosts & CSRF
# ====================
ALLOWED_HOSTS = [
    "django-khmer25-production.up.railway.app",
    "localhost",
    "127.0.0.1",
    "192.168.2.27",
]

CSRF_TRUSTED_ORIGINS = [
    "https://django-khmer25-production.up.railway.app",
    "https://flutter-khmer25-xslz.vercel.app",
    "https://*.vercel.app",
    "http://192.168.2.27:8000",
]


# ====================
# CORS (Flutter Web on Vercel)
# ====================
CORS_ALLOWED_ORIGINS = [
    "https://flutter-khmer25-xslz.vercel.app",
]

# Allow all Vercel preview deployments
CORS_ALLOWED_ORIGIN_REGEXES = [
    r"^https://.*\.vercel\.app$",
]

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


# ====================
# Cloudinary (Media Storage)
# ====================
CLOUDINARY_STORAGE = {
    "CLOUD_NAME": os.getenv("CLOUDINARY_CLOUD_NAME"),
    "API_KEY": os.getenv("CLOUDINARY_API_KEY"),
    "API_SECRET": os.getenv("CLOUDINARY_API_SECRET"),
}

# Django 4.2+ recommended way (use STORAGES)
STORAGES = {
    "default": {
        "BACKEND": "cloudinary_storage.storage.MediaCloudinaryStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}


# ====================
# Static & Media
# ====================
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# ✅ for local dev static folder (logo.png etc.)
STATICFILES_DIRS = [
    BASE_DIR / "static",
]

MEDIA_URL = "/media/"  # Cloudinary will return https Cloudinary URLs via .url


# ====================
# Installed Apps
# ====================
INSTALLED_APPS = [
    "unfold",  # ✅ MUST be before django.contrib.admin

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

    # ✅ corsheaders recommends high in the list (before CommonMiddleware)
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
# Database (Railway)
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
# Internationalization
# ====================
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Phnom_Penh"  # ✅ Cambodia time (optional but recommended)
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
# Railway proxy HTTPS
# ====================
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True


# ====================
# Security (prod)
# ====================
SECURE_SSL_REDIRECT = not DEBUG
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG


# ====================
# Django defaults
# ====================
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# ====================
# UNFOLD (Branding + Logo)
# ====================
UNFOLD = {
    "SITE_TITLE": "Khmer25 Admin",
    "SITE_HEADER": "Khmer25 Dashboard",
    "SITE_SUBHEADER": "E-Commerce Management System",
    "SITE_URL": "/admin/",

    # ✅ Correct (docs): use static() with lambda request
    "SITE_LOGO": {
        "light": lambda request: static("images/logo.png"),
        "dark": lambda request: static("images/logo.png"),
    },
    "SITE_ICON": {
        "light": lambda request: static("images/logo.png"),
        "dark": lambda request: static("images/logo.png"),
    },

    # ✅ Correct (docs): LOGIN uses "image" (optional)
    "LOGIN": {
        "image": lambda request: static("images/logo.png"),
        # optional:
        # "redirect_after": lambda request: reverse_lazy("admin:index"),
        # "form": "app.forms.CustomLoginForm",
    },

    "COLORS": {
        "primary": {
            "50": "#e6f0ff",
            "100": "#b3d1ff",
            "200": "#80b3ff",
            "300": "#4d94ff",
            "400": "#1a75ff",
            "500": "#005ce6",
            "600": "#0047b3",
            "700": "#003380",
            "800": "#001f4d",
            "900": "#000a1a",
        }
    },

    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": True,
    },

    "DASHBOARD": {
        "show_recent_actions": True,
    },
    "NAVIGATION": [
        {
            "title": "Khmer25 Product",
            "items": [
                {"title": "Products", "model": "products.Product", "icon": "inventory_2"},
                {"title": "Categorys", "model": "products.Category", "icon": "category"},
                {"title": "Carts", "model": "products.Cart", "icon": "shopping_cart"},
                {"title": "Orders", "model": "products.Order", "icon": "receipt_long"},
                {"title": "Payment proofs", "model": "products.PaymentProof", "icon": "payments"},
            ],
        },
        {
            "title": "Authentication and Authorization",
            "items": [
                {"title": "Groups", "model": "auth.Group", "icon": "groups"},
                {"title": "Users", "model": "users.User", "icon": "person"},
            ],
        },
    ],
}
