from django.contrib import admin
from .models import Faculty, Career, CareerYear, Group


@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):
    list_display  = ["name", "code", "created_at"]
    search_fields = ["name", "code"]


@admin.register(Career)
class CareerAdmin(admin.ModelAdmin):
    list_display  = ["name", "code", "faculty"]
    list_filter   = ["faculty"]
    search_fields = ["name", "code"]


@admin.register(CareerYear)
class CareerYearAdmin(admin.ModelAdmin):
    list_display = ["career", "year"]
    list_filter  = ["year", "career__faculty"]


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ["name", "career_year"]
    list_filter  = ["career_year__career__faculty", "career_year__year"]
