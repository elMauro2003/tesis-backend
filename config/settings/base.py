from pathlib import Path
from datetime import timedelta
from decouple import config, Csv

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = config(
    "SECRET_KEY",
    default="dev-only-secret-key-for-local-development-please-override-in-production-2026",
)
ALLOWED_HOSTS = config("ALLOWED_HOSTS", cast=Csv(), default="localhost,127.0.0.1")


DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

THIRD_PARTY_APPS = [
    "rest_framework",
    "rest_framework_simplejwt",
    "corsheaders",
    "django_filters",
    "drf_spectacular",
]

LOCAL_APPS = [
    "apps.academic",
    "apps.infrastructure",
    "apps.actors",
    "apps.operations",
    "apps.authentication",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# ─── Custom User Model ────────────────────────────────────────────────────────
AUTH_USER_MODEL = "authentication.User"
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",        # <- antes de Common
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
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

WSGI_APPLICATION = "config.wsgi.application"


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config("DB_NAME", default="uclv_residencias"),
        "USER": config("DB_USER", default="postgres"),
        "PASSWORD": config("DB_PASSWORD", default="postgres"),
        "HOST": config("DB_HOST", default="localhost"),
        "PORT": config("DB_PORT", default="5432"),
        "OPTIONS": {
            # Garantiza que los errores de BD se propaguen inmediatamente
            "connect_timeout": 10,
        },
    }
}


# ─── Password Validation ───────────────────────────────────────────────────────
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# ─── Internationalization ──────────────────────────────────────────────────────
LANGUAGE_CODE = "es-cu"
TIME_ZONE = "America/Havana"
USE_I18N = True
USE_TZ = True


# ─── Static files ──────────────────────────────────────────────────────────────
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# ─── Django REST Framework ─────────────────────────────────────────────────────
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    
    "DEFAULT_PAGINATION_CLASS": "core.pagination.StandardResultsPagination",
    "PAGE_SIZE": 20,
    
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
    
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ],
    
    "EXCEPTION_HANDLER": "core.exceptions.custom_exception_handler",
    
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}


SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=15),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": False,
    "BLACKLIST_AFTER_ROTATION": False,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "TOKEN_OBTAIN_SERIALIZER": "apps.authentication.serializers.CustomTokenObtainPairSerializer",
}



CORS_ALLOWED_ORIGINS = config("CORS_ALLOWED_ORIGINS", cast=Csv(), default="")
CORS_ALLOW_CREDENTIALS = True


SPECTACULAR_SETTINGS = {
    "TITLE": "API Sistema de Gestión de Residencias Estudiantiles — UCLV",
    "DESCRIPTION": (
        "Backend del sistema de gestión de residencias estudiantiles de la "
        "Universidad Central 'Marta Abreu' de Las Villas (UCLV). "
        "Implementado con Django REST Framework como parte del Trabajo de Diploma "
        "de Mauricio Jesús Avalo Tamayo."
    ),
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "COMPONENT_SPLIT_REQUEST": True,
    "SCHEMA_PATH_PREFIX": "/api/v1/",
    "TAGS": [
        {"name": "auth", "description": "Autenticación JWT"},
        {"name": "academic", "description": "Facultades, Carreras, Años Académicos, Grupos"},
        {"name": "infrastructure", "description": "Sedes, Edificios, Alas, Cuartos"},
        {"name": "students", "description": "Gestión de Estudiantes"},
        {"name": "professors", "description": "Profesores y Roles"},
        {"name": "assignments", "description": "Asignación de Cuartos"},
        {"name": "evaluations", "description": "Evaluaciones de Estudiantes"},
        {"name": "complaints", "description": "Quejas y Planteamientos"},
        {"name": "cleaning", "description": "Cuartelerías"},
        {"name": "information", "description": "Noticias e Informaciones"},
        {"name": "reports", "description": "Reportes"},
        {"name": "roles", "description": "Gestión de Roles y Permisos"},
    ],
}
