from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema_view, extend_schema

from core.permissions import IsDirectivo
from rest_framework.permissions import IsAuthenticated

from .models import Faculty, Career, CareerYear, Group
from .serializers import (
    FacultySerializer, CareerSerializer,
    CareerYearSerializer, GroupSerializer,
)


def _academic_schema(tag, summary_list, summary_detail):
    """Helper para anotar ViewSets con drf-spectacular."""
    return extend_schema_view(
        list=extend_schema(tags=[tag], summary=summary_list),
        retrieve=extend_schema(tags=[tag], summary=f"Detalle de {summary_detail}"),
        create=extend_schema(tags=[tag], summary=f"Crear {summary_detail}"),
        update=extend_schema(tags=[tag], summary=f"Actualizar {summary_detail}"),
        partial_update=extend_schema(tags=[tag], summary=f"Actualizar {summary_detail} (parcial)"),
        destroy=extend_schema(tags=[tag], summary=f"Eliminar {summary_detail}"),
    )


@_academic_schema("academic", "Listar facultades", "facultad")
class FacultyViewSet(viewsets.ModelViewSet):
    queryset           = Faculty.objects.prefetch_related("careers").order_by("name")
    serializer_class   = FacultySerializer
    permission_classes = [IsAuthenticated, IsDirectivo]
    filter_backends    = [filters.SearchFilter, filters.OrderingFilter]
    search_fields      = ["name", "code"]
    ordering_fields    = ["name", "created_at"]


@_academic_schema("academic", "Listar carreras", "carrera")
class CareerViewSet(viewsets.ModelViewSet):
    queryset           = Career.objects.select_related("faculty").order_by("faculty", "name")
    serializer_class   = CareerSerializer
    permission_classes = [IsAuthenticated, IsDirectivo]
    filter_backends    = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields   = ["faculty"]
    search_fields      = ["name", "code"]


@_academic_schema("academic", "Listar años académicos", "año académico")
class CareerYearViewSet(viewsets.ModelViewSet):
    queryset           = CareerYear.objects.select_related("career__faculty").order_by("career", "year")
    serializer_class   = CareerYearSerializer
    permission_classes = [IsAuthenticated, IsDirectivo]
    filter_backends    = [DjangoFilterBackend]
    filterset_fields   = ["career", "year"]


@_academic_schema("academic", "Listar grupos", "grupo")
class GroupViewSet(viewsets.ModelViewSet):
    queryset = (
        Group.objects
        .select_related("career_year__career__faculty")
        .order_by("career_year", "name")
    )
    serializer_class   = GroupSerializer
    permission_classes = [IsAuthenticated, IsDirectivo]
    filter_backends    = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields   = ["career_year", "career_year__career", "career_year__year"]
    search_fields      = ["name"]
