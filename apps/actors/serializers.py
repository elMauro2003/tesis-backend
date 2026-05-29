from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.academic.models import CareerYear
from apps.academic.serializers import GroupSerializer
from .models import Student, Professor, Dean, GroupAdvisor, YearLeadProfessor, WingSupervisor

User = get_user_model()


# ─── User inline (embebido en Student y Professor) ─────────────────────────────

class UserInlineSerializer(serializers.ModelSerializer):
    """Representación mínima del User para embeber en Student/Professor."""
    class Meta:
        model  = User
        fields = ["id", "username", "email", "first_name", "last_name", "is_active"]
        read_only_fields = fields


# ─── Student ───────────────────────────────────────────────────────────────────

class StudentSerializer(serializers.ModelSerializer):
    """
    Serializer completo de estudiante para creación y detalle.
    Incluye current_room_info para evitar una llamada extra al frontend.
    """
    user         = UserInlineSerializer(read_only=True)
    group_detail = GroupSerializer(source="group", read_only=True)
    full_name    = serializers.CharField(read_only=True)
    current_room_info = serializers.SerializerMethodField()

    class Meta:
        model  = Student
        fields = [
            "id", "user", "full_name",
            "ci", "student_id", "birth_date", "gender",
            "address", "province", "municipality", "phone", "emergency_phone",
            "illnesses", "medications",
            "is_militant", "is_cadet_minint", "is_cadet_far",
            "academic_performance", "disciplinary_process",
            "group", "group_detail",
            "current_room_info",
            "created_at", "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]

    def get_current_room_info(self, obj) -> dict | None:
        assignment = obj.active_assignment
        if not assignment:
            return None
        room = assignment.room
        return {
            "assignment_id": assignment.id,
            "room_id":       room.id,
            "room_number":   room.number,
            "wing":          room.wing.name,
            "building":      room.wing.building.name,
            "assigned_date": assignment.assigned_date,
        }


class StudentListSerializer(serializers.ModelSerializer):
    full_name    = serializers.CharField(read_only=True)
    group_name   = serializers.CharField(source="group.__str__", read_only=True)
    has_room     = serializers.SerializerMethodField()

    class Meta:
        model  = Student
        fields = [
            "id", "full_name", "student_id", "ci",
            "gender", "group", "group_name", "has_room",
        ]

    def get_has_room(self, obj) -> bool:
        return obj.current_room is not None


class StudentCreateSerializer(serializers.ModelSerializer):
    """
    Crea un Student junto con su User en una sola operación atómica.
    Recibe los datos del user anidados.
    El grupo se auto-asigna basado en career y year.
    """
    username   = serializers.CharField(write_only=True)
    first_name = serializers.CharField(write_only=True)
    last_name  = serializers.CharField(write_only=True)
    password   = serializers.CharField(write_only=True, style={"input_type": "password"})
    
    # Auto-asignación de grupo basado en carrera y año
    career = serializers.IntegerField(write_only=True, help_text="ID de la carrera")
    year   = serializers.IntegerField(write_only=True, help_text="Año académico (1-5)")

    birth_date = serializers.DateField(required=False, allow_null=True)

    class Meta:
        model = Student
        fields = [
            # PASO 1: Datos Personales
            "username", "first_name", "last_name", "password",
            "ci", "birth_date", "gender",
            "address", "province", "municipality", "phone", "emergency_phone",
            # PASO 2: Datos Académicos
            "career", "year", "academic_performance",
            # PASO 3: Salud y Perfil
            "illnesses", "medications",
            "is_militant", "is_cadet_minint", "is_cadet_far",
            "disciplinary_process",
        ]
        extra_kwargs = {
            # PASO 2: Campos opcionales
            "academic_performance": {"required": False, "allow_blank": True},
            # PASO 3: Campos opcionales
            "illnesses": {"required": False, "allow_blank": True},
            "medications": {"required": False, "allow_blank": True},
            "is_militant": {"required": False},
            "is_cadet_minint": {"required": False},
            "is_cadet_far": {"required": False},
            "disciplinary_process": {"required": False, "allow_blank": True},
            "birth_date": {"required": False, "allow_null": True},
        }
    def create(self, validated_data):
        from django.db import transaction, IntegrityError
        from django.contrib.auth.models import Group as DjangoGroup
        from rest_framework.exceptions import NotFound

        # Extraer campos del User
        user_fields = {
            k: validated_data.pop(k)
            for k in ["username", "first_name", "last_name", "password"]
        }
        
        # Auto-asignar grupo basado en career y year
        career_id = validated_data.pop("career")
        year = validated_data.pop("year")
        
        try:
            career_year = CareerYear.objects.get(career_id=career_id, year=year)
        except CareerYear.DoesNotExist:
            raise NotFound(
                detail=f"No existe año académico para la carrera {career_id} año {year}"
            )
        
        group = career_year.groups.first()
        if not group:
            raise NotFound(
                detail=f"No hay grupos disponibles para {career_year}"
            )
        
        validated_data["group"] = group

        # Generar birth_date si no viene
        from datetime import date
        import random
        if not validated_data.get("birth_date"):
            validated_data["birth_date"] = date(
                random.randint(1999, 2006),
                random.randint(1, 12),
                random.randint(1, 28),
            )
        with transaction.atomic():
            try:
                # Crear User con contraseña hasheada
                user = User.objects.create_user(**user_fields)
            except IntegrityError:
                raise serializers.ValidationError({
                    "username": ["Ya existe un usuario con ese username."]
                })
            # Asignar rol 'estudiante' automáticamente
            student_group = DjangoGroup.objects.filter(name="estudiante").first()
            if student_group:
                user.groups.add(student_group)
            # Generar student_id si no viene
            if not validated_data.get("student_id"):
                import random
                validated_data["student_id"] = f"STD{user.id:05d}{random.randint(100,999)}"
            # Crear Student
            student = Student.objects.create(user=user, **validated_data)

        return student

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Ya existe un usuario con ese username.")
        return value


# ─── Professor ─────────────────────────────────────────────────────────────────

class ProfessorSerializer(serializers.ModelSerializer):
    user      = UserInlineSerializer(read_only=True)
    full_name = serializers.CharField(source="user.get_full_name", read_only=True)
    # Sub-roles actuales del profesor
    is_dean                = serializers.BooleanField(source="dean.__bool__",               read_only=True, default=False)
    is_group_advisor       = serializers.BooleanField(source="group_advisor.__bool__",      read_only=True, default=False)
    is_year_lead_professor = serializers.BooleanField(source="year_lead_professor.__bool__",read_only=True, default=False)
    is_wing_supervisor     = serializers.BooleanField(source="wing_supervisor.__bool__",    read_only=True, default=False)

    class Meta:
        model  = Professor
        fields = [
            "id", "user", "full_name", "employee_id", "department",
            "is_dean", "is_group_advisor", "is_year_lead_professor", "is_wing_supervisor",
            "created_at", "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]


class ProfessorCreateSerializer(serializers.ModelSerializer):
    """Crea un Professor con su User asociado."""
    username   = serializers.CharField(write_only=True)
    email      = serializers.EmailField(write_only=True)
    first_name = serializers.CharField(write_only=True)
    last_name  = serializers.CharField(write_only=True)
    password   = serializers.CharField(write_only=True, style={"input_type": "password"})

    class Meta:
        model  = Professor
        fields = ["username", "email", "first_name", "last_name", "password",
                  "employee_id", "department"]

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Ya existe un usuario con ese username.")
        return value

    def create(self, validated_data):
        from django.db import transaction, IntegrityError
        user_fields = {
            k: validated_data.pop(k)
            for k in ["username", "email", "first_name", "last_name", "password"]
        }
        with transaction.atomic():
            try:
                user = User.objects.create_user(**user_fields)
            except IntegrityError:
                raise serializers.ValidationError({
                    "username": ["Ya existe un usuario con ese username."]
                })
            professor = Professor.objects.create(user=user, **validated_data)
        return professor


# ─── Sub-roles ─────────────────────────────────────────────────────────────────

class DeanSerializer(serializers.ModelSerializer):
    professor_name = serializers.CharField(source="professor.__str__", read_only=True)
    faculty_name   = serializers.CharField(source="faculty.name",      read_only=True)

    class Meta:
        model  = Dean
        fields = ["professor", "professor_name", "faculty", "faculty_name"]


class GroupAdvisorSerializer(serializers.ModelSerializer):
    professor_name = serializers.CharField(source="professor.__str__", read_only=True)
    group_name     = serializers.CharField(source="group.__str__",     read_only=True)

    class Meta:
        model  = GroupAdvisor
        fields = ["professor", "professor_name", "group", "group_name"]


class YearLeadProfessorSerializer(serializers.ModelSerializer):
    professor_name   = serializers.CharField(source="professor.__str__",    read_only=True)
    career_year_name = serializers.CharField(source="career_year.__str__",  read_only=True)

    class Meta:
        model  = YearLeadProfessor
        fields = ["professor", "professor_name", "career_year", "career_year_name"]


class WingSupervisorSerializer(serializers.ModelSerializer):
    professor_name = serializers.CharField(source="professor.__str__", read_only=True)
    wing_name      = serializers.CharField(source="wing.__str__",      read_only=True)

    class Meta:
        model  = WingSupervisor
        fields = ["professor", "professor_name", "wing", "wing_name"]
