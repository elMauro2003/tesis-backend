# ─── Imagen base ───────────────────────────────────────────────────────────────
# Python 3.12 slim para imagen más pequeña en producción
FROM python:3.12-slim

# ─── Variables de entorno del contenedor ───────────────────────────────────────
ENV PYTHONDONTWRITEBYTECODE=1   \
    PYTHONUNBUFFERED=1          \
    PIP_NO_CACHE_DIR=1          \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# ─── Directorio de trabajo ─────────────────────────────────────────────────────
WORKDIR /app

# ─── Dependencias del sistema ──────────────────────────────────────────────────
# libpq5: cliente PostgreSQL en tiempo de ejecución
# gcc/libpq-dev: necesarios si alguna dependencia compila extensiones
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# ─── Dependencias Python ───────────────────────────────────────────────────────
# Copiamos solo requirements primero para aprovechar el cache de Docker
COPY requirements/ requirements/
RUN pip install --no-cache-dir -r requirements/prod.txt

# ─── Código fuente ─────────────────────────────────────────────────────────────
COPY . .

# ─── Script de entrada ─────────────────────────────────────────────────────────
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["gunicorn", "-c", "deploy/gunicorn_conf.py", "config.asgi:application"]
