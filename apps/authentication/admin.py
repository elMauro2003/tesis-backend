from django.contrib import admin
from django.contrib.auth import get_user_model
from apps.authentication.models import User


User = get_user_model()

# agrega un filtro por grupo de usuarios
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ["username", "email", "first_name", "last_name", "is_staff", "is_active"]
    list_filter = ["is_staff", "is_active", "groups"]
    search_fields = ["username", "email", "first_name", "last_name"]