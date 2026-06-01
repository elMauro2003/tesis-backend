import os

from django.core.asgi import get_asgi_application

# Permite sobreescritura por entorno; en Docker usamos producción por defecto.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.prod")

application = get_asgi_application()
