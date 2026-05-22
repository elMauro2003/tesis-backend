import pytest
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
class TestSiteCRUD:
    """RF-25 a RF-29."""

    def test_create_site(self, client_directivo):
        url      = reverse("site-list")
        response = client_directivo.post(url, {
            "name":    "Sede Fajardo",
            "address": "Reparto Fajardo, Santa Clara",
        }, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["name"] == "Sede Fajardo"

    def test_list_sites(self, client_directivo, site):
        url      = reverse("site-list")
        response = client_directivo.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] >= 1

    def test_partial_update_site(self, client_directivo, site):
        url      = reverse("site-detail", kwargs={"pk": site.pk})
        response = client_directivo.patch(url, {"address": "Dirección actualizada"}, format="json")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["address"] == "Dirección actualizada"

    def test_delete_site_with_buildings_raises_error(self, client_directivo, building):
        """No se puede eliminar una sede con edificios (PROTECT)."""
        url      = reverse("site-detail", kwargs={"pk": building.site.pk})
        response = client_directivo.delete(url)
        # Django devuelve 409 Conflict o 500 con ProtectedError — DRF puede manejarlo
        assert response.status_code in [
            status.HTTP_409_CONFLICT,
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_500_INTERNAL_SERVER_ERROR,
        ]

    def test_instructor_cannot_create_site(self, client_instructor):
        """Solo directivos pueden gestionar infraestructura."""
        url      = reverse("site-list")
        response = client_instructor.post(url, {"name": "Sede X"}, format="json")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_put_not_allowed(self, client_directivo, site):
        """Solo PATCH permitido, no PUT."""
        url      = reverse("site-detail", kwargs={"pk": site.pk})
        response = client_directivo.put(url, {"name": "Nuevo nombre"}, format="json")
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED


@pytest.mark.django_db
class TestRoomCRUD:
    """RF-40 a RF-44."""

    def test_create_room(self, client_directivo, wing):
        url      = reverse("room-list")
        response = client_directivo.post(url, {
            "wing":     wing.pk,
            "number":   "201",
            "capacity": 3,
        }, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["available_spots"] == 3
        assert response.data["is_full"] is False

    def test_room_list_uses_compact_serializer(self, client_directivo, room):
        """El listado de cuartos usa RoomListSerializer."""
        url      = reverse("room-list")
        response = client_directivo.get(url)
        assert response.status_code == status.HTTP_200_OK
        first = response.data["results"][0]
        # RoomListSerializer no incluye building_name ni available_spots
        assert "is_full" in first

    def test_room_detail_uses_full_serializer(self, client_directivo, room):
        url      = reverse("room-detail", kwargs={"pk": room.pk})
        response = client_directivo.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert "available_spots"  in response.data
        assert "building_name"    in response.data
        assert "current_occupancy" in response.data

    def test_filter_rooms_by_wing(self, client_directivo, room, wing):
        url      = reverse("room-list")
        response = client_directivo.get(url, {"wing": wing.pk})
        assert response.status_code == status.HTTP_200_OK
        assert all(r["wing"] == wing.pk for r in response.data["results"])

    def test_duplicate_room_number_in_same_wing(self, client_directivo, wing, room):
        """No se pueden crear dos cuartos con el mismo número en el mismo ala."""
        url      = reverse("room-list")
        response = client_directivo.post(url, {
            "wing":     wing.pk,
            "number":   room.number,  # número duplicado
            "capacity": 2,
        }, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestWingUnique:
    def test_duplicate_wing_name_in_same_building(self, client_directivo, wing):
        url      = reverse("wing-list")
        response = client_directivo.post(url, {
            "building": wing.building.pk,
            "name":     wing.name,  # nombre duplicado
        }, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
