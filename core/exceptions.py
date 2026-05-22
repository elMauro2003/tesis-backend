"""
core/exceptions.py

Handler de excepciones personalizado. Garantiza que TODOS los errores
de la API devuelvan el mismo formato JSON

{
    "error": {
        "code": "VALIDATION_ERROR",
        "message": "Los datos proporcionados no son válidos",
        "details": {
            "field_name": ["Este campo es obligatorio."]
        }
    }
}

Registrado en settings.py como EXCEPTION_HANDLER.
"""
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from django.db.models.deletion import ProtectedError


# Mapeo de códigos HTTP → código de error semántico
HTTP_CODE_MAP = {
    400: "VALIDATION_ERROR",
    401: "AUTHENTICATION_REQUIRED",
    403: "PERMISSION_DENIED",
    404: "NOT_FOUND",
    405: "METHOD_NOT_ALLOWED",
    409: "CONFLICT",
    429: "RATE_LIMIT_EXCEEDED",
    500: "INTERNAL_SERVER_ERROR",
}


def custom_exception_handler(exc, context):
    """
    Transforma todas las excepciones DRF al formato estándar del proyecto.
    Las excepciones no manejadas por DRF se dejan pasar (Django las maneja).
    """
    # Primero dejamos que DRF haga su trabajo normal
    response = exception_handler(exc, context)

    if response is not None:
        http_code = response.status_code
        error_code = HTTP_CODE_MAP.get(http_code, "API_ERROR")

        # Extraemos el mensaje principal de los datos originales
        original_data = response.data
        message = _extract_message(original_data, http_code)

        # Construimos la respuesta normalizada
        normalized = {
            "error": {
                "code": error_code,
                "message": message,
            }
        }

        # Si hay detalles de validación (campo → lista de errores), los incluimos
        if isinstance(original_data, dict) and http_code == 400:
            # Filtramos el campo "detail" que ya está en message
            details = {k: v for k, v in original_data.items() if k != "detail"}
            if details:
                normalized["error"]["details"] = details

        response.data = normalized

    # Manejo adicional para excepciones de Django no capturadas por DRF
    if response is None:
        # ProtectedError -> conflicto por recursos dependientes
        if isinstance(exc, ProtectedError):
            return Response(
                {
                    "error": {
                        "code": HTTP_CODE_MAP.get(409, "CONFLICT"),
                        "message": "No se puede eliminar el recurso porque existen objetos dependientes.",
                    }
                },
                status=status.HTTP_409_CONFLICT,
            )

    return response


def _extract_message(data, http_code: int) -> str:
    """Extrae el mensaje principal de los datos de error de DRF."""
    if isinstance(data, dict):
        if "detail" in data:
            detail = data["detail"]
            # detail puede ser un objeto ErrorDetail o string
            return str(detail)
        # Para errores 400 sin campo "detail", construimos un mensaje genérico
        if http_code == 400:
            return "Los datos proporcionados no son válidos."
    if isinstance(data, list) and data:
        return str(data[0])
    return "Ha ocurrido un error."


# ─── Excepciones de Dominio Personalizadas ─────────────────────────────────────

class RoomAtCapacityError(Exception):
    """Se lanza cuando se intenta asignar un cuarto que ya alcanzó su capacidad."""
    pass


class StudentAlreadyAssignedError(Exception):
    """Se lanza cuando un estudiante ya tiene una asignación activa."""
    pass


class InvalidAssignmentReleaseError(Exception):
    """Se lanza al intentar liberar una asignación que ya fue liberada."""
    pass
