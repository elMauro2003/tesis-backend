from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.shortcuts import get_object_or_404

from rest_framework import status, generics, serializers
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken

from drf_spectacular.utils import extend_schema, OpenApiResponse

from core.permissions import IsAdmin
from .serializers import (
    CustomTokenObtainPairSerializer,
    ChangePasswordSerializer,
    UserSerializer,
    UserCreateSerializer,
    RoleSerializer,
    UserRoleAssignSerializer,
    LogoutResponseSerializer,
    UserPermissionsResponseSerializer,
)

User = get_user_model()


# ─── RF-59: Login ──────────────────────────────────────────────────────────────

class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["auth"],
        summary="Login — Obtener tokens JWT",
        description=(
            "Autentica al usuario y devuelve un par de tokens JWT. "
            "El access token expira en 15 minutos; el refresh token en 7 días. "
            "El payload del access token incluye los roles del usuario."
        ),
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


# ─── RF-60: Refresh ────────────────────────────────────────────────────────────

class RefreshView(TokenRefreshView):
    @extend_schema(
        tags=["auth"],
        summary="Refrescar access token",
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


# ─── RF-61: Logout ─────────────────────────────────────────────────────────────

class LogoutView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = LogoutResponseSerializer

    @extend_schema(
        tags=["auth"],
        summary="Logout (client-side)",
        description=(
            "El backend no invalida tokens (arquitectura stateless). "
            "El cliente debe descartar el access y refresh token localmente. "
            "Devuelve 200 OK como confirmación."
        ),
        responses={200: OpenApiResponse(description="Logout exitoso")},
    )
    def post(self, request):
        serializer = self.get_serializer(
            {"message": "Logout exitoso. Descarta los tokens en el cliente."}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


# ─── RF-62: Cambiar Contraseña ─────────────────────────────────────────────────

class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["auth"],
        summary="Cambiar contraseña",
        request=ChangePasswordSerializer,
        responses={
            200: OpenApiResponse(description="Contraseña actualizada"),
            400: OpenApiResponse(description="Datos inválidos"),
        },
    )
    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"message": "Contraseña actualizada correctamente."},
            status=status.HTTP_200_OK,
        )


# ─── Perfil propio ─────────────────────────────────────────────────────────────

class MeView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["auth"],
        summary="Perfil del usuario autenticado",
        responses={200: UserSerializer},
    )
    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)


# ─── RF-63: Listar Roles ───────────────────────────────────────────────────────

class RoleListView(generics.ListAPIView):
    queryset           = Group.objects.all().order_by("name")
    serializer_class   = RoleSerializer
    permission_classes = [IsAuthenticated, IsAdmin]

    @extend_schema(tags=["roles"], summary="Listar roles del sistema")
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


# ─── Gestión de Usuarios ───────────────────────────────────────────────────────

class UserListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def get_queryset(self):
        return User.objects.prefetch_related("groups").order_by("last_name", "first_name")

    def get_serializer_class(self):
        if self.request.method == "POST":
            return UserCreateSerializer
        return UserSerializer

    @extend_schema(tags=["roles"], summary="Listar usuarios")
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(tags=["roles"], summary="Crear usuario")
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset           = User.objects.prefetch_related("groups")
    serializer_class   = UserSerializer
    permission_classes = [IsAuthenticated, IsAdmin]

    @extend_schema(tags=["roles"], summary="Detalle de usuario")
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(tags=["roles"], summary="Actualizar usuario (parcial)")
    def patch(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        # Deshabilitamos PUT — solo PATCH
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


# ─── RF-64 y RF-65: Asignar / Remover Roles ───────────────────────────────────

class UserRolesView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def _get_user(self, pk):
        return get_object_or_404(User, pk=pk)

    @extend_schema(
        tags=["roles"],
        summary="Asignar rol a usuario (RF-64)",
        request=UserRoleAssignSerializer,
        responses={
            200: OpenApiResponse(description="Rol asignado"),
            400: OpenApiResponse(description="Rol inválido"),
            404: OpenApiResponse(description="Usuario no encontrado"),
        },
    )
    def post(self, request, pk):
        user = self._get_user(pk)
        serializer = UserRoleAssignSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        role_name = serializer.validated_data["role_name"]
        group     = Group.objects.get(name=role_name)
        user.groups.add(group)

        return Response(
            {
                "message": f"Rol '{role_name}' asignado a '{user.username}' correctamente.",
                "roles":   list(user.groups.values_list("name", flat=True)),
            },
            status=status.HTTP_200_OK,
        )


class UserRoleRemoveView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    @extend_schema(
        tags=["roles"],
        summary="Remover rol de usuario (RF-65)",
        responses={
            200: OpenApiResponse(description="Rol removido"),
            404: OpenApiResponse(description="Usuario o rol no encontrado"),
        },
    )
    def delete(self, request, pk, rol_id):
        user  = get_object_or_404(User, pk=pk)
        group = get_object_or_404(Group, pk=rol_id)

        if not user.groups.filter(pk=rol_id).exists():
            return Response(
                {"error": {
                    "code":    "NOT_FOUND",
                    "message": f"El usuario '{user.username}' no tiene el rol '{group.name}'.",
                }},
                status=status.HTTP_404_NOT_FOUND,
            )

        user.groups.remove(group)
        return Response(
            {
                "message": f"Rol '{group.name}' removido de '{user.username}'.",
                "roles":   list(user.groups.values_list("name", flat=True)),
            },
            status=status.HTTP_200_OK,
        )


# ─── RF-66: Listar Permisos de Usuario ────────────────────────────────────────

class UserPermissionsView(GenericAPIView):
    permission_classes = [IsAuthenticated, IsAdmin]
    serializer_class = UserPermissionsResponseSerializer

    @extend_schema(
        tags=["roles"],
        summary="Listar permisos de usuario (RF-66)",
    )
    def get(self, request, pk):
        user = get_object_or_404(
            User.objects.prefetch_related("groups", "user_permissions"),
            pk=pk,
        )
        payload = {
            "user": user,
            "roles": list(user.groups.values_list("name", flat=True)),
            "permissions": list(user.get_all_permissions()),
        }
        serializer = self.get_serializer(instance=payload)
        return Response(serializer.data)
