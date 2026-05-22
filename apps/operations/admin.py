from django.contrib import admin
from .models import Complaint, Evaluation, CleaningSchedule, Assignment, Information, Report


@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display  = ["__str__", "type", "status", "visibility", "date"]
    list_filter   = ["type", "status", "visibility"]
    search_fields = ["student__user__last_name", "description"]
    readonly_fields = ["response_date"]


@admin.register(Evaluation)
class EvaluationAdmin(admin.ModelAdmin):
    list_display  = ["student", "grade", "date", "created_by"]
    list_filter   = ["grade"]
    search_fields = ["student__user__last_name"]


@admin.register(CleaningSchedule)
class CleaningScheduleAdmin(admin.ModelAdmin):
    list_display = ["student", "room", "assigned_date", "completed", "evaluation"]
    list_filter  = ["completed", "evaluation"]


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display    = ["student", "room", "assigned_date", "released_date", "is_active"]
    list_filter     = ["room__wing__building__site"]
    search_fields   = ["student__user__last_name", "student__student_id"]
    readonly_fields = ["is_active"]

    @admin.display(boolean=True, description="¿Activa?")
    def is_active(self, obj):
        return obj.is_active


@admin.register(Information)
class InformationAdmin(admin.ModelAdmin):
    list_display = ["title", "published_date", "expires_date", "is_public", "created_by"]
    list_filter  = ["is_public"]
    search_fields = ["title"]


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display  = ["name", "type", "generated_by", "generated_date"]
    list_filter   = ["type"]
    search_fields = ["name"]
