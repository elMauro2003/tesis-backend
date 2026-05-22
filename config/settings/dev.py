from .base import *

DEBUG = True

REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"] = [
    "rest_framework.renderers.JSONRenderer",
    "rest_framework.renderers.BrowsableAPIRenderer",
]

# En desarrollo permitimos cualquier origen CORS (facilita trabajo con frontend local)
CORS_ALLOW_ALL_ORIGINS = True

# django-extensions: shell_plus, show_urls, graph_models, etc.
INSTALLED_APPS += ["django_extensions"]

# Base de datos SQLite para desarrollo local (fácil de borrar/recrear)
from pathlib import Path
DB_PATH = Path(__file__).resolve().parent.parent.parent / "db_dev.sqlite3"
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": str(DB_PATH),
    }
}

# Permitir que la app use la DB SQLite al ejecutar comandos de desarrollo
print(f"Using dev SQLite DB: {DATABASES['default']['NAME']}")
