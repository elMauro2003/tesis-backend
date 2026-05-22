from django.apps import AppConfig

class ActorsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.actors"
    verbose_name = "Dominio de Actores"

    def ready(self):
        # Importar señales al arrancar la app
        import apps.actors.signals  # noqa: F401
