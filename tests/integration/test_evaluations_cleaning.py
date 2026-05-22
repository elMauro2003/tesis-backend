import pytest
from django.urls import reverse
from rest_framework import status
from apps.operations.models import Evaluation, CleaningSchedule


@pytest.mark.django_db
class TestEvaluations:

    def test_instructor_can_create_evaluation(self, client_instructor, student):
        """RF-8: instructor añade evaluación."""
        url      = reverse("evaluation-list")
        response = client_instructor.post(url, {
            "student": student.pk,
            "date":    "2024-03-15",
            "grade":   "B",
            "comment": "Excelente comportamiento y cumplimiento.",
        }, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["grade"] == "B"
        assert response.data["grade_display"] == "Bien"

    def test_created_by_is_set_automatically(self, client_instructor, student, user_instructor):
        url = reverse("evaluation-list")
        client_instructor.post(url, {
            "student": student.pk, "date": "2024-03-15", "grade": "R",
        }, format="json")
        ev = Evaluation.objects.last()
        assert ev.created_by == user_instructor

    def test_invalid_grade_returns_400(self, client_instructor, student):
        url      = reverse("evaluation-list")
        response = client_instructor.post(url, {
            "student": student.pk, "date": "2024-03-15", "grade": "X",
        }, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_student_can_view_own_evaluations(self, client_estudiante, student, user_instructor):
        """RF-13: estudiante consulta sus propias evaluaciones."""
        Evaluation.objects.create(
            student=student, date="2024-03-15",
            grade="B", created_by=user_instructor,
        )
        url      = reverse("evaluation-mis-evaluaciones")
        response = client_estudiante.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] >= 1

    def test_student_cannot_create_evaluation(self, client_estudiante, student):
        url      = reverse("evaluation-list")
        response = client_estudiante.post(url, {
            "student": student.pk, "date": "2024-03-15", "grade": "B",
        }, format="json")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_instructor_can_update_evaluation(self, client_instructor, student, user_instructor):
        """RF-11: actualización parcial."""
        ev  = Evaluation.objects.create(
            student=student, date="2024-03-15",
            grade="R", created_by=user_instructor,
        )
        url      = reverse("evaluation-detail", kwargs={"pk": ev.pk})
        response = client_instructor.patch(url, {"grade": "B", "comment": "Mejoró."}, format="json")
        assert response.status_code == status.HTTP_200_OK
        ev.refresh_from_db()
        assert ev.grade == "B"


@pytest.mark.django_db
class TestCleaningSchedule:

    def test_instructor_can_create_cleaning_task(self, client_instructor, student, room):
        """RF-67: crear cuartelería."""
        url      = reverse("cleaning-list")
        response = client_instructor.post(url, {
            "room":          room.pk,
            "student":       student.pk,
            "assigned_date": "2024-04-01",
        }, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["completed"] is False

    def test_student_can_view_own_cleaning_tasks(self, client_estudiante, student, room):
        """RF-69: mis cuartelerías."""
        CleaningSchedule.objects.create(
            room=room, student=student, assigned_date="2024-04-01"
        )
        url      = reverse("cleaning-mis-cuartelerias")
        response = client_estudiante.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] >= 1

    def test_mark_cleaning_complete(self, client_instructor, student, room):
        """RF-70: marcar como completada con evaluación."""
        task = CleaningSchedule.objects.create(
            room=room, student=student, assigned_date="2024-04-01"
        )
        url      = reverse("cleaning-completar", kwargs={"pk": task.pk})
        response = client_instructor.patch(url, {
            "evaluation": "B",
            "comments":   "Cuarto en excelentes condiciones.",
        }, format="json")
        assert response.status_code == status.HTTP_200_OK
        task.refresh_from_db()
        assert task.completed  is True
        assert task.evaluation == "B"

    def test_filter_cleaning_by_room(self, client_instructor, student, room):
        """RF-68: filtrar cuartelerías por ala/cuarto."""
        CleaningSchedule.objects.create(
            room=room, student=student, assigned_date="2024-04-01"
        )
        url      = reverse("cleaning-list")
        response = client_instructor.get(url, {"room": room.pk})
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] >= 1
