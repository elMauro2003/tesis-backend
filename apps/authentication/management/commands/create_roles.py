"""
Comando personalizado para crear los 9 roles del sistema RBAC
como Groups de Django (ver tesis §2.6.2, Tabla 7).

Uso:
    python manage.py create_roles

Se ejecuta una sola vez tras las migraciones iniciales (o en cada
deploy sin efecto secundario gracias a get_or_create).
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType


# ─── Definición de Roles ───────────────────────────────────────────────────────
# Cada entrada: (nombre_del_grupo, descripción)
ROLES = [
    ("estudiante",   "Estudiante becado residente"),
    ("instructor",   "Instructor de beca — gestiona estudiantes, evaluaciones y asignaciones"),
    ("directivo",    "Directivo de beca — CRUD infraestructura, reportes y supervisión"),
    ("subdirector",  "Subdirector administrativo — gestiona quejas"),
    ("comunicador",  "Comunicador — publica informaciones/noticias"),
    ("decano",       "Decano de facultad — consulta estudiantes de su facultad"),
    ("ppa",          "Profesor Principal de Año — consulta estudiantes de su año"),
    ("pg",           "Profesor Guía — consulta estudiantes de su grupo"),
    ("admin",        "Administrador del sistema — gestión de roles y usuarios"),
]


class Command(BaseCommand):
    help = "Crea los 9 roles del sistema RBAC como Groups de Django."

    def handle(self, *args, **options):
        self.stdout.write("🔐 Creando roles del sistema...\n")

        created_count = 0
        existing_count = 0

        for role_name, description in ROLES:
            group, created = Group.objects.get_or_create(name=role_name)

            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f"Creado: '{role_name}' — {description}")
                )
            else:
                existing_count += 1
                self.stdout.write(
                    self.style.WARNING(f"Ya existe: '{role_name}'")
                )

        self.stdout.write(
            f"\n📊 Resultado: {created_count} creados, {existing_count} ya existían.\n"
        )
        self.stdout.write(
            self.style.SUCCESS("Roles del sistema listos.\n")
        )
        self.stdout.write(
            "Asigna roles con: python manage.py assign_role <username> <role>\n"
        )
