from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.actors.models import Student
from apps.infrastructure.models import Building, Room

User = get_user_model()


# ─── Complaint ─────────────────────────────────────────────────────────────────

class Complaint(models.Model):
    TYPE_CHOICES = [
        ("administrativa", "Administrativa"),
        ("educativa",      "Educativa"),
    ]
    STATUS_CHOICES = [
        ("pendiente",   "Pendiente"),
        ("en_proceso",  "En proceso"),
        ("resuelta",    "Resuelta"),
        ("rechazada",   "Rechazada"),
    ]

    student = models.ForeignKey(
        Student, on_delete=models.PROTECT,
        related_name="complaints", verbose_name="Estudiante",
    )
    date = models.DateField(
        default=timezone.now, verbose_name="Fecha de la queja",
    )
    # Edificio opcional: permite asociar la queja a una infraestructura específica
    building = models.ForeignKey(
        Building, on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="complaints", verbose_name="Edificio relacionado",
    )
    description = models.TextField(verbose_name="Descripción")
    type = models.CharField(
        max_length=20, choices=TYPE_CHOICES, verbose_name="Tipo",
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES,
        default="pendiente", verbose_name="Estado",
    )
    # Visibilidad: si True, otros estudiantes pueden ver la queja (anonimizada)
    visibility = models.BooleanField(
        default=False, verbose_name="Visible para otros estudiantes",
    )
    # Respuesta del subdirector
    response      = models.TextField(blank=True, null=True, verbose_name="Respuesta")
    response_date = models.DateTimeField(blank=True, null=True, verbose_name="Fecha de respuesta")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "complaints"
        verbose_name = "Queja"
        verbose_name_plural = "Quejas"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Queja #{self.pk} — {self.student} ({self.status})"


# ─── Evaluation ────────────────────────────────────────────────────────────────

class Evaluation(models.Model):
    GRADE_CHOICES = [
        ("B", "Bien"),
        ("R", "Regular"),
        ("M", "Mal"),
    ]

    student = models.ForeignKey(
        Student, on_delete=models.PROTECT,
        related_name="evaluations", verbose_name="Estudiante evaluado",
    )
    date = models.DateField(
        default=timezone.now, verbose_name="Fecha de evaluación",
    )
    grade = models.CharField(
        max_length=1, choices=GRADE_CHOICES, verbose_name="Calificación",
    )
    comment = models.TextField(
        blank=True, null=True, verbose_name="Comentario del instructor",
    )
    # El instructor que registra la evaluación
    created_by = models.ForeignKey(
        User, on_delete=models.PROTECT,
        related_name="evaluations_created", verbose_name="Registrado por",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "evaluations"
        verbose_name = "Evaluación"
        verbose_name_plural = "Evaluaciones"
        ordering = ["-date", "-created_at"]

    def __str__(self):
        return f"Eval {self.get_grade_display()} — {self.student} ({self.date})"


# ─── CleaningSchedule ──────────────────────────────────────────────────────────

class CleaningSchedule(models.Model):
    EVAL_CHOICES = [
        ("B", "Bien"),
        ("R", "Regular"),
        ("M", "Mal"),
    ]

    room = models.ForeignKey(
        Room, on_delete=models.PROTECT,
        related_name="cleaning_schedules", verbose_name="Cuarto a limpiar",
    )
    student = models.ForeignKey(
        Student, on_delete=models.PROTECT,
        related_name="cleaning_schedules", verbose_name="Estudiante asignado",
    )
    assigned_date = models.DateField(verbose_name="Fecha asignada")
    completed     = models.BooleanField(default=False, verbose_name="Completada")
    evaluation    = models.CharField(
        max_length=1, choices=EVAL_CHOICES,
        null=True, blank=True, verbose_name="Evaluación de la tarea",
    )
    comments = models.TextField(blank=True, null=True, verbose_name="Observaciones")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "cleaning_schedules"
        verbose_name = "Cuartelería"
        verbose_name_plural = "Cuartelerías"
        ordering = ["-assigned_date"]

    def __str__(self):
        return f"Cuartelería {self.assigned_date} — {self.student} → {self.room}"


# ─── Assignment ────────────────────────────────────────────────────────────────

class Assignment(models.Model):
    student = models.ForeignKey(
        Student, on_delete=models.PROTECT,
        related_name="assignments", verbose_name="Estudiante",
    )
    room = models.ForeignKey(
        Room, on_delete=models.PROTECT,
        related_name="assignments", verbose_name="Cuarto",
    )
    assigned_date = models.DateField(verbose_name="Fecha de asignación")
    released_date = models.DateField(
        null=True, blank=True, verbose_name="Fecha de liberación",
        help_text="NULL indica que la asignación está activa",
    )
    assigned_by = models.ForeignKey(
        User, on_delete=models.PROTECT,
        related_name="assignments_made", verbose_name="Asignado por",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "assignments"
        verbose_name = "Asignación de Cuarto"
        verbose_name_plural = "Asignaciones de Cuartos"
        ordering = ["-assigned_date"]

    def __str__(self):
        status = "ACTIVA" if self.released_date is None else f"liberada {self.released_date}"
        return f"Asignación {status} — {self.student} → {self.room}"

    @property
    def is_active(self) -> bool:
        return self.released_date is None


# ─── Information ───────────────────────────────────────────────────────────────

class Information(models.Model):
    title          = models.CharField(max_length=200, verbose_name="Título")
    content        = models.TextField(verbose_name="Contenido")
    published_date = models.DateField(default=timezone.now, verbose_name="Fecha de publicación")
    expires_date   = models.DateField(
        null=True, blank=True, verbose_name="Fecha de expiración",
    )
    is_public  = models.BooleanField(default=True, verbose_name="Visible para estudiantes")
    created_by = models.ForeignKey(
        User, on_delete=models.PROTECT,
        related_name="informations_created", verbose_name="Publicado por",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "information"
        verbose_name = "Información"
        verbose_name_plural = "Informaciones"
        ordering = ["-published_date"]

    def __str__(self):
        return f"{self.title} ({self.published_date})"


# ─── Report ────────────────────────────────────────────────────────────────────

class Report(models.Model):
    name           = models.CharField(max_length=200, verbose_name="Nombre del reporte")
    type           = models.CharField(max_length=50, verbose_name="Tipo de reporte")
    # JSONB en PostgreSQL: almacena los filtros/parámetros usados al generar
    parameters     = models.JSONField(null=True, blank=True, verbose_name="Parámetros")
    file_url       = models.CharField(
        max_length=500, blank=True, null=True, verbose_name="URL del archivo PDF",
    )
    generated_by   = models.ForeignKey(
        User, on_delete=models.PROTECT,
        related_name="reports_generated", verbose_name="Generado por",
    )
    generated_date = models.DateTimeField(default=timezone.now, verbose_name="Fecha de generación")

    class Meta:
        db_table = "reports"
        verbose_name = "Reporte"
        verbose_name_plural = "Reportes"
        ordering = ["-generated_date"]

    def __str__(self):
        return f"{self.name} ({self.generated_date.date()})"
