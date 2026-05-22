from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

# ─── API v1 ────────────────────────────────────────────────────────────────────
# Prefijo /api/v1/ en todos los endpoints
API_V1 = "api/v1/"

urlpatterns = [
    # ── Django Admin ──────────────────────────────────────────────────────────
    
    path("admin/", admin.site.urls),
    path(f"{API_V1}auth/", include("apps.authentication.urls")),
    # También exponemos algunas rutas de autenticación (roles/usuarios) directamente
    # bajo /api/v1/ para compatibilidad con la colección de pruebas.
    path(f"{API_V1}", include("apps.authentication.urls")),
    path(f"{API_V1}", include("apps.academic.urls")),
    path(f"{API_V1}", include("apps.infrastructure.urls")),
    path(f"{API_V1}", include("apps.actors.urls")),
    path(f"{API_V1}", include("apps.operations.urls")),
    
    # API Docs 
    path(f"{API_V1}schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        f"{API_V1}docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        f"{API_V1}redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
]
