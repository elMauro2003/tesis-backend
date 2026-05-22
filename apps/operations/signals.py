"""
Equivale al trigger de PostgreSQL mencionado en el esquemaDB §2.4:
"El campo current_occupancy se mantiene sincronizado automáticamente
mediante un trigger en la tabla assignments."

"""
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import Count


def _recalculate_occupancy(room):
    """
    Recalcula y persiste current_occupancy del cuarto basándose en
    el conteo real de asignaciones activas (released_date IS NULL).

    Usamos update() en lugar de save() para:
    - Evitar disparar señales en cascada
    - Ejecutar un solo UPDATE en la BD
    - No tocar updated_at del cuarto innecesariamente
    """
    from apps.operations.models import Assignment
    from apps.infrastructure.models import Room

    active_count = Assignment.objects.filter(
        room=room, released_date__isnull=True
    ).count()

    Room.objects.filter(pk=room.pk).update(current_occupancy=active_count)


# Importación diferida para evitar importaciones circulares en ready()
def _get_assignment_model():
    from apps.operations.models import Assignment
    return Assignment


@receiver(post_save, sender="operations.Assignment")
def update_occupancy_on_assignment_save(sender, instance, created, **kwargs):
    """
    Se dispara al CREAR o ACTUALIZAR una asignación.

    Casos que actualiza:
    - Nueva asignación activa (released_date=None) → +1 en el cuarto
    - Asignación liberada (released_date establecida) → -1 en el cuarto
    - Cambio de cuarto (raro, pero cubierto por recálculo completo)
    """
    _recalculate_occupancy(instance.room)


@receiver(post_delete, sender="operations.Assignment")
def update_occupancy_on_assignment_delete(sender, instance, **kwargs):
    """
    Se dispara al ELIMINAR una asignación.
    Necesario para mantener consistencia si se borra un registro directamente.
    """
    _recalculate_occupancy(instance.room)
