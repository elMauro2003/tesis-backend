#!/usr/bin/env python
"""
manage.py — Punto de entrada para comandos Django.

Uso habitual:
  python manage.py runserver          → levanta servidor de desarrollo
  python manage.py makemigrations     → genera migraciones
  python manage.py migrate            → aplica migraciones
  python manage.py createsuperuser    → crea admin
  python manage.py shell_plus         → shell con todos los modelos importados (requiere django-extensions)
"""
import os
import sys


def main():
    # Por defecto usa settings de desarrollo; en producción debe definirse:
    # export DJANGO_SETTINGS_MODULE=config.settings.prod
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "No se pudo importar Django. ¿Está el virtualenv activo "
            "y Django instalado?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
