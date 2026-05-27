from django.utils import timezone
from django.shortcuts import get_object_or_404

from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view

from core.permissions import (
    IsInstructor, IsDirectivo, IsSubdirector,
    IsComunicador, IsEstudiante, IsInstructorOrDirectivo,
    IsStudentOwner, IsStudentOwnerOrInstructor,
)
from .models import Complaint, Evaluation, CleaningSchedule, Assignment, Information, Report
from .serializers import (
    ComplaintSerializer, ComplaintCreateSerializer,
    ComplaintStatusSerializer, ComplaintResponseSerializer, ComplaintVisibilitySerializer,
    EvaluationSerializer,
    CleaningScheduleSerializer, CleaningCompleteSerializer,
    AssignmentSerializer, AssignmentReleaseSerializer,
    InformationSerializer, InformationPublicSerializer,
    ReportSerializer,
)


# ─── Complaints (RF-14 a RF-24) ────────────────────────────────────────────────

@extend_schema_view(
    list=extend_schema(tags=["complaints"],          summary="Listar quejas"),
    retrieve=extend_schema(tags=["complaints"],      summary="Consultar queja por ID"),
    create=extend_schema(tags=["complaints"],        summary="Añadir queja (RF-14)"),
    partial_update=extend_schema(tags=["complaints"],summary="Actualizar queja propia (RF-17)"),
    destroy=extend_schema(tags=["complaints"],       summary="Eliminar queja propia (RF-18)"),
)
class ComplaintViewSet(viewsets.ModelViewSet):
    filter_backends  = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["type", "status", "visibility", "building"]
    search_fields    = ["description", "student__user__last_name"]
    ordering_fields  = ["date", "created_at", "status"]
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]

    def get_permissions(self):
        if self.action in ["mis_quejas", "mis_evaluaciones", "mis_cuartelerias"]:
            return [IsAuthenticated(), IsEstudiante()]
        if self.action == "create":
            return [IsAuthenticated(), IsEstudiante()]
        if self.action in ["partial_update", "destroy"]:
            return [IsAuthenticated(), IsStudentOwnerOrInstructor()]
        if self.action in ["estado", "respuesta", "visibilidad"]:
            return [IsAuthenticated(), IsSubdirector()]
        return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        qs   = Complaint.objects.select_related(
            "student__user", "building"
        ).order_by("-created_at")

        if user.is_superuser or _has_role(user, "subdirector", "directivo", "admin", "instructor"):
            return qs  # Vista completa

        # Estudiante: solo sus quejas
        if hasattr(user, "student"):
            return qs.filter(student=user.student)

        return qs.none()

    def get_serializer_class(self):
        if self.action == "create":
            return ComplaintCreateSerializer
        return ComplaintSerializer

    # ── Acciones especiales ───────────────────────────────────────────────────

    @extend_schema(tags=["complaints"], summary="Mis quejas (RF-15)")
    @action(detail=False, methods=["get"], url_path="mis-quejas",
            permission_classes=[IsAuthenticated, IsEstudiante])
    def mis_quejas(self, request):
        qs = Complaint.objects.filter(student=request.user.student).order_by("-created_at")
        page = self.paginate_queryset(qs)
        if page is not None:
            return self.get_paginated_response(ComplaintSerializer(page, many=True).data)
        return Response(ComplaintSerializer(qs, many=True).data)

    @extend_schema(tags=["complaints"], summary="Quejas visibles (RF-19)")
    @action(detail=False, methods=["get"], url_path="visibles",
            permission_classes=[IsAuthenticated, IsEstudiante])
    def visibles(self, request):
        qs = Complaint.objects.filter(visibility=True).order_by("-created_at")
        page = self.paginate_queryset(qs)
        if page is not None:
            return self.get_paginated_response(ComplaintSerializer(page, many=True).data)
        return Response(ComplaintSerializer(qs, many=True).data)

    @extend_schema(tags=["complaints"], summary="Cambiar estado de queja (RF-22)",
                   request=ComplaintStatusSerializer)
    @action(detail=True, methods=["patch"], url_path="estado",
            permission_classes=[IsAuthenticated, IsSubdirector])
    def estado(self, request, pk=None):
        complaint  = self.get_object()
        serializer = ComplaintStatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        complaint.status = serializer.validated_data["status"]
        complaint.save(update_fields=["status", "updated_at"])
        return Response(ComplaintSerializer(complaint).data)

    @extend_schema(tags=["complaints"], summary="Responder queja (RF-23)",
                   request=ComplaintResponseSerializer)
    @action(detail=True, methods=["post"], url_path="respuesta",
            permission_classes=[IsAuthenticated, IsSubdirector])
    def respuesta(self, request, pk=None):
        complaint  = self.get_object()
        serializer = ComplaintResponseSerializer(
            complaint, data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(ComplaintSerializer(complaint).data)

    @extend_schema(tags=["complaints"], summary="Controlar visibilidad (RF-24)",
                   request=ComplaintVisibilitySerializer)
    @action(detail=True, methods=["patch"], url_path="visibilidad",
            permission_classes=[IsAuthenticated, IsSubdirector])
    def visibilidad(self, request, pk=None):
        complaint  = self.get_object()
        serializer = ComplaintVisibilitySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        complaint.visibility = serializer.validated_data["visibility"]
        complaint.save(update_fields=["visibility", "updated_at"])
        return Response(ComplaintSerializer(complaint).data)


# ─── Evaluations (RF-8 a RF-13) ───────────────────────────────────────────────

@extend_schema_view(
    list=extend_schema(tags=["evaluations"],         summary="Listar evaluaciones (RF-9)"),
    retrieve=extend_schema(tags=["evaluations"],     summary="Consultar evaluación (RF-10)"),
    create=extend_schema(tags=["evaluations"],       summary="Añadir evaluación (RF-8)"),
    partial_update=extend_schema(tags=["evaluations"],summary="Actualizar evaluación (RF-11)"),
    destroy=extend_schema(tags=["evaluations"],      summary="Eliminar evaluación (RF-12)"),
)
class EvaluationViewSet(viewsets.ModelViewSet):
    serializer_class  = EvaluationSerializer
    filter_backends   = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields  = ["grade", "student", "student__group"]
    ordering_fields   = ["date", "grade"]
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]

    def get_permissions(self):
        if self.action == "mis_evaluaciones":
            return [IsAuthenticated(), IsEstudiante()]
        if self.action in ["create", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsInstructor()]
        return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        qs = Evaluation.objects.select_related(
            "student__user", "created_by"
        ).order_by("-date")

        if _has_role(user, "instructor", "directivo", "admin") or user.is_superuser:
            return qs
        if hasattr(user, "student"):
            return qs.filter(student=user.student)
        return qs.none()

    @extend_schema(tags=["evaluations"], summary="Mis evaluaciones (RF-13)")
    @action(detail=False, methods=["get"], url_path="mis-evaluaciones",
            permission_classes=[IsAuthenticated, IsEstudiante])
    def mis_evaluaciones(self, request):
        qs   = Evaluation.objects.filter(student=request.user.student).order_by("-date")
        page = self.paginate_queryset(qs)
        if page is not None:
            return self.get_paginated_response(EvaluationSerializer(page, many=True).data)
        return Response(EvaluationSerializer(qs, many=True).data)


# ─── Cleaning Schedules (RF-67 a RF-70) ───────────────────────────────────────

@extend_schema_view(
    list=extend_schema(tags=["cleaning"],    summary="Listar cuartelerías (RF-68)"),
    retrieve=extend_schema(tags=["cleaning"],summary="Detalle de cuartelería"),
    create=extend_schema(tags=["cleaning"],  summary="Crear cuartelería (RF-67)"),
    destroy=extend_schema(tags=["cleaning"], summary="Eliminar cuartelería"),
)
class CleaningScheduleViewSet(viewsets.ModelViewSet):
    serializer_class  = CleaningScheduleSerializer
    filter_backends   = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields  = ["room", "room__wing", "student", "completed", "assigned_date"]
    ordering_fields   = ["assigned_date", "completed"]
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]

    def get_permissions(self):
        if self.action == "mis_cuartelerias":
            return [IsAuthenticated(), IsEstudiante()]
        if self.action in ["create", "destroy", "completar"]:
            return [IsAuthenticated(), IsInstructor()]
        return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        qs = CleaningSchedule.objects.select_related(
            "room__wing__building", "student__user"
        ).order_by("-assigned_date")

        if _has_role(user, "instructor", "directivo", "admin") or user.is_superuser:
            return qs
        if hasattr(user, "student"):
            return qs.filter(student=user.student)
        return qs.none()

    @extend_schema(tags=["cleaning"], summary="Mis cuartelerías (RF-69)")
    @action(detail=False, methods=["get"], url_path="mis-cuartelerias",
            permission_classes=[IsAuthenticated, IsEstudiante])
    def mis_cuartelerias(self, request):
        qs = CleaningSchedule.objects.filter(
            student=request.user.student
        ).order_by("-assigned_date")
        page = self.paginate_queryset(qs)
        if page is not None:
            return self.get_paginated_response(CleaningScheduleSerializer(page, many=True).data)
        return Response(CleaningScheduleSerializer(qs, many=True).data)

    @extend_schema(tags=["cleaning"], summary="Marcar cuartelería completada (RF-70)",
                   request=CleaningCompleteSerializer)
    @action(detail=True, methods=["patch"], url_path="completar",
            permission_classes=[IsAuthenticated, IsInstructor])
    def completar(self, request, pk=None):
        schedule   = self.get_object()
        serializer = CleaningCompleteSerializer(
            schedule, data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(CleaningScheduleSerializer(schedule).data)


# ─── Assignments (RF-45 a RF-49) ──────────────────────────────────────────────

@extend_schema_view(
    list=extend_schema(tags=["assignments"],    summary="Histórico de asignaciones (RF-47)"),
    retrieve=extend_schema(tags=["assignments"],summary="Consultar asignación (RF-48)"),
    create=extend_schema(tags=["assignments"],  summary="Asignar cuarto (RF-45)"),
)
class AssignmentViewSet(viewsets.ModelViewSet):
    serializer_class  = AssignmentSerializer
    permission_classes = [IsAuthenticated, IsInstructorOrDirectivo]
    filter_backends   = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields  = ["student", "room", "room__wing", "room__wing__building"]
    ordering_fields   = ["assigned_date", "released_date"]
    # Solo GET, POST — no PUT, PATCH, DELETE en el recurso base
    http_method_names = ["get", "post", "head", "options"]

    def get_queryset(self):
        return Assignment.objects.select_related(
            "student__user",
            "room__wing__building__site",
            "assigned_by",
        ).order_by("-assigned_date")

    @extend_schema(tags=["assignments"], summary="Asignaciones activas (RF-46)")
    @action(detail=False, methods=["get"], url_path="activas")
    def activas(self, request):
        qs   = self.get_queryset().filter(released_date__isnull=True)
        page = self.paginate_queryset(qs)
        if page is not None:
            return self.get_paginated_response(AssignmentSerializer(page, many=True).data)
        return Response(AssignmentSerializer(qs, many=True).data)

    @extend_schema(tags=["assignments"], summary="Liberar cuarto (RF-49)",
                   request=AssignmentReleaseSerializer)
    @action(detail=True, methods=["post"], url_path="liberar")
    def liberar(self, request, pk=None):
        assignment = self.get_object()
        serializer = AssignmentReleaseSerializer(
            assignment, data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(AssignmentSerializer(assignment).data)


# ─── Information (RF-50 a RF-55) ──────────────────────────────────────────────

@extend_schema_view(
    list=extend_schema(tags=["information"],         summary="Listar informaciones (RF-51)"),
    retrieve=extend_schema(tags=["information"],     summary="Consultar información (RF-52)"),
    create=extend_schema(tags=["information"],       summary="Crear información (RF-50)"),
    partial_update=extend_schema(tags=["information"],summary="Actualizar información (RF-53)"),
    destroy=extend_schema(tags=["information"],      summary="Eliminar información (RF-54)"),
)
class InformationViewSet(viewsets.ModelViewSet):
    filter_backends   = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    search_fields     = ["title", "content"]
    filterset_fields  = ["is_public"]
    ordering_fields   = ["published_date", "expires_date"]
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]

    def get_permissions(self):
        if self.action in ["create", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsComunicador()]
        return [IsAuthenticated()]

    def get_queryset(self):
        return Information.objects.select_related("created_by").order_by("-published_date")

    def get_serializer_class(self):
        return InformationSerializer

    @extend_schema(tags=["information"], summary="Informaciones públicas (RF-55)")
    @action(detail=False, methods=["get"], url_path="publicas",
            permission_classes=[IsAuthenticated])
    def publicas(self, request):
        qs = Information.objects.filter(
            is_public=True
        ).filter(
            # expires_date nulo o en el futuro
            expires_date__isnull=True
        ) | Information.objects.filter(
            is_public=True, expires_date__gte=timezone.now().date()
        )
        qs   = qs.order_by("-published_date")
        page = self.paginate_queryset(qs)
        if page is not None:
            return self.get_paginated_response(InformationPublicSerializer(page, many=True).data)
        return Response(InformationPublicSerializer(qs, many=True).data)


# ─── Reports (RF-56 a RF-58) ──────────────────────────────────────────────────

@extend_schema_view(
    list=extend_schema(tags=["reports"],    summary="Listar reportes (RF-58)"),
    retrieve=extend_schema(tags=["reports"],summary="Consultar reporte (RF-57)"),
    create=extend_schema(tags=["reports"],  summary="Solicitar reporte (RF-56)"),
)
class ReportViewSet(viewsets.ModelViewSet):
    serializer_class   = ReportSerializer
    permission_classes = [IsAuthenticated, IsDirectivo]
    filter_backends    = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields   = ["type"]
    ordering_fields    = ["generated_date"]
    http_method_names  = ["get", "post", "head", "options"]

    def get_queryset(self):
        return Report.objects.select_related("generated_by").order_by("-generated_date")


# ─── Helper local ─────────────────────────────────────────────────────────────

def _has_role(user, *roles) -> bool:
    if not user.is_authenticated:
        return False
    return user.groups.filter(name__in=roles).exists()
