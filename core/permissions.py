"""
core/permissions.py

Clases de permisos reutilizables por todos los ViewSets.

Implementa el RBAC definido en la tesis y los patrones
de permisos a nivel de objeto.

Los 9 roles del sistema son Groups de Django:
  - estudiante
  - instructor
  - directivo
  - subdirector
  - comunicador
  - decano
  - ppa  (Profesor Principal de Año)
  - pg   (Profesor Guía)
  - admin
"""
from rest_framework.permissions import BasePermission, SAFE_METHODS


# ─── Helpers ───────────────────────────────────────────────────────────────────

def _user_has_role(user, *roles: str) -> bool:
    """Verifica si el usuario pertenece a al menos uno de los roles dados."""
    if not user or not user.is_authenticated:
        return False
    # is_superuser tiene acceso total
    if user.is_superuser:
        return True
    return user.groups.filter(name__in=roles).exists()


# ─── Permisos por Rol ──────────────────────────────────────────────────────────

class IsInstructor(BasePermission):
    """Instructor de beca: gestiona estudiantes, evaluaciones y asignaciones."""
    message = "Se requiere rol de instructor de beca."

    def has_permission(self, request, view):
        return _user_has_role(request.user, "instructor", "directivo", "admin")


class IsDirectivo(BasePermission):
    """Directivo de beca: CRUD infraestructura (sedes, edificios, alas, cuartos) y reportes."""
    message = "Se requiere rol de directivo de beca."

    def has_permission(self, request, view):
        return _user_has_role(request.user, "directivo", "admin")


class IsSubdirector(BasePermission):
    """Subdirector administrativo: gestiona quejas (estado, respuesta, visibilidad)."""
    message = "Se requiere rol de subdirector administrativo."

    def has_permission(self, request, view):
        return _user_has_role(request.user, "subdirector", "directivo", "admin")


class IsComunicador(BasePermission):
    """Comunicador: CRUD de informaciones/noticias."""
    message = "Se requiere rol de comunicador."

    def has_permission(self, request, view):
        return _user_has_role(request.user, "comunicador", "directivo", "admin")


class IsEstudiante(BasePermission):
    """Estudiante becado: acceso a sus propias quejas, evaluaciones e informaciones."""
    message = "Se requiere rol de estudiante."

    def has_permission(self, request, view):
        return _user_has_role(request.user, "estudiante")


class IsDecano(BasePermission):
    """Decano: consulta de estudiantes de su facultad."""
    message = "Se requiere rol de decano."

    def has_permission(self, request, view):
        return _user_has_role(request.user, "decano", "directivo", "admin")


class IsPPA(BasePermission):
    """Profesor Principal de Año: consulta estudiantes de su año."""
    message = "Se requiere rol de Profesor Principal de Año (PPA)."

    def has_permission(self, request, view):
        return _user_has_role(request.user, "ppa", "directivo", "admin")


class IsPG(BasePermission):
    """Profesor Guía: consulta estudiantes de su grupo."""
    message = "Se requiere rol de Profesor Guía (PG)."

    def has_permission(self, request, view):
        return _user_has_role(request.user, "pg", "directivo", "admin")


class IsAdmin(BasePermission):
    """Administrador del sistema: gestión de roles y usuarios."""
    message = "Se requiere rol de administrador del sistema."

    def has_permission(self, request, view):
        return _user_has_role(request.user, "admin") or request.user.is_superuser


class IsInstructorOrDirectivo(BasePermission):
    """Instructor O Directivo: para operaciones compartidas como asignaciones."""
    message = "Se requiere rol de instructor o directivo."

    def has_permission(self, request, view):
        return _user_has_role(request.user, "instructor", "directivo", "admin")


class IsStudentReader(BasePermission):
    """
    Lectura de estudiantes para roles académicos y de gestión.
    Usado en listados y consultas de detalle.
    """
    message = "Se requiere rol de instructor, directivo, decano, PPA o PG."

    def has_permission(self, request, view):
        return _user_has_role(
            request.user,
            "instructor",
            "directivo",
            "decano",
            "ppa",
            "pg",
            "admin",
        )


# ─── Permisos a Nivel de Objeto  ───

class IsOwner(BasePermission):
    """
    Patrón 1: El recurso tiene un campo 'user' que apunta directamente al usuario.
    Solo el propietario puede modificar; lectura permitida a autenticados.
    """
    message = "Solo el propietario puede realizar esta acción."

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return request.user.is_authenticated
        return hasattr(obj, "user") and obj.user == request.user


class IsStudentOwner(BasePermission):
    """
    Patrón 2: El recurso tiene un campo 'student' que apunta a un Student,
    que a su vez tiene un campo 'user'. Usado en Quejas y Evaluaciones.
    Solo el estudiante dueño puede modificar sus propios recursos.
    """
    message = "Solo el estudiante propietario puede realizar esta acción."

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return request.user.is_authenticated
        return (
            hasattr(obj, "student")
            and hasattr(obj.student, "user")
            and obj.student.user == request.user
        )


class IsAssignedBy(BasePermission):
    """
    Patrón 3: El recurso tiene un campo 'assigned_by' que apunta al usuario
    que realizó la asignación. Usado en Assignments.
    """
    message = "Solo quien realizó la asignación puede modificarla."

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return request.user.is_authenticated
        return hasattr(obj, "assigned_by") and obj.assigned_by == request.user


class IsStudentOwnerOrInstructor(BasePermission):
    """
    Combinado: el estudiante dueño puede leer/modificar sus recursos,
    o un instructor/directivo puede gestionarlos.
    Usado principalmente en Quejas.
    """
    message = "Se requiere ser el estudiante propietario o tener rol de instructor."

    def has_object_permission(self, request, view, obj):
        user = request.user
        # Instructores y directivos tienen acceso total
        if _user_has_role(user, "instructor", "directivo", "subdirector", "admin"):
            return True
        # El estudiante dueño puede leer y modificar sus propios recursos
        if hasattr(obj, "student") and hasattr(obj.student, "user"):
            return obj.student.user == user
        return False
