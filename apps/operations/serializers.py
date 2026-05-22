from django.utils import timezone
from rest_framework import serializers

from apps.actors.models import Student
from apps.infrastructure.models import Room
from .models import Complaint, Evaluation, CleaningSchedule, Assignment, Information, Report


# ─── Complaint ─────────────────────────────────────────────────────────────────

class ComplaintSerializer(serializers.ModelSerializer):
    student_name  = serializers.CharField(source="student.full_name",    read_only=True)
    building_name = serializers.CharField(source="building.name",        read_only=True, default=None)
    status_display = serializers.CharField(source="get_status_display",  read_only=True)
    type_display   = serializers.CharField(source="get_type_display",    read_only=True)

    class Meta:
        model  = Complaint
        fields = [
            "id", "student", "student_name",
            "date", "building", "building_name",
            "description", "type", "type_display",
            "status", "status_display", "visibility",
            "response", "response_date",
            "created_at", "updated_at",
        ]
        read_only_fields = ["response", "response_date", "created_at", "updated_at"]


class ComplaintCreateSerializer(serializers.ModelSerializer):
    """Para crear una queja — el estudiante se toma del usuario autenticado."""
    student_name  = serializers.CharField(source="student.full_name",    read_only=True)
    building_name = serializers.CharField(source="building.name",        read_only=True, default=None)
    status_display = serializers.CharField(source="get_status_display",  read_only=True)
    type_display   = serializers.CharField(source="get_type_display",    read_only=True)

    class Meta:
        model  = Complaint
        fields = [
            "id", "student", "student_name",
            "date", "building", "building_name",
            "description", "type", "type_display",
            "status", "status_display", "visibility",
            "response", "response_date",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "student", "student_name", "response", "response_date", "created_at", "updated_at", "status", "status_display", "visibility"]

    def create(self, validated_data):
        user    = self.context["request"].user
        student = user.student  # El usuario autenticado debe ser estudiante
        return Complaint.objects.create(student=student, **validated_data)


class ComplaintStatusSerializer(serializers.Serializer):
    """Cambiar estado de una queja (RF-22)."""
    STATUS_CHOICES = ["pendiente", "en_proceso", "resuelta", "rechazada"]
    status = serializers.ChoiceField(choices=STATUS_CHOICES)


class ComplaintResponseSerializer(serializers.Serializer):
    """Responder una queja (RF-23)."""
    response = serializers.CharField(min_length=10)

    def update(self, instance, validated_data):
        instance.response      = validated_data["response"]
        instance.response_date = timezone.now()
        instance.status        = "resuelta"
        instance.save(update_fields=["response", "response_date", "status"])
        return instance


class ComplaintVisibilitySerializer(serializers.Serializer):
    """Controlar visibilidad de una queja (RF-24)."""
    visibility = serializers.BooleanField()


# ─── Evaluation ────────────────────────────────────────────────────────────────

class EvaluationSerializer(serializers.ModelSerializer):
    student_name   = serializers.CharField(source="student.full_name",   read_only=True)
    created_by_name= serializers.CharField(source="created_by.get_full_name", read_only=True)
    grade_display  = serializers.CharField(source="get_grade_display",   read_only=True)

    class Meta:
        model  = Evaluation
        fields = [
            "id", "student", "student_name",
            "date", "grade", "grade_display", "comment",
            "created_by", "created_by_name",
            "created_at", "updated_at",
        ]
        read_only_fields = ["created_by", "created_at", "updated_at"]

    def create(self, validated_data):
        validated_data["created_by"] = self.context["request"].user
        return super().create(validated_data)


# ─── CleaningSchedule ──────────────────────────────────────────────────────────

class CleaningScheduleSerializer(serializers.ModelSerializer):
    student_name     = serializers.CharField(source="student.full_name", read_only=True)
    room_detail      = serializers.CharField(source="room.__str__",      read_only=True)
    evaluation_display = serializers.CharField(source="get_evaluation_display", read_only=True, default=None)

    class Meta:
        model  = CleaningSchedule
        fields = [
            "id", "room", "room_detail", "student", "student_name",
            "assigned_date", "completed", "evaluation", "evaluation_display", "comments",
            "created_at", "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]


class CleaningCompleteSerializer(serializers.Serializer):
    """Marcar cuartelería como completada con evaluación (RF-70)."""
    EVAL_CHOICES = [("B", "Bien"), ("R", "Regular"), ("M", "Mal")]
    evaluation = serializers.ChoiceField(choices=EVAL_CHOICES)
    comments   = serializers.CharField(required=False, allow_blank=True)

    def update(self, instance, validated_data):
        instance.completed  = True
        instance.evaluation = validated_data["evaluation"]
        instance.comments   = validated_data.get("comments", instance.comments)
        instance.save(update_fields=["completed", "evaluation", "comments", "updated_at"])
        return instance


# ─── Assignment ────────────────────────────────────────────────────────────────

class AssignmentSerializer(serializers.ModelSerializer):
    student_name    = serializers.CharField(source="student.full_name",        read_only=True)
    student_id_code = serializers.CharField(source="student.student_id",       read_only=True)
    room_detail     = serializers.CharField(source="room.__str__",             read_only=True)
    assigned_by_name= serializers.CharField(source="assigned_by.get_full_name",read_only=True)
    is_active       = serializers.BooleanField(read_only=True)

    class Meta:
        model  = Assignment
        fields = [
            "id", "student", "student_name", "student_id_code",
            "room", "room_detail",
            "assigned_date", "released_date", "is_active",
            "assigned_by", "assigned_by_name",
            "created_at", "updated_at",
        ]
        read_only_fields = ["assigned_by", "released_date", "created_at", "updated_at"]

    def validate(self, attrs):
        """Validaciones de negocio antes de crear la asignación."""
        student = attrs.get("student")
        room    = attrs.get("room")

        # Validar que el estudiante no tenga asignación activa
        if student and Assignment.objects.filter(
            student=student, released_date__isnull=True
        ).exists():
            raise serializers.ValidationError({
                "student": (
                    f"El estudiante '{student.full_name}' ya tiene una asignación activa. "
                    "Libera el cuarto actual antes de asignar uno nuevo."
                )
            })

        # Validar que el cuarto no esté lleno
        if room and room.is_full:
            raise serializers.ValidationError({
                "room": (
                    f"El cuarto {room.number} está lleno "
                    f"({room.current_occupancy}/{room.capacity} plazas)."
                )
            })

        # Validar que el cuarto esté activo
        if room and not room.is_active:
            raise serializers.ValidationError({
                "room": f"El cuarto {room.number} está deshabilitado."
            })

        return attrs

    def create(self, validated_data):
        validated_data["assigned_by"] = self.context["request"].user
        return super().create(validated_data)


class AssignmentReleaseSerializer(serializers.Serializer):
    """Liberar un cuarto (RF-49)."""
    released_date = serializers.DateField(default=timezone.now)

    def update(self, instance, validated_data):
        if instance.released_date is not None:
            raise serializers.ValidationError(
                "Esta asignación ya fue liberada el "
                f"{instance.released_date}."
            )
        instance.released_date = validated_data["released_date"]
        instance.save(update_fields=["released_date", "updated_at"])
        return instance


# ─── Information ───────────────────────────────────────────────────────────────

class InformationSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source="created_by.get_full_name", read_only=True)
    published_date = serializers.DateField(required=False, allow_null=True)

    class Meta:
        model  = Information
        fields = [
            "id", "title", "content",
            "published_date", "expires_date", "is_public",
            "created_by", "created_by_name",
            "created_at", "updated_at",
        ]
        read_only_fields = ["created_by", "created_at", "updated_at"]

    def create(self, validated_data):
        # Si no se proporciona published_date, usar la fecha actual
        if "published_date" not in validated_data or validated_data["published_date"] is None:
            validated_data["published_date"] = timezone.now().date()
        validated_data["created_by"] = self.context["request"].user
        return super().create(validated_data)


class InformationPublicSerializer(serializers.ModelSerializer):
    """Versión reducida para estudiantes — sin campos de gestión."""
    class Meta:
        model  = Information
        fields = ["id", "title", "content", "published_date", "expires_date"]


# ─── Report ────────────────────────────────────────────────────────────────────

class ReportSerializer(serializers.ModelSerializer):
    generated_by_name = serializers.CharField(source="generated_by.get_full_name", read_only=True)

    class Meta:
        model  = Report
        fields = [
            "id", "name", "type", "parameters", "file_url",
            "generated_by", "generated_by_name", "generated_date",
        ]
        read_only_fields = ["generated_by", "generated_date", "file_url"]

    def create(self, validated_data):
        validated_data["generated_by"] = self.context["request"].user
        return super().create(validated_data)
