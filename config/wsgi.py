"""
config/wsgi.py — Punto de entrada para Gunicorn en producción.
"""
import os
from django.core.wsgi import get_wsgi_application

# En producción se sobreescribe con: DJANGO_SETTINGS_MODULE=config.settings.prod
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")
application = get_wsgi_application()
