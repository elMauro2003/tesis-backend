from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model
from .models import Student, Professor, Dean, GroupAdvisor, YearLeadProfessor, WingSupervisor

User = get_user_model()


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display  = ["full_name", "student_id", "ci", "group", "gender"]
    list_filter   = ["gender", "group__career_year__career__faculty", "is_militant"]
    search_fields = ["user__first_name", "user__last_name", "student_id", "ci"]
    readonly_fields = ["current_room"]

    @admin.display(description="Nombre Completo")
    def full_name(self, obj):
        return obj.full_name

    @admin.display(description="Cuarto Actual")
    def current_room(self, obj):
        return str(obj.current_room) if obj.current_room else "Sin asignar"


@admin.register(Professor)
class ProfessorAdmin(admin.ModelAdmin):
    list_display  = ["__str__", "employee_id", "department"]
    search_fields = ["user__first_name", "user__last_name", "employee_id"]


@admin.register(Dean)
class DeanAdmin(admin.ModelAdmin):
    list_display = ["professor", "faculty"]


@admin.register(GroupAdvisor)
class GroupAdvisorAdmin(admin.ModelAdmin):
    list_display = ["professor", "group"]


@admin.register(YearLeadProfessor)
class YearLeadProfessorAdmin(admin.ModelAdmin):
    list_display = ["professor", "career_year"]


@admin.register(WingSupervisor)
class WingSupervisorAdmin(admin.ModelAdmin):
    list_display = ["professor", "wing"]
