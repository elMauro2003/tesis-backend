"""
Nota: un Professor puede tener múltiples roles simultáneamente.
"""
from django.db import models
from django.contrib.auth import get_user_model

from apps.academic.models import Faculty, CareerYear, Group
from apps.infrastructure.models import Wing

User = get_user_model()


# ─── Student ───────────────────────────────────────────────────────────────────

class Student(models.Model):
    """
    Relaciones inversas:
        student.complaints        → QuerySet[Complaint]
        student.evaluations       → QuerySet[Evaluation]
        student.cleaning_schedules→ QuerySet[CleaningSchedule]
        student.assignments       → QuerySet[Assignment]
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="student",
        verbose_name="Usuario",
    )
    ci = models.CharField(
        max_length=11, unique=True, verbose_name="Carné de Identidad",
    )
    student_id = models.CharField(
        max_length=20, unique=True, verbose_name="Matrícula / Expediente",
    )
    birth_date = models.DateField(verbose_name="Fecha de Nacimiento")

    GENDER_CHOICES = [("M", "Masculino"), ("F", "Femenino")]
    gender = models.CharField(
        max_length=1, choices=GENDER_CHOICES, verbose_name="Sexo",
    )

    address   = models.TextField(blank=True, null=True, verbose_name="Dirección particular")
    province  = models.CharField(max_length=50, blank=True, null=True, verbose_name="Provincia")
    municipality = models.CharField(max_length=50, blank=True, null=True, verbose_name="Municipio")
    phone           = models.CharField(max_length=20, blank=True, null=True, verbose_name="Teléfono")
    emergency_phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Teléfono de familiar")

    # Datos de salud — sensibles, acceso restringido por RBAC
    illnesses   = models.TextField(blank=True, null=True, verbose_name="Enfermedades")
    medications = models.TextField(blank=True, null=True, verbose_name="Medicamentos")

    # Contexto social / político (requerido por el sistema de la UCLV)
    is_militant     = models.BooleanField(default=False, verbose_name="Militante UJC/PCC")
    is_cadet_minint = models.BooleanField(default=False, verbose_name="Cadete MININT")
    is_cadet_far    = models.BooleanField(default=False, verbose_name="Cadete FAR")

    # Seguimiento académico y disciplinario
    academic_performance = models.TextField(
        blank=True, null=True, verbose_name="Aprovechamiento Docente",
    )
    disciplinary_process = models.TextField(
        blank=True, null=True, verbose_name="Proceso Disciplinario",
    )

    group = models.ForeignKey(
        Group,
        on_delete=models.PROTECT,
        related_name="students",
        verbose_name="Grupo Académico",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "students"
        verbose_name = "Estudiante"
        verbose_name_plural = "Estudiantes"
        ordering = ["user__last_name", "user__first_name"]

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.student_id})"

    @property
    def full_name(self) -> str:
        return self.user.get_full_name()

    @property
    def active_assignment(self):
        """Devuelve la asignación activa o None — fuente única de verdad."""
        return self.assignments.filter(released_date__isnull=True).first()

    @property
    def current_room(self):
        """Atajo al cuarto actual del estudiante o None."""
        assignment = self.active_assignment
        return assignment.room if assignment else None


# ─── Professor ─────────────────────────────────────────────────────────────────

class Professor(models.Model):
    """
    Relaciones inversas:
        professor.dean               → Dean | None
        professor.group_advisor      → GroupAdvisor | None
        professor.year_lead_professor→ YearLeadProfessor | None
        professor.wing_supervisor    → WingSupervisor | None
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="professor",
        verbose_name="Usuario",
    )
    employee_id = models.CharField(
        max_length=20, unique=True, verbose_name="ID de Empleado",
    )
    department = models.CharField(
        max_length=100, blank=True, null=True, verbose_name="Departamento",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "professors"
        verbose_name = "Profesor"
        verbose_name_plural = "Profesores"
        ordering = ["user__last_name", "user__first_name"]

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.employee_id})"


# ─── Professor Sub-roles ───────────────────────────────────────────────────────

class Dean(models.Model):
    """
    Decano
    PK = professor_id (patrón de herencia multi-tabla con PK compartida).
    """
    professor = models.OneToOneField(
        Professor,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name="dean",
        verbose_name="Profesor",
    )
    faculty = models.OneToOneField(
        Faculty,
        on_delete=models.PROTECT,
        related_name="dean",
        verbose_name="Facultad supervisada",
    )

    class Meta:
        db_table = "deans"
        verbose_name = "Decano"
        verbose_name_plural = "Decanos"

    def __str__(self):
        return f"Decano {self.professor} → {self.faculty}"


class GroupAdvisor(models.Model):
    """
    Profesor Guía (PG)
    """
    professor = models.OneToOneField(
        Professor,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name="group_advisor",
        verbose_name="Profesor",
    )
    group = models.OneToOneField(
        Group,
        on_delete=models.PROTECT,
        related_name="group_advisor",
        verbose_name="Grupo asesorado",
    )

    class Meta:
        db_table = "group_advisors"
        verbose_name = "Profesor Guía"
        verbose_name_plural = "Profesores Guías"

    def __str__(self):
        return f"PG {self.professor} → {self.group}"


class YearLeadProfessor(models.Model):
    professor = models.OneToOneField(
        Professor,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name="year_lead_professor",
        verbose_name="Profesor",
    )
    career_year = models.OneToOneField(
        CareerYear,
        on_delete=models.PROTECT,
        related_name="year_lead_professor",
        verbose_name="Año Académico supervisado",
    )

    class Meta:
        db_table = "year_lead_professors"
        verbose_name = "Profesor Principal de Año"
        verbose_name_plural = "Profesores Principales de Año"

    def __str__(self):
        return f"PPA {self.professor} → {self.career_year}"


class WingSupervisor(models.Model):
    professor = models.OneToOneField(
        Professor,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name="wing_supervisor",
        verbose_name="Profesor / Instructor",
    )
    wing = models.OneToOneField(
        Wing,
        on_delete=models.PROTECT,
        related_name="wing_supervisor",
        verbose_name="Ala supervisada",
    )

    class Meta:
        db_table = "wing_supervisors"
        verbose_name = "Responsable de Ala"
        verbose_name_plural = "Responsables de Ala"

    def __str__(self):
        return f"Instructor {self.professor} → {self.wing}"
