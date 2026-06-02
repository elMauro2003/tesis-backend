import pytest
from django.urls import reverse
from django.contrib.auth.models import Group
from rest_framework import status


@pytest.mark.django_db
class TestProfessorGroupAssignment:
    """Tests para asignación de grupos (roles) a profesores."""

    def test_get_professor_groups(self, client_directivo, professor):
        """GET /profesores/{id}/grupos/ - debe listar grupos del usuario profesor."""
        url = reverse("professor-assign-groups", kwargs={"pk": professor.pk})
        response = client_directivo.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert "groups" in response.data
        assert isinstance(response.data["groups"], list)

    def test_assign_single_group_to_professor(self, client_directivo, professor):
        """POST /profesores/{id}/grupos/ - asignar un solo grupo."""
        url = reverse("professor-assign-groups", kwargs={"pk": professor.pk})
        data = {"groups": ["directivo"]}
        response = client_directivo.post(url, data, format="json")
        
        assert response.status_code == status.HTTP_200_OK
        assert "groups" in response.data
        assert "directivo" in response.data["groups"]
        
        # Verificar que el usuario tiene el grupo
        professor.user.refresh_from_db()
        assert professor.user.groups.filter(name="directivo").exists()

    def test_assign_multiple_groups_to_professor(self, client_directivo, professor):
        """POST /profesores/{id}/grupos/ - asignar múltiples grupos."""
        url = reverse("professor-assign-groups", kwargs={"pk": professor.pk})
        data = {"groups": ["directivo", "instructor", "comunicador"]}
        response = client_directivo.post(url, data, format="json")
        
        assert response.status_code == status.HTTP_200_OK
        assert set(response.data["groups"]) == {"directivo", "instructor", "comunicador"}
        
        # Verificar que el usuario tiene todos los grupos
        professor.user.refresh_from_db()
        user_groups = set(professor.user.groups.values_list("name", flat=True))
        assert user_groups == {"directivo", "instructor", "comunicador"}

    def test_assign_groups_replaces_previous(self, client_directivo, professor):
        """POST /profesores/{id}/grupos/ - nueva asignación reemplaza la anterior."""
        url = reverse("professor-assign-groups", kwargs={"pk": professor.pk})
        
        # Asignar primeros grupos
        response1 = client_directivo.post(url, {"groups": ["directivo", "instructor"]}, format="json")
        assert response1.status_code == status.HTTP_200_OK
        
        # Asignar nuevos grupos (debe reemplazar)
        response2 = client_directivo.post(url, {"groups": ["subdirector"]}, format="json")
        assert response2.status_code == status.HTTP_200_OK
        assert response2.data["groups"] == ["subdirector"]
        
        # Verificar que solo tiene el nuevo grupo
        professor.user.refresh_from_db()
        user_groups = set(professor.user.groups.values_list("name", flat=True))
        assert user_groups == {"subdirector"}

    def test_assign_invalid_group_returns_400(self, client_directivo, professor):
        """POST /profesores/{id}/grupos/ - grupo inválido debe retornar 400."""
        url = reverse("professor-assign-groups", kwargs={"pk": professor.pk})
        data = {"groups": ["rol_inexistente"]}
        response = client_directivo.post(url, data, format="json")
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "error" in response.data
        assert "Grupos no válidos" in response.data["error"]["details"]["groups"][0]

    def test_assign_mix_valid_and_invalid_groups_returns_400(self, client_directivo, professor):
        """POST /profesores/{id}/grupos/ - mezcla de válidos e inválidos debe fallar."""
        url = reverse("professor-assign-groups", kwargs={"pk": professor.pk})
        data = {"groups": ["directivo", "rol_inexistente"]}
        response = client_directivo.post(url, data, format="json")
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "error" in response.data

    def test_delete_all_professor_groups(self, client_directivo, professor):
        """DELETE /profesores/{id}/grupos/ - eliminar todos los grupos."""
        url = reverse("professor-assign-groups", kwargs={"pk": professor.pk})
        
        # Primero asignar algunos grupos
        client_directivo.post(url, {"groups": ["directivo", "instructor"]}, format="json")
        
        # Luego eliminarlos
        response = client_directivo.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verificar que no tiene grupos
        professor.user.refresh_from_db()
        assert professor.user.groups.count() == 0

    def test_assign_groups_only_directivo_can(self, client_instructor, professor):
        """Solo directivo puede asignar grupos."""
        url = reverse("professor-assign-groups", kwargs={"pk": professor.pk})
        data = {"groups": ["directivo"]}
        response = client_instructor.post(url, data, format="json")
        
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_assign_groups_unauthenticated_denied(self, client, professor):
        """Usuarios no autenticados no pueden asignar grupos."""
        url = reverse("professor-assign-groups", kwargs={"pk": professor.pk})
        response = client.post(url, {"groups": ["directivo"]}, format="json")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_assign_empty_group_list(self, client_directivo, professor):
        """POST con lista vacía debe limpiar todos los grupos."""
        url = reverse("professor-assign-groups", kwargs={"pk": professor.pk})
        
        # Asignar algunos grupos primero
        client_directivo.post(url, {"groups": ["directivo"]}, format="json")
        
        # Enviar lista vacía
        response = client_directivo.post(url, {"groups": []}, format="json")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["groups"] == []
        
        # Verificar que no tiene grupos
        professor.user.refresh_from_db()
        assert professor.user.groups.count() == 0

    def test_all_valid_roles_can_be_assigned(self, client_directivo, professor):
        """Todos los roles definidos en el sistema pueden ser asignados."""
        valid_roles = ["estudiante", "instructor", "directivo", "subdirector", 
                      "comunicador", "decano", "ppa", "pg", "admin"]
        
        url = reverse("professor-assign-groups", kwargs={"pk": professor.pk})
        data = {"groups": valid_roles}
        response = client_directivo.post(url, data, format="json")
        
        assert response.status_code == status.HTTP_200_OK
        assert set(response.data["groups"]) == set(valid_roles)
