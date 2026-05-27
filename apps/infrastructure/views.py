from django.db.models.deletion import ProtectedError
from rest_framework import viewsets, filters, status
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema_view, extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.permissions import IsDirectivo
from .models import Site, Building, Wing, Room
from .serializers import (
    SiteSerializer, BuildingSerializer,
    WingSerializer, RoomSerializer, RoomListSerializer,
)


@extend_schema_view(
    list=extend_schema(tags=["infrastructure"], summary="Listar sedes (RF-26)"),
    retrieve=extend_schema(tags=["infrastructure"], summary="Detalle de sede (RF-27)"),
    create=extend_schema(tags=["infrastructure"], summary="Crear sede (RF-25)"),
    partial_update=extend_schema(tags=["infrastructure"], summary="Actualizar sede (RF-28)"),
    destroy=extend_schema(tags=["infrastructure"], summary="Eliminar sede (RF-29)"),
)
class SiteViewSet(viewsets.ModelViewSet):
    queryset           = Site.objects.prefetch_related("buildings").order_by("name")
    serializer_class   = SiteSerializer
    permission_classes = [IsAuthenticated, IsDirectivo]
    filter_backends    = [filters.SearchFilter]
    search_fields      = ["name", "address"]
    http_method_names  = ["get", "post", "patch", "delete", "head", "options"]

    def destroy(self, request, *args, **kwargs):
        """Eliminar sede con manejo de errores de integridad referencial."""
        try:
            return super().destroy(request, *args, **kwargs)
        except ProtectedError:
            return Response(
                {
                    "error": {
                        "code": "CONFLICT",
                        "message": "No se puede eliminar esta sede porque tiene edificios asociados.",
                    }
                },
                status=status.HTTP_409_CONFLICT
            )


@extend_schema_view(
    list=extend_schema(tags=["infrastructure"], summary="Listar edificios (RF-31)"),
    retrieve=extend_schema(tags=["infrastructure"], summary="Detalle de edificio (RF-32)"),
    create=extend_schema(tags=["infrastructure"], summary="Crear edificio (RF-30)"),
    partial_update=extend_schema(tags=["infrastructure"], summary="Actualizar edificio (RF-33)"),
    destroy=extend_schema(tags=["infrastructure"], summary="Eliminar edificio (RF-34)"),
)
class BuildingViewSet(viewsets.ModelViewSet):
    queryset = (
        Building.objects
        .select_related("site")
        .prefetch_related("wings")
        .order_by("site", "name")
    )
    serializer_class   = BuildingSerializer
    permission_classes = [IsAuthenticated, IsDirectivo]
    filter_backends    = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields   = ["site"]
    search_fields      = ["name"]
    http_method_names  = ["get", "post", "patch", "delete", "head", "options"]


@extend_schema_view(
    list=extend_schema(tags=["infrastructure"], summary="Listar alas (RF-36)"),
    retrieve=extend_schema(tags=["infrastructure"], summary="Detalle de ala (RF-37)"),
    create=extend_schema(tags=["infrastructure"], summary="Crear ala (RF-35)"),
    partial_update=extend_schema(tags=["infrastructure"], summary="Actualizar ala (RF-38)"),
    destroy=extend_schema(tags=["infrastructure"], summary="Eliminar ala (RF-39)"),
)
class WingViewSet(viewsets.ModelViewSet):
    queryset = (
        Wing.objects
        .select_related("building__site")
        .prefetch_related("rooms")
        .order_by("building", "name")
    )
    serializer_class   = WingSerializer
    permission_classes = [IsAuthenticated, IsDirectivo]
    filter_backends    = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields   = ["building", "building__site"]
    search_fields      = ["name", "building__name"]
    http_method_names  = ["get", "post", "patch", "delete", "head", "options"]


@extend_schema_view(
    list=extend_schema(tags=["infrastructure"], summary="Listar cuartos (RF-41)"),
    retrieve=extend_schema(tags=["infrastructure"], summary="Detalle de cuarto (RF-42)"),
    create=extend_schema(tags=["infrastructure"], summary="Crear cuarto (RF-40)"),
    partial_update=extend_schema(tags=["infrastructure"], summary="Actualizar cuarto (RF-43)"),
    destroy=extend_schema(tags=["infrastructure"], summary="Eliminar cuarto (RF-44)"),
)
class RoomViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsDirectivo]
    filter_backends    = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields   = ["wing", "wing__building", "wing__building__site", "is_active"]
    search_fields      = ["number"]
    ordering_fields    = ["number", "capacity", "current_occupancy"]
    http_method_names  = ["get", "post", "patch", "delete", "head", "options"]

    def get_queryset(self):
        return (
            Room.objects
            .select_related("wing__building__site")
            .order_by("wing__building__site", "wing__building", "wing", "number")
        )

    def get_serializer_class(self):
        # Lista usa serializer compacto; detalle/creación/edición usa el completo
        if self.action == "list":
            return RoomListSerializer
        return RoomSerializer
