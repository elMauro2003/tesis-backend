from django.db.models import Prefetch
from django.db.models import Exists, OuterRef
from django.contrib.auth.models import Group as DjangoGroup
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

from core.permissions import IsInstructor, IsDirectivo, IsAdmin, IsStudentReader, IsInstructorOrDirectivo
from core.pagination import StudentCursorPagination

from .models import Student, Professor, Dean, GroupAdvisor, YearLeadProfessor, WingSupervisor
from .serializers import (
    StudentSerializer, StudentListSerializer, StudentCreateSerializer,
    ProfessorSerializer, ProfessorCreateSerializer,
    DeanSerializer, GroupAdvisorSerializer,
    YearLeadProfessorSerializer, WingSupervisorSerializer, GroupAssignmentSerializer,
)
from apps.operations.models import Assignment


@extend_schema_view(
    list=extend_schema(tags=["students"],    summary="Listar estudiantes (RF-2, RF-7)"),
    retrieve=extend_schema(tags=["students"],summary="Consultar estudiante por ID (RF-3)"),
    create=extend_schema(tags=["students"],  summary="Insertar estudiante (RF-1)"),
    update=extend_schema(tags=["students"],  summary="Actualizar estudiante completo (RF-4)"),
    partial_update=extend_schema(tags=["students"], summary="Actualizar estudiante parcial (RF-5)"),
    destroy=extend_schema(tags=["students"], summary="Eliminar estudiante (RF-6)"),
)
@method_decorator(cache_page(60 * 5), name="list")
class StudentViewSet(viewsets.ModelViewSet):
    pagination_class = StudentCursorPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = [
        "gender", "group", "group__career_year",
        "group__career_year__career", "group__career_year__career__faculty",
        "group__career_year__year", "is_militant",
    ]
    search_fields  = [
        "user__first_name", "user__last_name",
        "student_id", "ci", "user__email",
    ]
    ordering_fields = ["user__last_name", "student_id", "created_at"]

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [IsAuthenticated(), IsStudentReader()]
        # Escritura: instructor, directivo y admin
        return [IsAuthenticated(), IsInstructorOrDirectivo()]

    def get_queryset(self):
        active_assignments = Assignment.objects.select_related(
            "room__wing__building",
        ).only(
            "id",
            "student_id",
            "room_id",
            "assigned_date",
            "released_date",
            "room__id",
            "room__number",
            "room__wing__id",
            "room__wing__name",
            "room__wing__building__id",
            "room__wing__building__name",
        ).filter(
            released_date__isnull=True,
        ).order_by("-assigned_date")

        qs = (
            Student.objects
            .select_related(
                "user",
                "group__career_year__career__faculty",
            )
            .prefetch_related(
                Prefetch("assignments", queryset=active_assignments, to_attr="active_assignments"),
            )
            .order_by("-created_at")
        )

        user = self.request.user
        if user.is_superuser:
            return qs

        # Filtrado por rol — cada rol solo ve su ámbito
        if hasattr(user, "professor"):
            prof = user.professor
            # Decano: estudiantes de su facultad
            if hasattr(prof, "dean"):
                return qs.filter(
                    group__career_year__career__faculty=prof.dean.faculty
                )
            # PPA: estudiantes de su año académico
            if hasattr(prof, "year_lead_professor"):
                return qs.filter(
                    group__career_year=prof.year_lead_professor.career_year
                )
            # PG: estudiantes de su grupo
            if hasattr(prof, "group_advisor"):
                return qs.filter(group=prof.group_advisor.group)

        return qs

    def get_serializer_class(self):
        if self.action == "list":
            return StudentListSerializer
        if self.action == "create":
            return StudentCreateSerializer
        return StudentSerializer


@extend_schema_view(
    list=extend_schema(tags=["professors"],   summary="Listar profesores"),
    retrieve=extend_schema(tags=["professors"],summary="Detalle de profesor"),
    create=extend_schema(tags=["professors"],  summary="Crear profesor"),
    partial_update=extend_schema(tags=["professors"], summary="Actualizar profesor"),
    destroy=extend_schema(tags=["professors"], summary="Eliminar profesor"),
)
class ProfessorViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsDirectivo]
    filter_backends    = [filters.SearchFilter, DjangoFilterBackend]
    search_fields      = ["user__first_name", "user__last_name", "employee_id"]
    filterset_fields   = ["department"]
    http_method_names  = ["get", "post", "patch", "delete", "head", "options"]

    def get_queryset(self):
        return (
            Professor.objects
            .select_related("user")
            .prefetch_related("dean", "group_advisor", "year_lead_professor", "wing_supervisor")
            .annotate(
                is_dean=Exists(Dean.objects.filter(professor=OuterRef("pk"))),
                is_group_advisor=Exists(GroupAdvisor.objects.filter(professor=OuterRef("pk"))),
                is_year_lead_professor=Exists(YearLeadProfessor.objects.filter(professor=OuterRef("pk"))),
                is_wing_supervisor=Exists(WingSupervisor.objects.filter(professor=OuterRef("pk"))),
            )
            .order_by("user__last_name", "user__first_name")
        )

    def get_serializer_class(self):
        if self.action == "create":
            return ProfessorCreateSerializer
        return ProfessorSerializer

    # ── Acciones para sub-roles ───────────────────────────────────────────────

    @extend_schema(tags=["professors"], summary="Asignar/consultar sub-rol Decano",
                   request=DeanSerializer, responses={200: DeanSerializer})
    @action(detail=True, methods=["get", "post", "delete"], url_path="decano")
    def dean(self, request, pk=None):
        professor = self.get_object()
        if request.method == "GET":
            if hasattr(professor, "dean"):
                return Response(DeanSerializer(professor.dean).data)
            return Response({"detail": "Este profesor no es decano."}, status=404)
        if request.method == "POST":
            serializer = DeanSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            dean, _ = Dean.objects.update_or_create(
                professor=professor,
                defaults={"faculty": serializer.validated_data["faculty"]},
            )
            return Response(DeanSerializer(dean).data, status=status.HTTP_201_CREATED)
        if request.method == "DELETE":
            Dean.objects.filter(professor=professor).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(tags=["professors"], summary="Asignar/consultar sub-rol Profesor Guía",
                   request=GroupAdvisorSerializer, responses={200: GroupAdvisorSerializer})
    @action(detail=True, methods=["get", "post", "delete"], url_path="profesor-guia")
    def group_advisor(self, request, pk=None):
        professor = self.get_object()
        if request.method == "GET":
            if hasattr(professor, "group_advisor"):
                return Response(GroupAdvisorSerializer(professor.group_advisor).data)
            return Response({"detail": "Este profesor no es Profesor Guía."}, status=404)
        if request.method == "POST":
            serializer = GroupAdvisorSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            advisor, _ = GroupAdvisor.objects.update_or_create(
                professor=professor,
                defaults={"group": serializer.validated_data["group"]},
            )
            return Response(GroupAdvisorSerializer(advisor).data, status=status.HTTP_201_CREATED)
        if request.method == "DELETE":
            GroupAdvisor.objects.filter(professor=professor).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(tags=["professors"], summary="Asignar/consultar sub-rol PPA",
                   request=YearLeadProfessorSerializer, responses={200: YearLeadProfessorSerializer})
    @action(detail=True, methods=["get", "post", "delete"], url_path="ppa")
    def year_lead_professor(self, request, pk=None):
        professor = self.get_object()
        if request.method == "GET":
            if hasattr(professor, "year_lead_professor"):
                return Response(YearLeadProfessorSerializer(professor.year_lead_professor).data)
            return Response({"detail": "Este profesor no es PPA."}, status=404)
        if request.method == "POST":
            serializer = YearLeadProfessorSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            ppa, _ = YearLeadProfessor.objects.update_or_create(
                professor=professor,
                defaults={"career_year": serializer.validated_data["career_year"]},
            )
            return Response(YearLeadProfessorSerializer(ppa).data, status=status.HTTP_201_CREATED)
        if request.method == "DELETE":
            YearLeadProfessor.objects.filter(professor=professor).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(tags=["professors"], summary="Asignar/consultar sub-rol Responsable de Ala",
                   request=WingSupervisorSerializer, responses={200: WingSupervisorSerializer})
    @action(detail=True, methods=["get", "post", "delete"], url_path="responsable-ala")
    def wing_supervisor(self, request, pk=None):
        professor = self.get_object()
        if request.method == "GET":
            if hasattr(professor, "wing_supervisor"):
                return Response(WingSupervisorSerializer(professor.wing_supervisor).data)
            return Response({"detail": "Este profesor no es Responsable de Ala."}, status=404)
        if request.method == "POST":
            serializer = WingSupervisorSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            ws, _ = WingSupervisor.objects.update_or_create(
                professor=professor,
                defaults={"wing": serializer.validated_data["wing"]},
            )
            return Response(WingSupervisorSerializer(ws).data, status=status.HTTP_201_CREATED)
        if request.method == "DELETE":
            WingSupervisor.objects.filter(professor=professor).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(tags=["professors"], summary="Asignar/consultar/limpiar grupos (roles) de usuario",
                   request=GroupAssignmentSerializer, responses={200: GroupAssignmentSerializer})
    @action(detail=True, methods=["get", "post", "delete"], url_path="grupos")
    def assign_groups(self, request, pk=None):
        """
        Asigna grupos (roles) a un usuario profesor.
        
        GET: lista los grupos actuales del usuario
        POST: asigna nuevos grupos (reemplaza los anteriores)
        DELETE: elimina todos los grupos del usuario
        """
        professor = self.get_object()
        user = professor.user
        
        if request.method == "GET":
            groups = user.groups.values_list("name", flat=True)
            return Response({"groups": list(groups)})
        
        if request.method == "POST":
            serializer = GroupAssignmentSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            # Obtener los grupos validados
            group_names = serializer.validated_data["groups"]
            groups = DjangoGroup.objects.filter(name__in=group_names)
            
            # Limpiar grupos anteriores y asignar nuevos
            user.groups.clear()
            user.groups.set(groups)
            
            return Response({"groups": list(groups.values_list("name", flat=True))}, 
                          status=status.HTTP_200_OK)
        
        if request.method == "DELETE":
            user.groups.clear()
            return Response(status=status.HTTP_204_NO_CONTENT)
