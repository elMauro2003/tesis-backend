from django.urls import path
from .views import (
    LoginView,
    RefreshView,
    LogoutView,
    ChangePasswordView,
    MeView,
    RoleListView,
    UserListCreateView,
    UserDetailView,
    UserRolesView,
    UserRoleRemoveView,
    UserPermissionsView,
)

# Rutas bajo /api/v1/auth/
auth_urlpatterns = [
    path("login/",              LoginView.as_view(),          name="auth-login"),
    path("refresh/",            RefreshView.as_view(),         name="auth-refresh"),
    path("logout/",             LogoutView.as_view(),          name="auth-logout"),
    path("cambiar-contrasena/", ChangePasswordView.as_view(),  name="auth-change-password"),
    path("me/",                 MeView.as_view(),              name="auth-me"),
]

# Rutas bajo /api/v1/
extra_urlpatterns = [
    path("roles/",                               RoleListView.as_view(),        name="roles-list"),
    path("usuarios/",                            UserListCreateView.as_view(),   name="users-list"),
    path("usuarios/<int:pk>/",                   UserDetailView.as_view(),       name="users-detail"),
    path("usuarios/<int:pk>/roles/",             UserRolesView.as_view(),        name="users-roles"),
    path("usuarios/<int:pk>/roles/<int:rol_id>/",UserRoleRemoveView.as_view(),   name="users-roles-remove"),
    path("usuarios/<int:pk>/permisos/",          UserPermissionsView.as_view(),  name="users-permissions"),
]

urlpatterns = auth_urlpatterns + extra_urlpatterns
