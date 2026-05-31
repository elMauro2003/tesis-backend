# Pruebas de performance con Mercury

Este módulo concentra una sola capa de validación:

1. **django-mercury-performance**: detección de cuellos de botella, exceso de queries y patrones N+1 dentro de pruebas Django.

## 1) Instalación

Instalar las dependencias con UV:

```bash
uv add pytest==8.2.2 pytest-django==4.8.0 pytest-cov==5.0.0 factory-boy==3.3.0 ipython==8.25.0 django-extensions==3.2.3
uv add --group dev django-mercury-performance==0.1.2
```

## 2) Pruebas con Mercury

Ejecutar solo las pruebas de performance:

```bash
uv run pytest tests/performance -m performance
```

### Qué cubre

- autenticación
- catálogos académicos
- infraestructura
- actores
- flujo operativo de quejas, evaluaciones y reportes