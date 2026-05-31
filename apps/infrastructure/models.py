from django.db import models


class BuildingGender(models.TextChoices):
    VARONES = "Varones", "Varones"
    HEMBRAS = "Hembras", "Hembras"
    MIXTO = "Mixto", "Mixto"


class Site(models.Model):
    name = models.CharField(
        max_length=100, unique=True, verbose_name="Nombre",
    )
    address = models.TextField(
        blank=True, null=True, verbose_name="Dirección / Ubicación",
    )
    description = models.TextField(
        blank=True, null=True, verbose_name="Descripción",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "sites"
        verbose_name = "Sede"
        verbose_name_plural = "Sedes"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Building(models.Model):
    """
    Edificio dentro de una sede.
    Relaciones inversas:
        building.wings      → QuerySet[Wing]
        building.complaints → QuerySet[Complaint]  (en operations)
    """
    site = models.ForeignKey(
        Site, on_delete=models.PROTECT, related_name="buildings", verbose_name="Sede",
    )
    name = models.CharField(
        max_length=50, verbose_name="Nombre / Número",
        help_text="Nombre o número identificador del edificio",
    )
    gender = models.CharField(
        max_length=10,
        choices=BuildingGender.choices,
        default=BuildingGender.MIXTO,
        verbose_name="Sexo de los estudiantes",
        help_text="Define qué sexo de estudiantes aloja el edificio",
    )
    address = models.TextField(
        blank=True, null=True, verbose_name="Dirección",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "buildings"
        verbose_name = "Edificio"
        verbose_name_plural = "Edificios"
        ordering = ["site", "name"]

    def __str__(self):
        return f"Edificio {self.name} — {self.site}"


class Wing(models.Model):
    """
    Relaciones inversas:
        wing.rooms           → QuerySet[Room]
        wing.wing_supervisor → WingSupervisor | None  (en actors)
    """
    building = models.ForeignKey(
        Building, on_delete=models.PROTECT, related_name="wings", verbose_name="Edificio",
    )
    name = models.CharField(
        max_length=20, verbose_name="Nombre / Identificador",
        help_text="Identificador del ala (ej: 'A', 'B', 'Norte')",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "wings"
        verbose_name = "Ala"
        verbose_name_plural = "Alas"
        ordering = ["building", "name"]
        constraints = [
            # Refleja UNIQUE(building_id, name) del esquemaDB §2.3
            models.UniqueConstraint(fields=["building", "name"], name="uq_building_wing"),
        ]

    def __str__(self):
        return f"Ala {self.name} — {self.building}"


class Room(models.Model):
    """
    Relaciones inversas:
        room.assignments        → QuerySet[Assignment]
        room.cleaning_schedules → QuerySet[CleaningSchedule]
    """
    wing = models.ForeignKey(
        Wing, on_delete=models.PROTECT, related_name="rooms", verbose_name="Ala",
    )
    number = models.CharField(
        max_length=10, verbose_name="Número / Identificador",
    )
    capacity = models.PositiveSmallIntegerField(
        verbose_name="Capacidad máxima",
        help_text="Número máximo de estudiantes que puede alojar el cuarto",
    )
    # Sincronizado automáticamente por señales — no modificar manualmente
    current_occupancy = models.PositiveSmallIntegerField(
        default=0, verbose_name="Ocupación actual",
        help_text="Se actualiza automáticamente con las asignaciones activas",
    )
    is_active = models.BooleanField(
        default=True, verbose_name="Habilitado",
        help_text="Desactivar para cuartos fuera de servicio sin eliminarlos",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "rooms"
        verbose_name = "Cuarto"
        verbose_name_plural = "Cuartos"
        ordering = ["wing", "number"]
        constraints = [
            # UNIQUE(wing_id, number) — esquemaDB §2.4
            models.UniqueConstraint(fields=["wing", "number"], name="uq_wing_room"),
            # CHECK: current_occupancy <= capacity
            models.CheckConstraint(
                check=models.Q(current_occupancy__lte=models.F("capacity")),
                name="chk_occupancy_lte_capacity",
            ),
            # CHECK: capacity > 0
            models.CheckConstraint(
                check=models.Q(capacity__gt=0),
                name="chk_capacity_positive",
            ),
        ]

    def __str__(self):
        return f"Cuarto {self.number} — {self.wing}"

    @property
    def is_full(self) -> bool:
        """True si el cuarto alcanzó su capacidad máxima."""
        return self.current_occupancy >= self.capacity

    @property
    def available_spots(self) -> int:
        """Número de plazas disponibles."""
        return max(0, self.capacity - self.current_occupancy)
