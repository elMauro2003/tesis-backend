import pytest
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
class TestLogin:
    """RF-59: POST /api/v1/auth/login/"""

    def test_login_valid_credentials_returns_tokens(self, client_no_auth, user_instructor):
        url      = reverse("auth-login")
        response = client_no_auth.post(url, {
            "username": "instructor_test",
            "password": "InstrPass123!",
        }, format="json")

        assert response.status_code == status.HTTP_200_OK
        data = response.data
        assert "access"  in data
        assert "refresh" in data
        assert "user"    in data
        assert data["user"]["username"] == "instructor_test"
        assert "roles" in data["user"]
        assert "instructor" in data["user"]["roles"]

    def test_login_invalid_password_returns_401(self, client_no_auth, user_instructor):
        url      = reverse("auth-login")
        response = client_no_auth.post(url, {
            "username": "instructor_test",
            "password": "ContrasenaWrong!",
        }, format="json")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_nonexistent_user_returns_401(self, client_no_auth):
        url      = reverse("auth-login")
        response = client_no_auth.post(url, {
            "username": "fantasma",
            "password": "cualquiera",
        }, format="json")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_response_error_format_is_normalized(self, client_no_auth):
        """El error de credenciales inválidas usa el formato estándar del proyecto."""
        url      = reverse("auth-login")
        response = client_no_auth.post(url, {
            "username": "nobody",
            "password": "wrong",
        }, format="json")
        assert "error" in response.data
        assert "code"    in response.data["error"]
        assert "message" in response.data["error"]

    def test_login_inactive_user_returns_401(self, client_no_auth, user_instructor):
        user_instructor.is_active = False
        user_instructor.save()
        url = reverse("auth-login")
        response = client_no_auth.post(url, {
            "username": "instructor_test",
            "password": "InstrPass123!",
        }, format="json")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestTokenRefresh:
    """RF-60: POST /api/v1/auth/refresh/"""

    def _get_refresh_token(self, client, username, password):
        url  = reverse("auth-login")
        resp = client.post(url, {"username": username, "password": password}, format="json")
        return resp.data["refresh"]

    def test_refresh_valid_token_returns_new_access(self, client_no_auth, user_instructor):
        refresh_token = self._get_refresh_token(
            client_no_auth, "instructor_test", "InstrPass123!"
        )
        url = reverse("auth-refresh")
        response = client_no_auth.post(url, {"refresh": refresh_token}, format="json")
        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data

    def test_refresh_invalid_token_returns_401(self, client_no_auth):
        url = reverse("auth-refresh")
        response = client_no_auth.post(url, {"refresh": "token.invalido.aqui"}, format="json")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestLogout:
    """RF-61: POST /api/v1/auth/logout/"""

    def test_logout_authenticated_returns_200(self, client_instructor):
        url      = reverse("auth-logout")
        response = client_instructor.post(url)
        assert response.status_code == status.HTTP_200_OK
        assert "message" in response.data

    def test_logout_unauthenticated_returns_401(self, client_no_auth):
        url      = reverse("auth-logout")
        response = client_no_auth.post(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestChangePassword:
    """RF-62: POST /api/v1/auth/cambiar-contrasena/"""

    def test_change_password_success(self, client_instructor, user_instructor):
        url      = reverse("auth-change-password")
        response = client_instructor.post(url, {
            "old_password":         "InstrPass123!",
            "new_password":         "NuevaClave456@",
            "confirm_new_password": "NuevaClave456@",
        }, format="json")
        assert response.status_code == status.HTTP_200_OK
        # Verificar que la nueva contraseña funciona
        user_instructor.refresh_from_db()
        assert user_instructor.check_password("NuevaClave456@")

    def test_change_password_wrong_old_password(self, client_instructor):
        url      = reverse("auth-change-password")
        response = client_instructor.post(url, {
            "old_password":         "ContrasenaEquivocada!",
            "new_password":         "NuevaClave456@",
            "confirm_new_password": "NuevaClave456@",
        }, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_change_password_mismatch_confirmation(self, client_instructor):
        url      = reverse("auth-change-password")
        response = client_instructor.post(url, {
            "old_password":         "InstrPass123!",
            "new_password":         "NuevaClave456@",
            "confirm_new_password": "OtraClave789#",
        }, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_change_password_requires_authentication(self, client_no_auth):
        url      = reverse("auth-change-password")
        response = client_no_auth.post(url, {
            "old_password": "cualquiera",
            "new_password": "nueva",
            "confirm_new_password": "nueva",
        }, format="json")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestMeEndpoint:
    """GET /api/v1/auth/me/"""

    def test_me_returns_user_data_with_roles(self, client_instructor, user_instructor):
        url      = reverse("auth-me")
        response = client_instructor.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["username"] == user_instructor.username
        assert "roles" in response.data
        assert "instructor" in response.data["roles"]

    def test_me_unauthenticated_returns_401(self, client_no_auth):
        url      = reverse("auth-me")
        response = client_no_auth.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
