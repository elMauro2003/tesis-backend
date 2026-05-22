from .base import *

DEBUG = False

# Permite ejecutar tests aunque no exista .env local
SECRET_KEY = config("SECRET_KEY", default="test-secret-key-not-for-production")
ALLOWED_HOSTS = ["*"]

# BD aislada para pruebas
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "test_db.sqlite3",
        # Habilita ALL constraints en SQLite incluyendo UNIQUE
        "OPTIONS": {
            "timeout": 20,
        },
    }
}

# Acelera hashing durante pruebas
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

# Sin browsable API en tests
REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"] = [
    "rest_framework.renderers.JSONRenderer",
]
