import pytest
from django.urls import reverse
from rest_framework import status
from apps.operations.models import Complaint


@pytest.mark.django_db
class TestComplaintCreate:
    """RF-14: POST /api/v1/quejas/"""

    def test_student_can_create_complaint(self, client_estudiante, student):
        url      = reverse("complaint-list")
        response = client_estudiante.post(url, {
            "description": "El agua caliente no funciona desde hace 3 días.",
            "type":        "administrativa",
        }, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["student"] == student.pk
        assert response.data["status"]  == "pendiente"
        assert response.data["visibility"] is False

    def test_complaint_auto_assigns_to_authenticated_student(
        self, client_estudiante, student
    ):
        """El student se toma del usuario autenticado, no del body."""
        url = reverse("complaint-list")
        client_estudiante.post(url, {
            "description": "Queja de prueba",
            "type":        "educativa",
        }, format="json")

        complaint = Complaint.objects.last()
        assert complaint.student == student

    def test_instructor_cannot_create_complaint(self, client_instructor):
        """Solo estudiantes pueden crear quejas."""
        url      = reverse("complaint-list")
        response = client_instructor.post(url, {
            "description": "Intento de instructor",
            "type":        "administrativa",
        }, format="json")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_unauthenticated_cannot_create_complaint(self, client_no_auth):
        url      = reverse("complaint-list")
        response = client_no_auth.post(url, {
            "description": "Intento anónimo",
            "type":        "administrativa",
        }, format="json")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestComplaintAccess:
    """RF-15, RF-16, RF-19, RF-20: Acceso a quejas según rol."""

    def _create_complaint(self, student):
        return Complaint.objects.create(
            student=student,
            description="Queja de prueba",
            type="administrativa",
            status="pendiente",
        )

    def test_student_sees_only_own_complaints(
        self, client_estudiante, student, group, user_instructor
    ):
        """Un estudiante no puede ver las quejas de otros."""
        from django.contrib.auth import get_user_model
        from apps.actors.models import Student
        User = get_user_model()

        # Crear otro estudiante y su queja
        u2 = User.objects.create_user(username="otro_stu", password="Pass123!")
        s2 = Student.objects.create(
            user=u2, ci="88888888888", student_id="OTHER-001",
            birth_date="2000-01-01", gender="F", group=group,
        )
        self._create_complaint(s2)  # queja de otro estudiante

        url      = reverse("complaint-mis-quejas")
        response = client_estudiante.get(url)
        assert response.status_code == status.HTTP_200_OK
        # El estudiante no tiene quejas propias → lista vacía
        assert response.data["count"] == 0

    def test_subdirector_sees_all_complaints(
        self, client_subdirector, student
    ):
        self._create_complaint(student)
        url      = reverse("complaint-list")
        response = client_subdirector.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] >= 1

    def test_visible_complaints_endpoint(self, client_estudiante, student):
        """RF-19: estudiantes ven quejas con visibility=True."""
        Complaint.objects.create(
            student=student, description="Queja pública",
            type="administrativa", visibility=True,
        )
        Complaint.objects.create(
            student=student, description="Queja privada",
            type="administrativa", visibility=False,
        )
        url      = reverse("complaint-visibles")
        response = client_estudiante.get(url)
        assert response.status_code == status.HTTP_200_OK
        descriptions = [c["description"] for c in response.data["results"]]
        assert "Queja pública" in descriptions
        assert "Queja privada" not in descriptions


@pytest.mark.django_db
class TestComplaintWorkflow:
    """RF-22, RF-23, RF-24: Acciones del subdirector sobre quejas."""

    def _complaint(self, student):
        return Complaint.objects.create(
            student=student, description="Queja test",
            type="administrativa", status="pendiente",
        )

    def test_subdirector_can_change_status(self, client_subdirector, student):
        complaint = self._complaint(student)
        url       = reverse("complaint-estado", kwargs={"pk": complaint.pk})
        response  = client_subdirector.patch(url, {"status": "en_proceso"}, format="json")

        assert response.status_code == status.HTTP_200_OK
        complaint.refresh_from_db()
        assert complaint.status == "en_proceso"

    def test_invalid_status_returns_400(self, client_subdirector, student):
        complaint = self._complaint(student)
        url       = reverse("complaint-estado", kwargs={"pk": complaint.pk})
        response  = client_subdirector.patch(url, {"status": "inventado"}, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_subdirector_can_respond_to_complaint(self, client_subdirector, student):
        """RF-23: Responder una queja."""
        complaint = self._complaint(student)
        url       = reverse("complaint-respuesta", kwargs={"pk": complaint.pk})
        response  = client_subdirector.post(
            url,
            {"response": "Su queja ha sido atendida y el problema fue solucionado."},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        complaint.refresh_from_db()
        assert complaint.response is not None
        assert complaint.response_date is not None
        assert complaint.status == "resuelta"

    def test_response_too_short_returns_400(self, client_subdirector, student):
        complaint = self._complaint(student)
        url       = reverse("complaint-respuesta", kwargs={"pk": complaint.pk})
        response  = client_subdirector.post(url, {"response": "OK"}, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_subdirector_can_toggle_visibility(self, client_subdirector, student):
        """RF-24: Cambiar visibilidad de una queja."""
        complaint = self._complaint(student)
        assert complaint.visibility is False

        url      = reverse("complaint-visibilidad", kwargs={"pk": complaint.pk})
        response = client_subdirector.patch(url, {"visibility": True}, format="json")

        assert response.status_code == status.HTTP_200_OK
        complaint.refresh_from_db()
        assert complaint.visibility is True

    def test_student_cannot_change_status(self, client_estudiante, student):
        """Solo subdirector puede cambiar estado."""
        complaint = self._complaint(student)
        url       = reverse("complaint-estado", kwargs={"pk": complaint.pk})
        response  = client_estudiante.patch(url, {"status": "resuelta"}, format="json")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_instructor_cannot_respond_complaint(self, client_instructor, student):
        complaint = self._complaint(student)
        url       = reverse("complaint-respuesta", kwargs={"pk": complaint.pk})
        response  = client_instructor.post(
            url, {"response": "Respuesta de instructor no autorizada"}, format="json"
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
