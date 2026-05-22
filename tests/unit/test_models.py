import pytest
from django.db import IntegrityError


# ─── Room ────────────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestRoomModel:
    def test_is_full_false_when_below_capacity(self, room):
        assert room.is_full is False

    def test_is_full_true_when_at_capacity(self, room_full):
        assert room_full.is_full is True

    def test_available_spots_calculation(self, room):
        # capacity=4, current_occupancy=0 → 4 spots
        assert room.available_spots == 4

    def test_available_spots_zero_when_full(self, room_full):
        assert room_full.available_spots == 0

    def test_str_representation(self, room, wing):
        assert room.number in str(room)
        assert wing.name in str(room)

    def test_unique_constraint_wing_number(self, wing):
        """No pueden existir dos cuartos con el mismo número en el mismo ala."""
        from apps.infrastructure.models import Room
        Room.objects.create(wing=wing, number="202", capacity=3)
        with pytest.raises(IntegrityError):
            Room.objects.create(wing=wing, number="202", capacity=2)

    def test_capacity_must_be_positive(self, wing):
        """capacity=0 debe violar el CHECK constraint."""
        from apps.infrastructure.models import Room
        with pytest.raises(Exception):  # IntegrityError o ValidationError según el backend
            r = Room(wing=wing, number="000", capacity=0)
            r.full_clean()  # Dispara validación a nivel de modelo


# ─── Wing ────────────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestWingModel:
    def test_unique_constraint_building_name(self, building):
        """No pueden existir dos alas con el mismo nombre en el mismo edificio."""
        from apps.infrastructure.models import Wing
        Wing.objects.create(building=building, name="Norte")
        with pytest.raises(IntegrityError):
            Wing.objects.create(building=building, name="Norte")

    def test_same_name_allowed_in_different_buildings(self, site):
        """El mismo nombre de ala es válido en edificios distintos."""
        from apps.infrastructure.models import Building, Wing
        b1 = Building.objects.create(site=site, name="Edif-10")
        b2 = Building.objects.create(site=site, name="Edif-11")
        Wing.objects.create(building=b1, name="Sur")
        # No debe lanzar excepción
        Wing.objects.create(building=b2, name="Sur")


# ─── CareerYear ───────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestCareerYearModel:
    def test_unique_constraint_career_year(self, career):
        """No pueden existir dos "3er año" de la misma carrera."""
        from apps.academic.models import CareerYear
        CareerYear.objects.create(career=career, year=1)
        with pytest.raises(IntegrityError):
            CareerYear.objects.create(career=career, year=1)

    def test_same_year_allowed_in_different_careers(self, faculty):
        """El mismo año (ej: 1) es válido en carreras distintas."""
        from apps.academic.models import Career, CareerYear
        c1 = Career.objects.create(name="Carrera A", faculty=faculty)
        c2 = Career.objects.create(name="Carrera B", faculty=faculty)
        CareerYear.objects.create(career=c1, year=1)
        CareerYear.objects.create(career=c2, year=1)  # No debe fallar


# ─── Student ─────────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestStudentModel:
    def test_full_name_delegates_to_user(self, student):
        expected = student.user.get_full_name()
        assert student.full_name == expected

    def test_active_assignment_none_when_no_assignment(self, student):
        assert student.active_assignment is None

    def test_current_room_none_when_no_assignment(self, student):
        assert student.current_room is None

    def test_str_contains_student_id(self, student):
        assert student.student_id in str(student)

    def test_str_contains_full_name(self, student):
        assert student.full_name in str(student)

    def test_student_id_must_be_unique(self, db, group):
        """Dos estudiantes no pueden tener el mismo student_id."""
        from apps.actors.models import Student
        from django.contrib.auth import get_user_model
        from django.db import connection
        User = get_user_model()

        # Enable UNIQUE constraints in SQLite for this test
        if connection.vendor == 'sqlite':
            with connection.cursor() as cursor:
                cursor.execute("PRAGMA constraint_check_order=ON")

        user1 = User.objects.create_user(username="student1", password="Pass123!")
        # Create first student
        Student.objects.create(
            user=user1, ci="99999999998",
            student_id="ICI-2020-001",
            birth_date="2001-01-01", gender="F", group=group,
        )

        # Intentar crear otro con el mismo student_id
        user2 = User.objects.create_user(username="dup_student", password="Pass123!")
        with pytest.raises(IntegrityError):
            Student.objects.create(
                user=user2, ci="99999999999",
                student_id="ICI-2020-001",  # duplicado
                birth_date="2001-01-01", gender="F", group=group,
            )


# ─── Assignment ───────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestAssignmentModel:
    def test_is_active_true_when_no_release_date(self, student, room, user_instructor):
        from apps.operations.models import Assignment
        a = Assignment.objects.create(
            student=student, room=room,
            assigned_date="2024-01-15", assigned_by=user_instructor,
        )
        assert a.is_active is True

    def test_is_active_false_when_released(self, student, room, user_instructor):
        from apps.operations.models import Assignment
        a = Assignment.objects.create(
            student=student, room=room,
            assigned_date="2024-01-15",
            released_date="2024-06-30",
            assigned_by=user_instructor,
        )
        assert a.is_active is False

    def test_str_contains_active_label(self, student, room, user_instructor):
        from apps.operations.models import Assignment
        a = Assignment.objects.create(
            student=student, room=room,
            assigned_date="2024-01-15", assigned_by=user_instructor,
        )
        assert "ACTIVA" in str(a)


# ─── Exception handlers ───────────────────────────────────────────────────────

class TestCustomExceptionHandler:
    """
    Tests del custom_exception_handler de core/exceptions.py.
    Sin BD — solo verificamos la transformación del formato.
    """

    def test_404_becomes_not_found_code(self):
        from core.exceptions import custom_exception_handler
        from rest_framework.exceptions import NotFound

        exc      = NotFound("No encontrado")
        context  = {"view": None, "request": None}
        response = custom_exception_handler(exc, context)

        assert response.status_code == 404
        assert response.data["error"]["code"] == "NOT_FOUND"
        assert "message" in response.data["error"]

    def test_403_becomes_permission_denied(self):
        from core.exceptions import custom_exception_handler
        from rest_framework.exceptions import PermissionDenied

        exc      = PermissionDenied("Acceso denegado")
        context  = {"view": None, "request": None}
        response = custom_exception_handler(exc, context)

        assert response.status_code == 403
        assert response.data["error"]["code"] == "PERMISSION_DENIED"

    def test_validation_error_includes_details(self):
        from core.exceptions import custom_exception_handler
        from rest_framework.exceptions import ValidationError

        exc      = ValidationError({"email": ["El email ya existe."]})
        context  = {"view": None, "request": None}
        response = custom_exception_handler(exc, context)

        assert response.status_code == 400
        assert response.data["error"]["code"] == "VALIDATION_ERROR"
        assert "details" in response.data["error"]
        assert "email" in response.data["error"]["details"]

    def test_non_drf_exception_returns_none(self):
        """Excepciones que no son de DRF retornan None (Django las maneja)."""
        from core.exceptions import custom_exception_handler

        exc      = ValueError("error interno")
        context  = {"view": None, "request": None}
        response = custom_exception_handler(exc, context)
        assert response is None
