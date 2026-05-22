from django.apps import AppConfig

class OperationsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.operations"
    verbose_name = "Dominio de Procesos Operativos"

    def ready(self):
        import apps.operations.signals  # noqa: F401
