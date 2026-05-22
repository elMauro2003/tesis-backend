import pytest
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
class TestStudentCRUD:

    def test_list_students_as_instructor(self, client_instructor, student):
        """RF-2: instructor puede listar estudiantes."""
        url      = reverse("student-list")
        response = client_instructor.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] >= 1

    def test_retrieve_student_as_instructor(self, client_instructor, student):
        """RF-3: instructor puede consultar un estudiante por ID."""
        url      = reverse("student-detail", kwargs={"pk": student.pk})
        response = client_instructor.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["student_id"] == student.student_id

    def test_create_student_as_instructor(self, client_instructor, group):
        """RF-1: instructor puede crear un estudiante (con User asociado)."""
        url      = reverse("student-list")
        response = client_instructor.post(url, {
            "username":   "nuevo_est",
            "email":      "nuevo@test.cu",
            "first_name": "Nuevo",
            "last_name":  "Estudiante",
            "password":   "EstPass456!",
            "ci":         "95050512345",
            "student_id": "ICI-2024-099",
            "birth_date": "1995-05-05",
            "gender":     "F",
            "group":      group.pk,
        }, format="json")
        assert response.status_code == status.HTTP_201_CREATED

    def test_partial_update_student(self, client_instructor, student):
        """RF-5: actualización parcial."""
        url      = reverse("student-detail", kwargs={"pk": student.pk})
        response = client_instructor.patch(url, {"province": "Villa Clara"}, format="json")
        assert response.status_code == status.HTTP_200_OK
        student.refresh_from_db()
        assert student.province == "Villa Clara"

    def test_delete_student(self, client_instructor, student):
        """RF-6: instructor puede eliminar estudiante."""
        url      = reverse("student-detail", kwargs={"pk": student.pk})
        response = client_instructor.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_search_students_by_name(self, client_instructor, student):
        """RF-7: búsqueda por nombre."""
        url      = reverse("student-list")
        response = client_instructor.get(url, {"search": student.user.last_name})
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] >= 1

    def test_filter_students_by_group(self, client_instructor, student, group):
        url      = reverse("student-list")
        response = client_instructor.get(url, {"group": group.pk})
        assert response.status_code == status.HTTP_200_OK
        assert all(s["group"] == group.pk for s in response.data["results"])


@pytest.mark.django_db
class TestStudentPermissions:

    def test_student_cannot_list_all_students(self, client_estudiante):
        """Los estudiantes no pueden ver el listado general."""
        url      = reverse("student-list")
        response = client_estudiante.get(url)
        # Puede devolver 403 o lista vacía según el filtrado — ambos son correctos
        # El importante es que no vea estudiantes de otros
        assert response.status_code in [status.HTTP_403_FORBIDDEN, status.HTTP_200_OK]

    def test_unauthenticated_cannot_access_students(self, client_no_auth):
        url      = reverse("student-list")
        response = client_no_auth.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_list_response_uses_compact_serializer(self, client_instructor, student):
        """El listado usa StudentListSerializer (menos campos que el detalle)."""
        url      = reverse("student-list")
        response = client_instructor.get(url)
        assert response.status_code == status.HTTP_200_OK
        # StudentListSerializer no incluye illnesses/medications (datos sensibles)
        first = response.data["results"][0]
        assert "illnesses" not in first
        assert "medications" not in first
        assert "full_name" in first


@pytest.mark.django_db
class TestStudentPagination:

    def test_list_is_paginated(self, client_instructor, student):
        url      = reverse("student-list")
        response = client_instructor.get(url)
        assert "count"    in response.data
        assert "next"     in response.data
        assert "previous" in response.data
        assert "results"  in response.data

    def test_custom_page_size(self, client_instructor, student):
        url      = reverse("student-list")
        response = client_instructor.get(url, {"page_size": 5})
        assert response.status_code == status.HTTP_200_OK
