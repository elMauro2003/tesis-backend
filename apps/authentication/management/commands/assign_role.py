"""
Comando de conveniencia para asignar un rol a un usuario desde la CLI.

Uso:
    python manage.py assign_role <username> <role>

Ejemplo:
    python manage.py assign_role jperez instructor
    python manage.py assign_role mgarcia estudiante
"""
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

User = get_user_model()


class Command(BaseCommand):
    help = "Asigna un rol (Group) a un usuario existente."

    def add_arguments(self, parser):
        parser.add_argument("username", type=str, help="Nombre de usuario")
        parser.add_argument(
            "role",
            type=str,
            help="Nombre del rol: estudiante | instructor | directivo | "
                 "subdirector | comunicador | decano | ppa | pg | admin",
        )

    def handle(self, *args, **options):
        username = options["username"]
        role_name = options["role"]

        # Verificar que el usuario existe
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise CommandError(f"El usuario '{username}' no existe.")

        # Verificar que el rol existe
        try:
            group = Group.objects.get(name=role_name)
        except Group.DoesNotExist:
            raise CommandError(
                f"El rol '{role_name}' no existe. "
                f"Ejecuta primero: python manage.py create_roles"
            )

        # Asignar el rol
        user.groups.add(group)
        self.stdout.write(
            self.style.SUCCESS(
                f"Rol '{role_name}' asignado a '{username}' correctamente."
            )
        )
