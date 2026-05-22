from rest_framework import serializers
from .models import Faculty, Career, CareerYear, Group


class FacultySerializer(serializers.ModelSerializer):
    career_count = serializers.IntegerField(
        source="careers.count", read_only=True,
        help_text="Número de carreras en esta facultad",
    )

    class Meta:
        model  = Faculty
        fields = ["id", "name", "code", "career_count", "created_at", "updated_at"]
        read_only_fields = ["created_at", "updated_at"]


class CareerSerializer(serializers.ModelSerializer):
    faculty_name = serializers.CharField(source="faculty.name", read_only=True)

    class Meta:
        model  = Career
        fields = ["id", "name", "code", "faculty", "faculty_name", "created_at", "updated_at"]
        read_only_fields = ["created_at", "updated_at"]


class CareerYearSerializer(serializers.ModelSerializer):
    career_name = serializers.CharField(source="career.name", read_only=True)
    year_display = serializers.CharField(source="get_year_display", read_only=True)

    class Meta:
        model  = CareerYear
        fields = ["id", "career", "career_name", "year", "year_display", "created_at", "updated_at"]
        read_only_fields = ["created_at", "updated_at"]


class GroupSerializer(serializers.ModelSerializer):
    # Anidado de solo lectura para dar contexto completo sin joins adicionales
    career_year_detail = CareerYearSerializer(source="career_year", read_only=True)

    class Meta:
        model  = Group
        fields = ["id", "name", "career_year", "career_year_detail", "created_at", "updated_at"]
        read_only_fields = ["created_at", "updated_at"]
