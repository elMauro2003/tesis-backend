"""
Dominio Académico

Entidades:
    Faculty      → Facultades
    Career       → Carreras
    CareerYear   → Años Académicos (1-5)
    Group        → Grupos estudiantiles

Jerarquía:
    Faculty → Career → CareerYear → Group → Student (en apps.actors)
"""
from django.db import models


class Faculty(models.Model):
    """
    Unidad organizativa de nivel superior.
    Relaciones inversas:
        faculty.careers  → QuerySet[Career]
        faculty.dean     → Dean | None  (OneToOne desde actors)
    """
    name = models.CharField(
        max_length=100, unique=True, verbose_name="Nombre",
    )
    code = models.CharField(
        max_length=10, unique=True, null=True, blank=True, verbose_name="Código",
        help_text="Abreviatura (ej: 'MATFISCOM')",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "faculties"
        verbose_name = "Facultad"
        verbose_name_plural = "Facultades"
        ordering = ["name"]

    def __str__(self):
        return f"{self.code} — {self.name}" if self.code else self.name


class Career(models.Model):
    """
    Programa académico.
    Relaciones inversas:
        career.career_years → QuerySet[CareerYear]
    """
    name = models.CharField(max_length=100, verbose_name="Nombre")
    code = models.CharField(
        max_length=10, unique=True, null=True, blank=True, verbose_name="Código",
    )
    faculty = models.ForeignKey(
        Faculty, on_delete=models.PROTECT, related_name="careers", verbose_name="Facultad",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "careers"
        verbose_name = "Carrera"
        verbose_name_plural = "Carreras"
        ordering = ["faculty", "name"]

    def __str__(self):
        return f"{self.name} ({self.faculty.code or self.faculty.name})"


class CareerYear(models.Model):
    """
    Relaciones inversas:
        career_year.groups              → QuerySet[Group]
        career_year.year_lead_professor → YearLeadProfessor | None
    """
    YEAR_CHOICES = [(i, f"{i}° Año") for i in range(1, 6)]

    career = models.ForeignKey(
        Career, on_delete=models.PROTECT, related_name="career_years", verbose_name="Carrera",
    )
    year = models.PositiveSmallIntegerField(
        choices=YEAR_CHOICES, verbose_name="Año",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "career_years"
        verbose_name = "Año Académico"
        verbose_name_plural = "Años Académicos"
        ordering = ["career", "year"]
        constraints = [
            models.UniqueConstraint(fields=["career", "year"], name="uq_career_year"),
        ]

    def __str__(self):
        return f"{self.career} — {self.year}° Año"


class Group(models.Model):
    """
    Unidad básica de organización estudiantil.
    Relaciones inversas:
        group.students      → QuerySet[Student]
        group.group_advisor → GroupAdvisor | None
    """
    name = models.CharField(
        max_length=20, verbose_name="Nombre",
        help_text="Identificador del grupo (ej: 'A', 'B', 'C-1')",
    )
    career_year = models.ForeignKey(
        CareerYear, on_delete=models.PROTECT, related_name="groups", verbose_name="Año Académico",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "groups"
        verbose_name = "Grupo"
        verbose_name_plural = "Grupos"
        ordering = ["career_year", "name"]

    def __str__(self):
        return f"{self.career_year} — Grupo {self.name}"
