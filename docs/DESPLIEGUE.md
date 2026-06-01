# 📘 Guía Completa de Despliegue

**UCLV Residencias Backend | v1.0 | 2026**

---

## 📚 Tabla de contenidos

1. [Arquitectura](#arquitectura)
2. [Despliegue Local](#despliegue-local)
3. [Despliegue con Docker](#despliegue-con-docker)
4. [Despliegue en Producción](#despliegue-en-producción)
5. [Configuración de BD](#configuración-de-bd)
6. [SSL/HTTPS](#sslhttps)
7. [Monitoreo y Logs](#monitoreo-y-logs)
8. [Troubleshooting](#troubleshooting)

---

## Arquitectura

### Componentes principales

```
┌─────────────┐
│   Cliente   │ (Frontend, Mobile, etc.)
└──────┬──────┘
       │ HTTP/HTTPS
       ▼
┌─────────────────────────┐
│   Nginx (Reverse Proxy) │ (Puerto 80/443)
└──────┬──────────────────┘
       │ HTTP (local)
       ▼
┌─────────────────────────────────────────┐
│  Gunicorn / Uvicorn (ASGI Server)       │
│  ├─ Worker 1 (async)                    │
│  ├─ Worker 2 (async)                    │
│  ├─ Worker 3 (async)                    │
│  └─ Worker 4 (async)                    │
└──────┬──────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────┐
│  Django REST Framework + Apps           │
│  ├─ apiendpoint `/api/v1/`              │
│  ├─ Authentication (JWT)                │
│  ├─ RBAC Permissions                    │
│  └─ Business Logic                      │
└──────┬──────────────────────────────────┘
       │
       ▼
┌─────────────────────────┐
│  PostgreSQL Database    │ (Puerto 5432)
│  (o SQLite para dev)    │
└─────────────────────────┘
```

### Stack ASGI

- **Servidor ASGI:** Uvicorn + Gunicorn (UvicornWorker)
- **Número de workers:** 4 recomendado (desarrollable según CPU)
- **Fórmula workers:** `(2 × número_de_CPUs) + 1`
- **Concurrencia:** Hasta 100+ usuarios simultáneos con setup adecuado

---

## Despliegue Local

### Paso 1: Clonar y configurar

```bash
# Clonar repositorio
git clone https://github.com/yourusername/uclv_residencias.git
cd uclv_residencias

# Crear entorno virtual con UV
uv sync

# Copiar template de variables de entorno
cp .env.example .env
```

### Paso 2: Configurar variables de entorno (`.env`)

```bash
# Django
DEBUG=True
SECRET_KEY=tu-clave-secreta-aqui-cambiar-en-produccion
ALLOWED_HOSTS=localhost,127.0.0.1

# Base de datos (SQLite para dev, PostgreSQL recomendado)
DATABASE_URL=sqlite:///./db_dev.sqlite3
# O para PostgreSQL:
# DATABASE_URL=postgresql://user:password@localhost:5432/uclv_residencias

# JWT
SIMPLE_JWT_ACCESS_TOKEN_LIFETIME=300
SIMPLE_JWT_REFRESH_TOKEN_LIFETIME=86400

# Email (para recuperación de contraseña, etc.)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=tu-email@gmail.com
EMAIL_HOST_PASSWORD=tu-app-password

# Logging
LOG_LEVEL=INFO
```

### Paso 3: Migraciones y setup

```bash
# Aplicar migraciones
python manage.py migrate

# Crear usuario superadmin (si lo deseas)
python manage.py createsuperuser

# (Opcional) Cargar datos de prueba
python manage.py seed_database

# Recolectar archivos estáticos
python manage.py collectstatic --noinput
```

### Paso 4: Ejecutar servidor local (Uvicorn)

```bash
# Opción 1: Uvicorn simple (desarrollo rápido)
uv run uvicorn config.asgi:application \
    --host 0.0.0.0 \
    --port 8000 \
    --reload

# Opción 2: Uvicorn con 4 workers (simular producción)
uv run uvicorn config.asgi:application \
    --host 0.0.0.0 \
    --port 8000 \
    --workers 4

# Opción 3: Gunicorn + UvicornWorker (recomendado para pruebas realistas)
gunicorn config.asgi:application \
    --worker-class uvicorn.workers.UvicornWorker \
    --workers 4 \
    --bind 0.0.0.0:8000 \
    --access-logfile - \
    --error-logfile - \
    --log-level info
```

### Paso 5: Verificar

```bash
# Salud de la API
curl http://localhost:8000/api/v1/health/

# Documentación interactiva
# Abre en navegador: http://localhost:8000/api/v1/docs/

# Listar endpoints
curl http://localhost:8000/api/v1/
```

---

## Despliegue con Docker

### Requisitos

- Docker 20.10+
- Docker Compose 2.0+

### Ejecución

```bash
# Build y lanzar
docker-compose up -d

# Verificar status
docker-compose ps

# Ver logs en tiempo real
docker-compose logs -f backend

# Entrar en el contenedor (debugging)
docker-compose exec backend bash

# Parar servicios
docker-compose down

# Limpiar todo (incluyendo volúmenes)
docker-compose down -v
```

### Configuración Docker Compose

El archivo `docker-compose.yml` incluye:
- **Backend:** Gunicorn + UvicornWorker (4 workers)
- **Base de datos:** PostgreSQL 15
- **Volúmenes:** Para persistencia
- **Networking:** Red interna

Ajusta los puertos, credenciales y variables de entorno según sea necesario.

---

## Despliegue en Producción

### Configuración recomendada

```
┌──────────────────────────────────────────┐
│         Internet                         │
└──────────────────┬───────────────────────┘
                   │ HTTPS (443)
                   ▼
         ┌─────────────────────┐
         │  Nginx (Reverse     │
         │  Proxy + SSL/TLS)   │
         │  Puertos 80/443     │
         └──────────┬──────────┘
                    │ HTTP (interno)
                    ▼
    ┌────────────────────────────────┐
    │  Gunicorn (ASGI server)        │
    │  8 workers (prod) / 4 (test)   │
    │  Supervisor o Systemd          │
    │  Puerto 8000 (interno)         │
    └──────────┬─────────────────────┘
               │
               ▼
         ┌──────────────────┐
         │  PostgreSQL 15   │
         │  Backups diarios │
         │  Puerto 5432     │
         └──────────────────┘
```

### Paso 1: Preparar servidor

```bash
# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar dependencias
sudo apt install -y python3.12 python3.12-venv postgresql postgresql-contrib \
    nginx supervisor git uv certbot python3-certbot-nginx

# Crear usuario para aplicación
sudo useradd -m -s /bin/bash uclvapp

# Cambiar a usuario
sudo su - uclvapp
```

### Paso 2: Clonar aplicación

```bash
# Como user 'uclvapp'
cd /home/uclvapp
git clone https://github.com/yourusername/uclv_residencias.git
cd uclv_residencias

# Instalar dependencias
uv sync

# Copiar .env y configurar
cp .env.example .env
# Editar .env con valores de producción
nano .env
```

**Variables críticas para producción:**

```bash
DEBUG=False
SECRET_KEY=<generar-con-openssl-rand-hex>
ALLOWED_HOSTS=tudominio.com,www.tudominio.com
DATABASE_URL=postgresql://user:password@localhost:5432/uclv_residencias
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

### Paso 3: Configurar PostgreSQL

```bash
# Acceder como root
sudo -i

# Conectar a PostgreSQL
sudo -u postgres psql

# Crear base de datos y usuario
CREATE DATABASE uclv_residencias;
CREATE USER uclvapp WITH PASSWORD 'secure-password-here';
ALTER ROLE uclvapp SET client_encoding TO 'utf8';
ALTER ROLE uclvapp SET default_transaction_isolation TO 'read committed';
ALTER ROLE uclvapp SET default_transaction_deferrable TO on;
ALTER ROLE uclvapp SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE uclv_residencias TO uclvapp;
\q

# Salir de root
exit
```

### Paso 4: Migraciones y setup

```bash
# Como user 'uclvapp'
cd /home/uclvapp/uclv_residencias

# Migraciones
python manage.py migrate --settings=config.settings.prod

# Create superuser
python manage.py createsuperuser --settings=config.settings.prod

# Recolectar estáticos
python manage.py collectstatic --noinput --settings=config.settings.prod
```

### Paso 5: Configurar Gunicorn con Supervisor

Crear archivo `/home/uclvapp/uclv_residencias/gunicorn_prod.conf`:

```python
# gunicorn_prod.conf
import multiprocessing

bind = "127.0.0.1:8000"
workers = (multiprocessing.cpu_count() * 2) + 1
worker_class = "uvicorn.workers.UvicornWorker"
worker_tmp_dir = "/dev/shm"
max_requests = 1000
max_requests_jitter = 50
timeout = 60
keepalive = 5
access_log = "/home/uclvapp/uclv_residencias/logs/access.log"
error_log = "/home/uclvapp/uclv_residencias/logs/error.log"
log_level = "info"
```

Crear archivo supervisor: `sudo nano /etc/supervisor/conf.d/uclv.conf`

```ini
[program:uclv_backend]
directory=/home/uclvapp/uclv_residencias
command=/home/uclvapp/.local/bin/gunicorn \
    config.asgi:application \
    --config gunicorn_prod.conf \
    --env DJANGO_SETTINGS_MODULE=config.settings.prod
user=uclvapp
autostart=true
autorestart=true
startsecs=10
stdout_logfile=/home/uclvapp/uclv_residencias/logs/gunicorn_stdout.log
stdout_logfile_maxbytes=1MB
stdout_logfile_backups=10
stderr_logfile=/home/uclvapp/uclv_residencias/logs/gunicorn_stderr.log
```

### Paso 6: Configurar Nginx

Crear archivo `sudo nano /etc/nginx/sites-available/uclv_residencias`:

```nginx
upstream uclv_backend {
    server 127.0.0.1:8000;
}

# Redireccionamiento HTTP → HTTPS
server {
    listen 80;
    server_name tudominio.com www.tudominio.com;
    return 301 https://$server_name$request_uri;
}

# HTTPS (después de obtener certificado SSL)
server {
    listen 443 ssl http2;
    server_name tudominio.com www.tudominio.com;

    # SSL Certificates (Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/tudominio.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/tudominio.com/privkey.pem;

    # SSL Config (Mozilla)
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    ssl_session_tickets off;

    # HSTS
    add_header Strict-Transport-Security "max-age=63072000; includeSubDomains" always;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;

    # Proxy
    location / {
        proxy_pass http://uclv_backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
    }

    # Static files
    location /static/ {
        alias /home/uclvapp/uclv_residencias/staticfiles/;
        expires 365d;
    }

    # Media files
    location /media/ {
        alias /home/uclvapp/uclv_residencias/media/;
        expires 7d;
    }

    # Deny access to sensitive files
    location ~ /\. {
        deny all;
        access_log off;
        log_not_found off;
    }
}
```

Habilitar sitio:

```bash
sudo ln -s /etc/nginx/sites-available/uclv_residencias \
    /etc/nginx/sites-enabled/uclv_residencias

# Remover default si existe
sudo rm /etc/nginx/sites-enabled/default

# Test config
sudo nginx -t

# Reiniciar
sudo systemctl restart nginx
```

### Paso 7: Obtener certificado SSL

```bash
# Certbot automático con Nginx
sudo certbot certonly --nginx -d tudominio.com -d www.tudominio.com

# Renovación automática (crontab)
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer
```

### Paso 8: Iniciar servicios

```bash
# Actualizar supervisor
sudo supervisorctl reread
sudo supervisorctl update

# Iniciar aplicación
sudo supervisorctl start uclv_backend

# Ver status
sudo supervisorctl status
```

### Paso 9: Backups

Crear script `backup.sh` en `/home/uclvapp/`:

```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/home/uclvapp/backups"
mkdir -p $BACKUP_DIR

# Backup BD
sudo -u postgres pg_dump uclv_residencias | gzip > \
    $BACKUP_DIR/db_$DATE.sql.gz

# Backup archivos importantes
tar czf $BACKUP_DIR/app_$DATE.tar.gz \
    /home/uclvapp/uclv_residencias/media \
    /home/uclvapp/uclv_residencias/.env

# Limpiar backups antiguos (>30 días)
find $BACKUP_DIR -name "*.gz" -mtime +30 -delete

echo "Backup completado: $DATE"
```

Añadir a crontab (cada día a las 2 AM):

```bash
crontab -e
# 0 2 * * * /home/uclvapp/backup.sh
```

---

## Configuración de BD

### PostgreSQL (Producción)

#### Creación

```bash
# Como postgres user
sudo -u postgres psql

CREATE DATABASE uclv_residencias
    WITH
    ENCODING 'UTF8'
    LC_COLLATE 'es_ES.UTF-8'
    LC_CTYPE 'es_ES.UTF-8'
    TEMPLATE template0;

CREATE USER uclvapp WITH PASSWORD 'secure-password';
GRANT ALL PRIVILEGES ON DATABASE uclv_residencias TO uclvapp;
```

#### Optimizaciones recomendadas

Editar `/etc/postgresql/15/main/postgresql.conf`:

```ini
# Conexiones
max_connections = 200

# Memoria
shared_buffers = 256MB  # 25% de RAM
effective_cache_size = 1GB  # 50-75% de RAM
work_mem = 16MB  # shared_buffers / max_connections

# Vacuum
autovacuum = on
autovacuum_naptime = 10s

# Logging
logging_collector = on
log_directory = '/var/log/postgresql'
log_filename = 'postgresql-%Y-%m-%d.log'
log_min_duration_statement = 1000  # Log queries > 1s
```

Reiniciar después:

```bash
sudo systemctl restart postgresql
```

### SQLite (Desarrollo)

```bash
# Crear BD de desarrollo
python manage.py migrate

# Backup SQLite
cp db_dev.sqlite3 db_dev.sqlite3.bak

# Inspeccionar datos (con tool)
sqlite3 db_dev.sqlite3
sqlite> .schema
sqlite> SELECT * FROM actors_student LIMIT 5;
sqlite> .quit
```

---

## SSL/HTTPS

### Obtener certificado (Let's Encrypt)

```bash
# Instalación única
sudo apt install certbot python3-certbot-nginx

# Obtener certificado (Nginx)
sudo certbot certonly --nginx -d tudominio.com -d www.tudominio.com

# O obtener directamente (sin Nginx)
sudo certbot certonly --standalone -d tudominio.com

# Ruta de certificados
/etc/letsencrypt/live/tudominio.com/
├── cert.pem
├── chain.pem
├── fullchain.pem
└── privkey.pem
```

### Renovación automática

```bash
# Verificar timer
sudo systemctl status certbot.timer

# Renovación manual
sudo certbot renew --dry-run  # Test
sudo certbot renew            # Real
```

### Forzar HTTPS en Django

Asegurar en `config/settings/prod.py`:

```python
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000  # 1 año
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
```

---

## Monitoreo y Logs

### Ver logs en tiempo real

```bash
# Gunicorn access logs
tail -f /home/uclvapp/uclv_residencias/logs/access.log

# Gunicorn error logs
tail -f /home/uclvapp/uclv_residencias/logs/error.log

# Django logs (si está configurado)
tail -f /var/log/django.log

# Supervisor
sudo tail -f /var/log/supervisor/supervisord.log

# Nginx
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### Health checks

```bash
# Ver estado de aplicación
curl https://tudominio.com/api/v1/health/

# Ver status de workers Gunicorn
# (si está expuesto en admin)
curl https://tudominio.com/admin/
```

### Alertas recomendadas

- Cpu > 80%
- Memoria > 90%
- Espacio disco < 10%
- Tiempo respuesta P95 > 5s
- Tasa de errores > 0.1%

Usar herramientas como:
- **Prometheus + Grafana**
- **New Relic**
- **DataDog**
- **Sentry** (error tracking)

---

## Troubleshooting

### Problema: Error 502 Bad Gateway (Nginx)

**Causa típica:** Gunicorn no está corriendo o no escucha en puerto 8000

```bash
# Verificar si está corriendo
sudo supervisorctl status uclv_backend

# Reiniciar
sudo supervisorctl restart uclv_backend

# Ver logs
sudo supervisorctl tail uclv_backend
```

### Problema: Base de datos no conecta

```bash
# Verificar DATABASE_URL en .env
grep DATABASE_URL /home/uclvapp/uclv_residencias/.env

# Verificar credenciales PostgreSQL
sudo -u postgres psql -l

# Verificar conexión
python manage.py dbshell --settings=config.settings.prod
```

### Problema: SSL certificado vencido

```bash
# Verificar fecha
sudo openssl x509 -enddate -noout -in /etc/letsencrypt/live/tudominio.com/cert.pem

# Renovar inmediato
sudo certbot renew --force-renewal

# Reiniciar Nginx
sudo systemctl restart nginx
```

### Problema: Archivos estáticos no se sirven (404)

```bash
# Recolectar estáticos nuevamente
python manage.py collectstatic --noinput --clear --settings=config.settings.prod

# Verificar permisos
ls -la /home/uclvapp/uclv_residencias/staticfiles/
sudo chown -R uclvapp:uclvapp /home/uclvapp/uclv_residencias/staticfiles/

# Reiniciar Nginx
sudo systemctl restart nginx
```

### Problema: Memoria se agota

```bash
# Ver procesos Gunicorn
ps aux | grep gunicorn

# Ver memoria por proceso
ps aux --sort=-%mem

# Reducir workers o aumentar disponible
# Editar gunicorn_prod.conf y reiniciar:
sudo supervisorctl restart uclv_backend
```

---

## 📞 Soporte

- **Documentación:** [docs/INDEX.md](INDEX.md)
- **Performance:** [performance/k6/REPORTE_RENDIMIENTO.md](../../performance/k6/REPORTE_RENDIMIENTO.md)
- **API Docs:** `https://tudominio.com/api/v1/docs/`

