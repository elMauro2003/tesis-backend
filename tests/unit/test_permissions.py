import pytest
from unittest.mock import MagicMock, patch
from django.contrib.auth.models import AnonymousUser

from core.permissions import (
    IsInstructor, IsDirectivo, IsSubdirector, IsComunicador,
    IsEstudiante, IsAdmin, IsInstructorOrDirectivo,
    IsOwner, IsStudentOwner, IsAssignedBy, IsStudentOwnerOrInstructor,
    _user_has_role,
)


# ─── Helper ───────────────────────────────────────────────────────────────────

def make_request(user):
    """Crea un mock de request con el usuario dado."""
    req = MagicMock()
    req.user = user
    return req


def make_user_with_role(role_name):
    """
    Crea un mock de User autenticado con un grupo específico.
    Evita BD usando MagicMock para tests unitarios puros.
    """
    user = MagicMock()
    user.is_authenticated = True
    user.is_superuser = False
    # Simular groups.filter(...).exists()
    user.groups.filter.return_value.exists.return_value = True
    return user


def make_user_without_role():
    user = MagicMock()
    user.is_authenticated = True
    user.is_superuser = False
    user.groups.filter.return_value.exists.return_value = False
    return user


# ─── Tests de _user_has_role ──────────────────────────────────────────────────

class TestUserHasRole:
    def test_none_user_returns_false(self):
        assert _user_has_role(None, "instructor") is False

    def test_anonymous_user_returns_false(self):
        user = MagicMock()
        user.is_authenticated = False
        assert _user_has_role(user, "instructor") is False

    def test_superuser_always_true(self):
        user = MagicMock()
        user.is_authenticated = True
        user.is_superuser = True
        assert _user_has_role(user, "cualquier_rol") is True

    def test_user_with_matching_role(self):
        user = make_user_with_role("instructor")
        assert _user_has_role(user, "instructor") is True

    def test_user_without_matching_role(self):
        user = make_user_without_role()
        assert _user_has_role(user, "instructor") is False


# ─── Tests de permisos por rol ────────────────────────────────────────────────

class TestRolePermissions:
    """
    Verifica que cada clase de permiso acepta su rol correcto
    y rechaza roles incorrectos.
    """

    @pytest.mark.parametrize("perm_class,valid_role", [
        (IsInstructor,         "instructor"),
        (IsDirectivo,          "directivo"),
        (IsSubdirector,        "subdirector"),
        (IsComunicador,        "comunicador"),
        (IsEstudiante,         "estudiante"),
        (IsAdmin,              "admin"),
        (IsInstructorOrDirectivo, "instructor"),
        (IsInstructorOrDirectivo, "directivo"),
    ])
    def test_permission_granted_for_valid_role(self, perm_class, valid_role):
        user = make_user_with_role(valid_role)
        perm = perm_class()
        request = make_request(user)
        assert perm.has_permission(request, None) is True

    def test_instructor_rejected_for_student(self):
        user = make_user_without_role()
        perm = IsInstructor()
        assert perm.has_permission(make_request(user), None) is False

    def test_directivo_rejected_for_instructor_role_only(self):
        """IsDirectivo solo acepta directivo/admin, no instructor puro."""
        user = MagicMock()
        user.is_authenticated = True
        user.is_superuser = False
        # Simula que el usuario tiene solo "instructor", no "directivo" ni "admin"
        user_roles = ["instructor"]
        def mock_filter(**kwargs):
            names = kwargs.get("name__in", [])
            mock = MagicMock()
            # Retorna True si ALGÚN rol del usuario está en los nombres buscados
            mock.exists.return_value = any(role in names for role in user_roles)
            return mock
        user.groups.filter.side_effect = mock_filter
        perm = IsDirectivo()
        assert perm.has_permission(make_request(user), None) is False

    def test_unauthenticated_user_denied(self):
        user = MagicMock()
        user.is_authenticated = False
        user.is_superuser = False
        for perm_class in [IsInstructor, IsDirectivo, IsEstudiante, IsAdmin]:
            perm = perm_class()
            assert perm.has_permission(make_request(user), None) is False

    def test_superuser_bypasses_all_role_checks(self):
        user = MagicMock()
        user.is_authenticated = True
        user.is_superuser = True
        for perm_class in [IsInstructor, IsDirectivo, IsSubdirector, IsComunicador]:
            perm = perm_class()
            assert perm.has_permission(make_request(user), None) is True


# ─── Tests de permisos a nivel de objeto ──────────────────────────────────────

class TestObjectLevelPermissions:
    """
    Verifica los 3 patrones de permisos a nivel de objeto (tesis §2.6.3).
    Protegen contra BOLA (Broken Object Level Authorization).
    """

    # ── Patrón 1: IsOwner ────────────────────────────────────────────────────

    def test_is_owner_safe_methods_allowed_for_any_authenticated(self):
        for method in ["GET", "HEAD", "OPTIONS"]:
            request = MagicMock()
            request.method = method
            request.user = MagicMock(is_authenticated=True)
            obj = MagicMock()
            perm = IsOwner()
            assert perm.has_object_permission(request, None, obj) is True

    def test_is_owner_write_allowed_for_owner(self):
        user = MagicMock()
        obj  = MagicMock()
        obj.user = user
        request = MagicMock()
        request.method = "PATCH"
        request.user = user
        assert IsOwner().has_object_permission(request, None, obj) is True

    def test_is_owner_write_denied_for_other_user(self):
        owner   = MagicMock()
        other   = MagicMock()
        obj     = MagicMock()
        obj.user = owner
        request = MagicMock()
        request.method = "DELETE"
        request.user = other
        assert IsOwner().has_object_permission(request, None, obj) is False

    def test_is_owner_denied_when_obj_has_no_user_field(self):
        request = MagicMock()
        request.method = "PATCH"
        obj = MagicMock(spec=[])  # sin atributo 'user'
        assert IsOwner().has_object_permission(request, None, obj) is False

    # ── Patrón 2: IsStudentOwner ─────────────────────────────────────────────

    def test_is_student_owner_write_allowed_for_student(self):
        user    = MagicMock()
        student = MagicMock()
        student.user = user
        obj = MagicMock()
        obj.student = student
        request = MagicMock()
        request.method = "PATCH"
        request.user = user
        assert IsStudentOwner().has_object_permission(request, None, obj) is True

    def test_is_student_owner_write_denied_for_other_student(self):
        user1   = MagicMock()
        user2   = MagicMock()
        student = MagicMock()
        student.user = user1
        obj = MagicMock()
        obj.student = student
        request = MagicMock()
        request.method = "DELETE"
        request.user = user2
        assert IsStudentOwner().has_object_permission(request, None, obj) is False

    # ── Patrón 3: IsAssignedBy ───────────────────────────────────────────────

    def test_is_assigned_by_allowed_for_creator(self):
        user = MagicMock()
        obj  = MagicMock()
        obj.assigned_by = user
        request = MagicMock()
        request.method = "PATCH"
        request.user = user
        assert IsAssignedBy().has_object_permission(request, None, obj) is True

    def test_is_assigned_by_denied_for_non_creator(self):
        creator = MagicMock()
        other   = MagicMock()
        obj     = MagicMock()
        obj.assigned_by = creator
        request = MagicMock()
        request.method = "PATCH"
        request.user = other
        assert IsAssignedBy().has_object_permission(request, None, obj) is False

    # ── IsStudentOwnerOrInstructor ────────────────────────────────────────────

    def test_instructor_has_full_access_to_any_object(self):
        user = MagicMock()
        user.is_authenticated = True
        user.is_superuser = False
        user.groups.filter.return_value.exists.return_value = True

        obj = MagicMock()
        request = MagicMock()
        request.method = "DELETE"
        request.user = user

        perm = IsStudentOwnerOrInstructor()
        assert perm.has_object_permission(request, None, obj) is True

    def test_student_owner_can_access_own_object(self):
        user    = MagicMock()
        user.is_authenticated = True
        user.is_superuser = False
        user.groups.filter.return_value.exists.return_value = False  # no instructor

        student = MagicMock()
        student.user = user
        obj = MagicMock()
        obj.student = student

        request = MagicMock()
        request.method = "PATCH"
        request.user = user

        perm = IsStudentOwnerOrInstructor()
        assert perm.has_object_permission(request, None, obj) is True

    def test_other_student_denied_access(self):
        user1   = MagicMock()
        user2   = MagicMock()
        user2.is_authenticated = True
        user2.is_superuser = False
        user2.groups.filter.return_value.exists.return_value = False

        student = MagicMock()
        student.user = user1
        obj = MagicMock()
        obj.student = student

        request = MagicMock()
        request.method = "PATCH"
        request.user = user2

        perm = IsStudentOwnerOrInstructor()
        assert perm.has_object_permission(request, None, obj) is False
