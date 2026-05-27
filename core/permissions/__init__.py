"""
Clases de permisos reutilizables expuestas por el paquete core.permissions.

Este archivo contiene la implementación real para evitar colisiones entre el
paquete core.permissions/ y el módulo core/permissions.py.
"""
from rest_framework.permissions import BasePermission, SAFE_METHODS


def _user_has_role(user, *roles: str) -> bool:
    """Verifica si el usuario pertenece a al menos uno de los roles dados."""
    if not user or not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    return user.groups.filter(name__in=roles).exists()


class IsInstructor(BasePermission):
    message = "Se requiere rol de instructor de beca."

    def has_permission(self, request, view):
        return _user_has_role(request.user, "instructor", "directivo", "admin")


class IsDirectivo(BasePermission):
    message = "Se requiere rol de directivo de beca."

    def has_permission(self, request, view):
        return _user_has_role(request.user, "directivo", "admin")


class IsSubdirector(BasePermission):
    message = "Se requiere rol de subdirector administrativo."

    def has_permission(self, request, view):
        return _user_has_role(request.user, "subdirector", "directivo", "admin")


class IsComunicador(BasePermission):
    message = "Se requiere rol de comunicador."

    def has_permission(self, request, view):
        return _user_has_role(request.user, "comunicador", "directivo", "admin")


class IsEstudiante(BasePermission):
    message = "Se requiere rol de estudiante."

    def has_permission(self, request, view):
        return _user_has_role(request.user, "estudiante")


class IsDecano(BasePermission):
    message = "Se requiere rol de decano."

    def has_permission(self, request, view):
        return _user_has_role(request.user, "decano", "directivo", "admin")


class IsPPA(BasePermission):
    message = "Se requiere rol de Profesor Principal de Año (PPA)."

    def has_permission(self, request, view):
        return _user_has_role(request.user, "ppa", "directivo", "admin")


class IsPG(BasePermission):
    message = "Se requiere rol de Profesor Guía (PG)."

    def has_permission(self, request, view):
        return _user_has_role(request.user, "pg", "directivo", "admin")


class IsAdmin(BasePermission):
    message = "Se requiere rol de administrador del sistema."

    def has_permission(self, request, view):
        return _user_has_role(request.user, "admin") or request.user.is_superuser


class IsInstructorOrDirectivo(BasePermission):
    message = "Se requiere rol de instructor o directivo."

    def has_permission(self, request, view):
        return _user_has_role(request.user, "instructor", "directivo", "admin")


class IsStudentReader(BasePermission):
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


class IsOwner(BasePermission):
    message = "Solo el propietario puede realizar esta acción."

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return request.user.is_authenticated
        return hasattr(obj, "user") and obj.user == request.user


class IsStudentOwner(BasePermission):
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
    message = "Solo quien realizó la asignación puede modificarla."

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return request.user.is_authenticated
        return hasattr(obj, "assigned_by") and obj.assigned_by == request.user


class IsStudentOwnerOrInstructor(BasePermission):
    message = "Se requiere ser el estudiante propietario o tener rol de instructor."

    def has_object_permission(self, request, view, obj):
        user = request.user
        if _user_has_role(user, "instructor", "directivo", "subdirector", "admin"):
            return True
        if hasattr(obj, "student") and hasattr(obj.student, "user"):
            return obj.student.user == user
        return False


__all__ = [
    "IsInstructor",
    "IsDirectivo",
    "IsSubdirector",
    "IsComunicador",
    "IsEstudiante",
    "IsDecano",
    "IsPPA",
    "IsPG",
    "IsAdmin",
    "IsInstructorOrDirectivo",
    "IsStudentReader",
    "IsOwner",
    "IsStudentOwner",
    "IsAssignedBy",
    "IsStudentOwnerOrInstructor",
]
