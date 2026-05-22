#!/bin/bash
# docker-entrypoint.sh
#
# Se ejecuta cada vez que el contenedor arranca.
# Espera a que PostgreSQL esté listo antes de lanzar Django.

set -e

echo "⏳ Esperando a PostgreSQL en ${DB_HOST}:${DB_PORT}..."

# Espera activa hasta que el puerto de PG responda
until python -c "
import socket, sys
try:
    s = socket.create_connection(('${DB_HOST}', ${DB_PORT}), timeout=2)
    s.close()
    sys.exit(0)
except Exception:
    sys.exit(1)
" 2>/dev/null; do
  echo "   PostgreSQL no disponible aún, reintentando en 2s..."
  sleep 2
done

echo "✅ PostgreSQL disponible."

echo "🔄 Aplicando migraciones..."
python manage.py migrate --noinput

echo "📦 Recolectando archivos estáticos..."
python manage.py collectstatic --noinput --clear

echo "🚀 Iniciando servidor..."
exec "$@"
