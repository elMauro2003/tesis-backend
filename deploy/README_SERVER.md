Ejecutar el servidor con workers async (Gunicorn + Uvicorn)

Recomendado para entornos de staging/producción (Linux):

1) Instalar dependencias

```bash
pip install gunicorn uvicorn
```

2) Ejecutar Gunicorn usando la configuración incluida

```bash
gunicorn -c deploy/gunicorn_conf.py config.asgi:application
```

Opciones útiles:
- Ajustar `workers` en `deploy/gunicorn_conf.py` según CPUs.
- Para logs en ficheros, cambiar `accesslog`/`errorlog` en la configuración.

Desarrollo local (Windows / rápido):

```powershell
# Usar Uvicorn directo y elegir workers (Windows usa multiprocessing spawn)
python -m pip install uvicorn
uvicorn config.asgi:application --host 0.0.0.0 --port 8000 --reload --workers 2
```

Notas:
- `config.asgi:application` es el entrypoint ASGI creado en `config/asgi.py`.
- En contenedores/Docker, ejecutar Gunicorn es la opción habitual.
- Si tu despliegue requiere alta concurrencia consider usar un cache/reverse proxy (nginx) y cache distribuido (Redis).
