from rest_framework import serializers
from .models import Site, Building, Wing, Room


class SiteSerializer(serializers.ModelSerializer):
    building_count = serializers.IntegerField(source="buildings.count", read_only=True)

    class Meta:
        model  = Site
        fields = ["id", "name", "address", "description", "building_count", "created_at", "updated_at"]
        read_only_fields = ["created_at", "updated_at"]


class BuildingSerializer(serializers.ModelSerializer):
    site_name  = serializers.CharField(source="site.name", read_only=True)
    wing_count = serializers.IntegerField(source="wings.count", read_only=True)

    class Meta:
        model  = Building
        fields = ["id", "name", "address", "site", "site_name", "wing_count", "created_at", "updated_at"]
        read_only_fields = ["created_at", "updated_at"]


class WingSerializer(serializers.ModelSerializer):
    building_name = serializers.CharField(source="building.name", read_only=True)
    site_name     = serializers.CharField(source="building.site.name", read_only=True)
    room_count    = serializers.IntegerField(source="rooms.count", read_only=True)

    class Meta:
        model  = Wing
        fields = [
            "id", "name", "building", "building_name", "site_name",
            "room_count", "created_at", "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]


class RoomSerializer(serializers.ModelSerializer):
    wing_name     = serializers.CharField(source="wing.name", read_only=True)
    building_name = serializers.CharField(source="wing.building.name", read_only=True)
    # Campos calculados del modelo
    is_full          = serializers.BooleanField(read_only=True)
    available_spots  = serializers.IntegerField(read_only=True)

    class Meta:
        model  = Room
        fields = [
            "id", "number", "wing", "wing_name", "building_name",
            "capacity", "current_occupancy", "is_active",
            "is_full", "available_spots",
            "created_at", "updated_at",
        ]
        read_only_fields = ["current_occupancy", "created_at", "updated_at"]


class RoomListSerializer(serializers.ModelSerializer):
    """Versión compacta para listados — menos campos, más rápido."""
    is_full = serializers.BooleanField(read_only=True)

    class Meta:
        model  = Room
        fields = ["id", "number", "wing", "capacity", "current_occupancy", "is_active", "is_full"]
        read_only_fields = ["current_occupancy"]
