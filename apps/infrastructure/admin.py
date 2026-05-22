from django.contrib import admin
from .models import Site, Building, Wing, Room


@admin.register(Site)
class SiteAdmin(admin.ModelAdmin):
    list_display  = ["name", "address"]
    search_fields = ["name"]


@admin.register(Building)
class BuildingAdmin(admin.ModelAdmin):
    list_display  = ["name", "site"]
    list_filter   = ["site"]
    search_fields = ["name"]


@admin.register(Wing)
class WingAdmin(admin.ModelAdmin):
    list_display  = ["name", "building"]
    list_filter   = ["building__site"]
    search_fields = ["name", "building__name"]


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display  = ["number", "wing", "capacity", "current_occupancy", "is_active", "is_full"]
    list_filter   = ["is_active", "wing__building__site"]
    search_fields = ["number"]
    readonly_fields = ["current_occupancy"]  # Solo lectura — lo actualiza la señal

    @admin.display(boolean=True, description="¿Lleno?")
    def is_full(self, obj):
        return obj.is_full
