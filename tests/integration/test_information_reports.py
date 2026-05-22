import pytest
from django.urls import reverse
from rest_framework import status
from apps.operations.models import Information


@pytest.mark.django_db
class TestInformation:

    def test_comunicador_can_create_information(self, client_comunicador):
        """RF-50: comunicador publica noticia."""
        url      = reverse("information-list")
        response = client_comunicador.post(url, {
            "title":     "Aviso importante sobre horario de comedor",
            "content":   "El comedor cambia su horario a partir del lunes.",
            "is_public": True,
        }, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["title"] == "Aviso importante sobre horario de comedor"

    def test_created_by_set_automatically(self, client_comunicador, user_comunicador):
        url = reverse("information-list")
        client_comunicador.post(url, {
            "title": "Test auto-assign", "content": "Contenido de prueba.", "is_public": True,
        }, format="json")
        info = Information.objects.last()
        assert info.created_by == user_comunicador

    def test_instructor_cannot_create_information(self, client_instructor):
        url      = reverse("information-list")
        response = client_instructor.post(url, {
            "title": "Intento de instructor", "content": "...", "is_public": True,
        }, format="json")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_student_can_see_public_information(self, client_estudiante, user_comunicador):
        """RF-55: estudiantes ven informaciones públicas no expiradas."""
        Information.objects.create(
            title="Pública vigente", content="...",
            is_public=True, created_by=user_comunicador,
        )
        Information.objects.create(
            title="No pública", content="...",
            is_public=False, created_by=user_comunicador,
        )
        url      = reverse("information-publicas")
        response = client_estudiante.get(url)
        assert response.status_code == status.HTTP_200_OK
        titles = [i["title"] for i in response.data["results"]]
        assert "Pública vigente" in titles
        assert "No pública" not in titles

    def test_public_serializer_hides_management_fields(
        self, client_estudiante, user_comunicador
    ):
        """Los estudiantes no ven created_by ni is_public en /publicas/."""
        Information.objects.create(
            title="Info pública", content="Contenido.",
            is_public=True, created_by=user_comunicador,
        )
        url      = reverse("information-publicas")
        response = client_estudiante.get(url)
        first    = response.data["results"][0]
        assert "created_by"  not in first
        assert "is_public"   not in first

    def test_partial_update_information(self, client_comunicador, user_comunicador):
        """RF-53: actualizar información."""
        info = Information.objects.create(
            title="Original", content="Contenido original.",
            is_public=True, created_by=user_comunicador,
        )
        url      = reverse("information-detail", kwargs={"pk": info.pk})
        response = client_comunicador.patch(url, {"title": "Título actualizado"}, format="json")
        assert response.status_code == status.HTTP_200_OK
        info.refresh_from_db()
        assert info.title == "Título actualizado"


@pytest.mark.django_db
class TestReports:

    def test_directivo_can_create_report(self, client_directivo):
        """RF-56: solicitar generación de reporte."""
        url      = reverse("report-list")
        response = client_directivo.post(url, {
            "name":       "Reporte de ocupación mensual",
            "type":       "ocupacion",
            "parameters": {"month": "2024-03", "site_id": 1},
        }, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["name"] == "Reporte de ocupación mensual"
        assert response.data["generated_by"] is not None

    def test_report_list(self, client_directivo):
        """RF-58: listar reportes generados."""
        url      = reverse("report-list")
        response = client_directivo.get(url)
        assert response.status_code == status.HTTP_200_OK

    def test_instructor_cannot_access_reports(self, client_instructor):
        url      = reverse("report-list")
        response = client_instructor.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_student_cannot_access_reports(self, client_estudiante):
        url      = reverse("report-list")
        response = client_estudiante.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN
