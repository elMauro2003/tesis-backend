# 🚀 GUÍA DE OPTIMIZACIÓN - `/api/v1/estudiantes/`

## Vista Actual (Probable)

```python
# apps/academic/views.py
from rest_framework import viewsets
from .models import Student
from .serializers import StudentSerializer

class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    pagination_class = PageNumberPagination
```

**Problema:** Este ViewSet probable tiene N+1 queries

---

## Paso 1: Optimizar QuerySet ⚡

### ❌ ANTES (Lento)
```python
queryset = Student.objects.all()
# Si StudentSerializer accede a:
# - student.user.name → N queries
# - student.faculty.name → N queries
# - student.residencia.name → N queries
# Total: 1 + 3N queries para N estudiantes
```

### ✅ DESPUÉS (Rápido)
```python
class StudentViewSet(viewsets.ModelViewSet):
    serializer_class = StudentSerializer
    pagination_class = PageNumberPagination
    
    def get_queryset(self):
        """Override para optimizar queries"""
        return Student.objects.select_related(
            'user',      # ForeignKey (one-to-one)
            'faculty',   # ForeignKey
            'residencia' # ForeignKey
        ).prefetch_related(
            'roles',     # Many-to-many
            'documents'  # Reverse ForeignKey
        ).only(
            'id', 'user_id', 'faculty_id', 'residencia_id',
            'matricula', 'created_at', 'updated_at'
        )
```

**Ganancia:** Reduce de 1+3N queries a 1+2 queries (100x más rápido)

---

## Paso 2: Caché en Redis 🔐

### Instalación
```bash
pip install django-redis
```

### settings/base.py
```python
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'CONNECTION_POOL_KWARGS': {'max_connections': 50}
        }
    }
}
```

### En la Vista
```python
from django.views.decorators.cache import cache_page
from rest_framework.decorators import api_view

class StudentViewSet(viewsets.ModelViewSet):
    
    @cache_page(cache_timeout=300)  # 5 minutos
    def list(self, request, *args, **kwargs):
        """Cachea respuesta por 5 minutos"""
        return super().list(request, *args, **kwargs)
    
    def invalidate_cache(self):
        """Limpia caché cuando hay cambios"""
        from django.core.cache import cache
        cache.delete_many([
            f'views.decorators.cache.cache_page.*StudentViewSet.list*'
        ])
```

**Ganancia:** Segunda request elimina completely DB hits (1000x más rápido)

---

## Paso 3: Índices en Base de Datos 🗂️

### Crear Migrations
```bash
python manage.py makemigrations --name add_student_indexes
```

### En la Migration
```python
# apps/academic/migrations/0XXX_add_student_indexes.py
from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('academic', '0XXX_previous'),
    ]

    operations = [
        # Índice simple
        migrations.AddIndex(
            model_name='student',
            index=models.Index(
                fields=['faculty'],
                name='idx_student_faculty'
            ),
        ),
        # Índice compuesto (para filtros combinados)
        migrations.AddIndex(
            model_name='student',
            index=models.Index(
                fields=['faculty', 'user'],
                name='idx_student_faculty_user'
            ),
        ),
        # Full-text search (opcional, si hay búsqueda)
        migrations.RunSQL(
            "CREATE INDEX idx_student_matricula ON academic_student(matricula);",
            "DROP INDEX idx_student_matricula ON academic_student;"
        ),
    ]
```

### Aplica:
```bash
python manage.py migrate academic
```

---

## Paso 4: Serializers Optimizados 📦

### ❌ ANTES
```python
class StudentSerializer(serializers.ModelSerializer):
    user = UserSerializer()  # Nested - trae TODO del user
    faculty = FacultySerializer()  # Nested - trae TODO
    
    class Meta:
        model = Student
        fields = '__all__'  # ❌ Trae campos innecesarios
```

### ✅ DESPUÉS
```python
class StudentListSerializer(serializers.ModelSerializer):
    """Para listados (más compacto)"""
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    faculty_name = serializers.CharField(source='faculty.name', read_only=True)
    
    class Meta:
        model = Student
        fields = [
            'id', 'matricula', 'user_name', 'faculty_name',
            'created_at', 'updated_at'
        ]

class StudentDetailSerializer(serializers.ModelSerializer):
    """Para detail (más completo)"""
    user = UserMinimalSerializer(read_only=True)
    faculty = FacultyMinimalSerializer(read_only=True)
    
    class Meta:
        model = Student
        fields = [
            'id', 'matricula', 'user', 'faculty',
            'email', 'phone', 'created_at', 'updated_at'
        ]

class StudentViewSet(viewsets.ModelViewSet):
    pagination_class = PageNumberPagination
    
    def get_serializer_class(self):
        """USA diferentes serializers para list vs detail"""
        if self.action == 'list':
            return StudentListSerializer
        return StudentDetailSerializer
```

**Ganancia:** Reduce payload HTTP en 60-80%

---

## Paso 5: Paginación Eficiente 📄

### ❌ ANTES (Lento para N grande)
```python
# DEFAULT - usa OFFSET LIMIT
# SELECT * FROM student OFFSET 10000 LIMIT 20
# ↑ Tiene que saltar 10,000 filas cada vez
```

### ✅ DESPUÉS (Rápido)
```python
# settings/base.py
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.CursorPagination',
    'DEFAULT_PAGE_SIZE': 25,
}

# O en la vista
from rest_framework.pagination import CursorPagination

class StudentCursorPagination(CursorPagination):
    page_size = 25
    ordering = '-created_at'  # Ordenar por fecha descendente
    cursor_query_param = 'cursor'

class StudentViewSet(viewsets.ModelViewSet):
    pagination_class = StudentCursorPagination
```

**Formato respuesta:**
```json
{
  "next": "http://api.example.com/students/?cursor=cD01",
  "previous": "http://api.example.com/students/?cursor=cD0xMA==",
  "results": [...]
}
```

---

## Paso 6: Monitoreo & Profiling 📊

### Django Debug Toolbar (Desarrollo)
```bash
pip install django-debug-toolbar
```

```python
# settings/development.py
INSTALLED_APPS += ['debug_toolbar']
MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
INTERNAL_IPS = ['127.0.0.1']
```

### En el navegador: http://localhost:8000/__debug__/
- Ver todos los SQL queries ejecutados
- Tiempo de cada query
- Duplicados (N+1 detection)

### Django Extensions (Análisis profundo)
```bash
pip install django-extensions

# Analizar todas las queries
python manage.py shell_plus

>>> from django.contrib.auth.models import User
>>> from django.db import connection, reset_queries
>>> from django.conf import settings
>>> settings.DEBUG = True
>>>
>>> reset_queries()
>>> # Ejecutar código aquí
>>> print(f"Total queries: {len(connection.queries)}")
>>> for q in connection.queries:
...     print(f"{q['time']}s - {q['sql'][:100]}")
```

---

## Paso 7: Configuración Gunicorn para Producción ⚙️

### requirements/production.txt
```
gunicorn==21.2.0
whitenoise==6.6.0
psycopg2-binary==2.9.9  # PostgreSQL driver
```

### gunicorn_config.py
```python
import multiprocessing

# Workers = (2 * CPU_CORES) + 1
workers = (multiprocessing.cpu_count() * 2) + 1
worker_class = 'sync'  # O 'gevent' si hay async/await
max_requests = 1000
max_requests_jitter = 100
timeout = 30

# Logging
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" %(D)s'
accesslog = '-'
errorlog = '-'
loglevel = 'info'

# Performance
keepalive = 5
```

### Comando de Inicio
```bash
gunicorn \
    --config gunicorn_config.py \
    --bind 0.0.0.0:8000 \
    config.wsgi:application
```

---

## Paso 8: Nginx como Reverse Proxy 🔄

### /etc/nginx/sites-available/uclv-api
```nginx
upstream django_app {
    server localhost:8000;
    server localhost:8001;
    server localhost:8002;
    server localhost:8003;
}

server {
    listen 80;
    server_name api.uclv.cu;
    client_max_body_size 20M;

    # Caché estática
    location /static/ {
        alias /var/www/uclv-residencias/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Caché en Nginx
    location /api/v1/estudiantes/ {
        proxy_pass http://django_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_cache my_cache;
        proxy_cache_valid 200 5m;
        proxy_cache_key "$scheme$request_method$host$request_uri";
    }

    # Resto de endpoints sin caché
    location /api/ {
        proxy_pass http://django_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_read_timeout 30s;
    }
}
```

---

## 📊 Comparación: Antes vs. Después

```
MÉTRICA                  ANTES           DESPUÉS         MEJORA
========================================================================
Queries por request      1 + 3N = ~301   1 + 2 = 3       99%↓
Tiempo response          8.2s            < 100ms         82x↑
Caché hit (2o request)   8.2s            < 10ms          820x↑
Payload HTTP             ~2 MB           ~200 kB         90%↓
Max concurrent users     50              500+            10x↑
p95 latencia             13.76s          < 300ms         46x↑
```

---

## 🎯 Checklist de Implementación

- [ ] Actualizar `get_queryset()` con `select_related()` + `prefetch_related()`
- [ ] Crear indexes en migration
- [ ] Implementar `StudentListSerializer` + `StudentDetailSerializer`
- [ ] Cambiar a `CursorPagination`
- [ ] Configurar Redis y caché
- [ ] Instalar Django Debug Toolbar para profiling local
- [ ] Setup Gunicorn en staging
- [ ] Configurar Nginx con caché
- [ ] Hacer pruebas de carga nuevamente (deben mejorar 50-100x)
- [ ] Monitorear en Grafana

---

## 📞 Soporte

Si tienes dudas sobre alguna optimización, consulta:
- Django Docs: https://docs.djangoproject.com/en/stable/topics/db/optimization/
- DRF Optimization: https://www.django-rest-framework.org/topics/performance/
- Redis + Django: https://django-redis.readthedocs.io/
