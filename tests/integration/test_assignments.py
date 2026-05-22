import pytest
from django.urls import reverse
from rest_framework import status
from apps.operations.models import Assignment
from apps.infrastructure.models import Room


@pytest.mark.django_db
class TestAssignmentCreate:
    """RF-45: POST /api/v1/asignaciones/"""

    def test_create_assignment_success(self, client_instructor, student, room):
        url = reverse("assignment-list")
        response = client_instructor.post(url, {
            "student":       student.pk,
            "room":          room.pk,
            "assigned_date": "2024-03-01",
        }, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["student"] == student.pk
        assert response.data["room"]    == room.pk
        assert response.data["is_active"] is True

    def test_create_assignment_updates_room_occupancy(self, client_instructor, student, room):
        """La señal debe incrementar current_occupancy del cuarto."""
        assert room.current_occupancy == 0

        url = reverse("assignment-list")
        client_instructor.post(url, {
            "student": student.pk, "room": room.pk, "assigned_date": "2024-03-01",
        }, format="json")

        room.refresh_from_db()
        assert room.current_occupancy == 1

    def test_cannot_assign_student_with_active_assignment(
        self, client_instructor, student, room, wing, user_instructor
    ):
        """Un estudiante no puede tener dos asignaciones activas."""
        # Primera asignación
        Assignment.objects.create(
            student=student, room=room,
            assigned_date="2024-01-01", assigned_by=user_instructor,
        )
        # Segundo cuarto
        room2 = Room.objects.create(wing=wing, number="102", capacity=3)

        url = reverse("assignment-list")
        response = client_instructor.post(url, {
            "student": student.pk, "room": room2.pk, "assigned_date": "2024-03-01",
        }, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "student" in response.data["error"]["details"]

    def test_cannot_assign_to_full_room(self, client_instructor, student, room_full):
        """No se puede asignar a un cuarto lleno."""
        url = reverse("assignment-list")
        response = client_instructor.post(url, {
            "student": student.pk, "room": room_full.pk, "assigned_date": "2024-03-01",
        }, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "room" in response.data["error"]["details"]

    def test_cannot_assign_to_inactive_room(self, client_instructor, student, wing):
        """No se puede asignar a un cuarto deshabilitado."""
        inactive_room = Room.objects.create(
            wing=wing, number="999", capacity=4, is_active=False
        )
        url = reverse("assignment-list")
        response = client_instructor.post(url, {
            "student": student.pk, "room": inactive_room.pk, "assigned_date": "2024-03-01",
        }, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_student_cannot_create_assignment(self, client_estudiante, student, room):
        """Los estudiantes no tienen permiso para crear asignaciones."""
        url = reverse("assignment-list")
        response = client_estudiante.post(url, {
            "student": student.pk, "room": room.pk, "assigned_date": "2024-03-01",
        }, format="json")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_unauthenticated_cannot_create_assignment(self, client_no_auth, student, room):
        url = reverse("assignment-list")
        response = client_no_auth.post(url, {
            "student": student.pk, "room": room.pk, "assigned_date": "2024-03-01",
        }, format="json")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestAssignmentRelease:
    """RF-49: POST /api/v1/asignaciones/{id}/liberar/"""

    def _create_assignment(self, student, room, user_instructor):
        return Assignment.objects.create(
            student=student, room=room,
            assigned_date="2024-01-15", assigned_by=user_instructor,
        )

    def test_release_active_assignment_success(
        self, client_instructor, student, room, user_instructor
    ):
        assignment = self._create_assignment(student, room, user_instructor)
        url        = reverse("assignment-liberar", kwargs={"pk": assignment.pk})
        response   = client_instructor.post(url, {"released_date": "2024-06-30"}, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["is_active"] is False
        assert response.data["released_date"] == "2024-06-30"

    def test_release_decrements_room_occupancy(
        self, client_instructor, student, room, user_instructor
    ):
        """Liberar la asignación debe decrementar current_occupancy."""
        assignment = self._create_assignment(student, room, user_instructor)
        room.refresh_from_db()
        assert room.current_occupancy == 1

        url = reverse("assignment-liberar", kwargs={"pk": assignment.pk})
        client_instructor.post(url, {"released_date": "2024-06-30"}, format="json")

        room.refresh_from_db()
        assert room.current_occupancy == 0

    def test_cannot_release_already_released_assignment(
        self, client_instructor, student, room, user_instructor
    ):
        assignment = Assignment.objects.create(
            student=student, room=room,
            assigned_date="2024-01-15",
            released_date="2024-03-01",
            assigned_by=user_instructor,
        )
        url      = reverse("assignment-liberar", kwargs={"pk": assignment.pk})
        response = client_instructor.post(url, {"released_date": "2024-06-30"}, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_active_assignments_list(self, client_instructor, student, room, user_instructor):
        """RF-46: solo aparecen asignaciones activas."""
        # Una activa, una liberada
        a_active = self._create_assignment(student, room, user_instructor)
        Assignment.objects.filter(pk=a_active.pk).update(released_date=None)

        url      = reverse("assignment-activas")
        response = client_instructor.get(url)
        assert response.status_code == status.HTTP_200_OK
        ids = [item["id"] for item in response.data["results"]]
        assert a_active.pk in ids


@pytest.mark.django_db
class TestOccupancySignal:
    """
    Tests específicos de la señal que sincroniza current_occupancy.
    Valida que el equivalente al trigger PG funciona correctamente.
    """

    def test_occupancy_increments_on_assignment_create(
        self, student, room, user_instructor
    ):
        assert room.current_occupancy == 0
        Assignment.objects.create(
            student=student, room=room,
            assigned_date="2024-01-01", assigned_by=user_instructor,
        )
        room.refresh_from_db()
        assert room.current_occupancy == 1

    def test_occupancy_decrements_on_assignment_release(
        self, student, room, user_instructor
    ):
        a = Assignment.objects.create(
            student=student, room=room,
            assigned_date="2024-01-01", assigned_by=user_instructor,
        )
        room.refresh_from_db()
        assert room.current_occupancy == 1

        a.released_date = "2024-06-01"
        a.save()
        room.refresh_from_db()
        assert room.current_occupancy == 0

    def test_occupancy_decrements_on_assignment_delete(
        self, student, room, user_instructor
    ):
        a = Assignment.objects.create(
            student=student, room=room,
            assigned_date="2024-01-01", assigned_by=user_instructor,
        )
        room.refresh_from_db()
        assert room.current_occupancy == 1

        a.delete()
        room.refresh_from_db()
        assert room.current_occupancy == 0

    def test_multiple_students_same_room(self, group, room, user_instructor):
        """Un cuarto con capacidad 4 puede tener hasta 4 asignaciones activas."""
        from django.contrib.auth import get_user_model
        from apps.actors.models import Student

        User = get_user_model()
        students = []
        for i in range(3):
            u = User.objects.create_user(username=f"stu{i}", password="Pass123!")
            s = Student.objects.create(
                user=u, ci=f"9000000000{i}", student_id=f"TEST-00{i}",
                birth_date="2000-01-01", gender="M", group=group,
            )
            students.append(s)
            Assignment.objects.create(
                student=s, room=room,
                assigned_date="2024-01-01", assigned_by=user_instructor,
            )

        room.refresh_from_db()
        assert room.current_occupancy == 3
        assert room.is_full is False  # capacity=4
        assert room.available_spots == 1
