"""Pruebas de performance con django-mercury-performance.

Estas pruebas se ejecutan sobre el test client de Django y sirven para detectar
regresiones de tiempo de respuesta, exceso de queries y patrones N+1 en los
flujos más representativos del sistema.
"""

from __future__ import annotations

import pytest

pytest.importorskip("django_mercury")

from django_mercury import monitor


API_PREFIX = "/api/v1"


@pytest.mark.django_db
@pytest.mark.performance
class TestMercuryPerformance:
    def test_authentication_flow(self, client_no_auth, user_estudiante, client_estudiante):
        with monitor(response_time_ms=700, query_count=15):
            login = client_no_auth.post(
                f"{API_PREFIX}/auth/login/",
                {
                    "username": user_estudiante.username,
                    "password": "EstPass123!",
                },
                format="json",
            )

        assert login.status_code == 200
        assert "access" in login.json()

        with monitor(response_time_ms=400, query_count=10):
            me = client_estudiante.get(f"{API_PREFIX}/auth/me/")

        assert me.status_code == 200

    def test_academic_catalogs(self, client_directivo, faculty, career, career_year, group):
        with monitor(response_time_ms=500, query_count=25):
            facultades = client_directivo.get(f"{API_PREFIX}/facultades/")
            carreras = client_directivo.get(f"{API_PREFIX}/carreras/")
            anios = client_directivo.get(f"{API_PREFIX}/anios-academicos/")
            grupos = client_directivo.get(f"{API_PREFIX}/grupos/")

        assert facultades.status_code == 200
        assert carreras.status_code == 200
        assert anios.status_code == 200
        assert grupos.status_code == 200

    def test_infrastructure_catalogs(self, client_directivo, site, building, wing, room):
        with monitor(response_time_ms=500, query_count=30):
            sedes = client_directivo.get(f"{API_PREFIX}/sedes/")
            edificios = client_directivo.get(f"{API_PREFIX}/edificios/")
            alas = client_directivo.get(f"{API_PREFIX}/alas/")
            cuartos = client_directivo.get(f"{API_PREFIX}/cuartos/")
            cuarto_detalle = client_directivo.get(f"{API_PREFIX}/cuartos/{room.id}/")
            cuartos_activas = client_directivo.get(f"{API_PREFIX}/cuartos/?is_active=true")

        assert sedes.status_code == 200
        assert edificios.status_code == 200
        assert alas.status_code == 200
        assert cuartos.status_code == 200
        assert cuarto_detalle.status_code == 200
        assert cuartos_activas.status_code == 200

    def test_actor_catalogs(self, client_instructor, client_directivo, student, professor):
        with monitor(response_time_ms=500, query_count=30):
            estudiantes = client_instructor.get(f"{API_PREFIX}/estudiantes/")
            estudiante_detalle = client_instructor.get(f"{API_PREFIX}/estudiantes/{student.id}/")
            profesores = client_directivo.get(f"{API_PREFIX}/profesores/")

        assert estudiantes.status_code == 200
        assert estudiante_detalle.status_code == 200
        assert profesores.status_code == 200

    def test_operations_flow(self, client_estudiante, client_subdirector, client_directivo, student, building):
        with monitor(response_time_ms=600, query_count=15):
            evaluaciones = client_estudiante.get(f"{API_PREFIX}/evaluaciones/mis-evaluaciones/")
            quejas_visibles = client_estudiante.get(f"{API_PREFIX}/quejas/visibles/")

        assert evaluaciones.status_code == 200
        assert quejas_visibles.status_code == 200

        complaint_payload = {
            "building": building.id,
            "description": "Validación de performance: queja de prueba para monitoreo.",
            "type": "educativa",
        }

        with monitor(response_time_ms=700, query_count=15):
            creada = client_estudiante.post(
                f"{API_PREFIX}/quejas/",
                complaint_payload,
                format="json",
            )

        assert creada.status_code == 201
        complaint_id = creada.json()["id"]

        with monitor(response_time_ms=500, query_count=12):
            listado = client_subdirector.get(f"{API_PREFIX}/quejas/")

        assert listado.status_code == 200

        with monitor(response_time_ms=700, query_count=15):
            cambio = client_subdirector.patch(
                f"{API_PREFIX}/quejas/{complaint_id}/estado/",
                {"status": "en_proceso"},
                format="json",
            )

        assert cambio.status_code in (200, 204)

        with monitor(response_time_ms=700, query_count=15):
            reporte = client_directivo.post(
                f"{API_PREFIX}/reportes/",
                {
                    "name": "Reporte de performance",
                    "type": "ocupancia",
                    "parameters": {"source": "mercury"},
                },
                format="json",
            )

        assert reporte.status_code in (200, 201)