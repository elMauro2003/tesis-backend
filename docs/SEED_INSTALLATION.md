# 🌱 Seeding de Base de Datos

**Guía para cargar datos realistas de prueba en la BD actual. Con este script, tienes un sistema completo funcionando con datos de simulación.**

---

## Tabla de Contenidos

1. [Qué Carga el Seed](#qué-carga-el-seed)
2. [Instalación y Uso](#instalación-y-uso)
3. [Datos de Login](#datos-de-login)
4. [Verificación](#verificación)
5. [Casos de Uso Incluidos](#casos-de-uso-incluidos)

---

## Qué Carga el Seed

El script `seed_database` puebla la BD con datos realistas que simulan un semestre académico completo (Septiembre 2025 — Julio 2026, estándar cubano).

### Cantidad de Datos

```
🏢 INFRAESTRUCTURA
├─ 3 Sedes (Central, Pedagógico, Fajardo)
├─ 8 Edificios
├─ 24 Alas
└─ 120 Cuartos (capacidad 4 c/u, 480 spots totales)

🎓 ACADÉMICO
├─ 2 Facultades (Matemática/Física/Computación, Ingeniería)
├─ 3 Carreras (ICI, Ingeniería Eléctrica, Ingeniería Civil)
├─ 5 Años Académicos (1º a 5º año)
└─ 15 Grupos de Estudiantes
   └─ ~10 estudiantes/grupo

👥 PERSONAS
├─ 9 Profesores (con roles asignados)
│  ├─ 1 Decano
│  ├─ 3 Responsables de Ala (PPA)
│  ├─ 3 Profesores Guía (PG)
│  └─ 2 Sin rol adicional
└─ 60 Estudiantes
   ├─ Distribuidos en 15 grupos
   ├─ Todos con asignaciones activas
   └─ Datos médicos y personales generados

📋 OPERACIONES
├─ 30 Evaluaciones (distribuidas por semanas del semestre)
├─ 20 Quejas (en estados: pendiente, en_proceso, resuelta)
├─ 10 Cuartelerías (completadas y en progreso)
├─ 60 Asignaciones (mixtura de activas e históricas)
├─ 5 Informaciones/Noticias (públicas)
└─ 2 Reportes generados
```

### Cobertura de Workflows

✅ Estudiantes completamente registrados  
✅ Asignaciones de cuartos (algunos con ocupancia incompleta)  
✅ Evaluaciones periódicas  
✅ Quejas en varios estados (muestra flujo completo)  
✅ Cuartelerías (limpieza rotativa)  
✅ Informaciones publicadas  
✅ Reportes de prueba  

---

## Instalación y Uso

### Requisitos Previos

```bash
# 1. Tener entorno virtual activado
python -V  # Debe ser 3.12+

# 2. BD configurada y migrada
python manage.py migrate
# (si pregunta qué configuración: con config/settings/test.py o dev.py)

# 3. Roles creados
python manage.py create_roles
# Crea los 9 roles: estudiante, instructor, directivo, subdirector, comunicador, etc
```

### Ejecutar Seed

```bash
# Comando simple
python manage.py seed_database

# Output esperado:
# ✓ Creando sedes...
# ✓ Creando edificios...
# ... (progreso de cada sección)
# ✓ Seed database completado exitosamente!
# Total: 3 sedes, 8 edificios, 24 alas, 120 cuartos,
#        2 facultades, 3 carreras, 5 años académicos,
#        15 grupos de estudiantes, 9 profesores, 60 estudiantes
```

### Limpiar BD y Rehacer Seed

```bash
# Opción 1: Flush completo (peligroso - elimina TODO)
python manage.py flush
# Response: "This will delete all data in the database..."
# Teclea "yes" para confirmar

# Luego repoblar
python manage.py seed_database

# Opción 2: Usar transacciones (más seguro - futuro)
# (el seed puede hacerse idempotente)
```

---

## Datos de Login

### Usuarios Creados

El script crea usuarios con credenciales predefinidas:

#### 👨‍🎓 Estudiante

```
username: luis_garcia
password: Password123!
email: luis@uclv.cu
roles: estudiante

Descripción: Estudiante de 3er año, grupo C-311, ICI
```

#### 👨‍🏫 Instructor

```
username: carlos_instructor
password: Password123!
email: carlos@uclv.cu
roles: instructor

Descripción: Instructor de beca
```

#### 👔 Directivo

```
username: ana_directivo
password: Password123!
email: ana@uclv.cu
roles: directivo

Descripción: Directora de Becas
```

#### 👨‍⚖️ Subdirector

```
username: juan_subdirector
password: Password123!
email: juan@uclv.cu
roles: subdirector

Descripción: Subdirector Administrativo
```

#### 📢 Comunicador

```
username: maria_comunicador
password: Password123!
email: maria@uclv.cu
roles: comunicador

Descripción: Encargado de Comunicaciones
```

#### 🎓 Profesores (Decano, PPA, PG)

```
username: profesor_decano
password: Password123!
email: prof_decano@uclv.cu
roles: profesor, decano

---

username: profesor_ppa_1
password: Password123!
email: prof_ppa@uclv.cu
roles: profesor, ppa

---

username: profesor_pg_1
password: Password123!
email: prof_pg@uclv.cu
roles: profesor, pg
```

#### 🔧 Admin

```
username: admin
password: admin123
email: admin@uclv.cu
roles: admin

Descripción: Superusuario (también disponible en /admin/)
```

### Ejemplo: Login como Estudiante

```bash
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "luis_garcia",
    "password": "Password123!"
  }'

# Response 200 OK
{
  "refresh": "eyJ0eXA...",
  "access": "eyJ0eXA...",
  "user": {
    "id": 50,
    "username": "luis_garcia",
    "email": "luis@uclv.cu",
    "roles": ["estudiante"]
  }
}
```

---

## Verificación

### Método 1: Admin Django

```bash
# Acceder a admin
http://localhost:8000/admin/

# Login con:
username: admin
password: admin123

# Verificar:
✓ Authentication and Authorization → Users (60+ estudiantes, 10+ profesores)
✓ Academic → Faculties (2), Careers (3), Career Years (5), Groups (15)
✓ Infrastructure → Sites (3), Buildings (8), Wings (24), Rooms (120)
✓ Actors → Students (60), Professors (9)
✓ Operations → Complaints (20), Evaluations (30), Assignments (60)
```

### Método 2: Swagger UI

```bash
# Acceder a Swagger
http://localhost:8000/api/v1/docs/

# Login con credenciales del role que quieras probar
# Pruebar endpoints:
GET /api/v1/estudiantes/        # 60 estudiantes listados
GET /api/v1/cuartos/            # 120 cuartos
GET /api/v1/evaluaciones/       # 30 evaluaciones
GET /api/v1/quejas/mis-quejas/  # Quejas del estudiante actual
```

### Método 3: API Directamente

```bash
# Listar estudiantes
curl -X GET http://localhost:8000/api/v1/estudiantes/?page=1 \
  -H "Authorization: Bearer <access_token>"

# Response (paginated)
{
  "count": 60,
  "next": "http://localhost:8000/api/v1/estudiantes/?page=2",
  "results": [
    {
      "id": 1,
      "student_id": "ICI-2025-001",
      "ci": "00010111234",
      "user": {
        "id": 50,
        "first_name": "Luis",
        "last_name": "García"
      },
      "group": "C-311",
      "is_militant": true
    },
    ...
  ]
}

# Listar cuartos
curl http://localhost:8000/api/v1/cuartos/ \
  -H "Authorization: Bearer <access_token>"

# Response
{
  "count": 120,
  "results": [
    {
      "id": 1,
      "number": "101",
      "wing": "Ala Norte",
      "capacity": 4,
      "current_occupancy": 3,
      "is_full": false,
      "is_active": true
    },
    ...
  ]
}
```

### Método 4: Shell Django

```bash
python manage.py shell

# En el shell:
from apps.actors.models import Student
from apps.infrastructure.models import Room, Assignment

# Cuántos estudiantes
print(f"Total estudiantes: {Student.objects.count()}")
# Output: Total estudiantes: 60

# Ocupancia de cuartos
room = Room.objects.first()
print(f"Cuarto {room.number}: {room.current_occupancy}/{room.capacity}")
# Output: Cuarto 101: 3/4

# Asignaciones activas
active = Assignment.objects.filter(released_date__isnull=True).count()
print(f"Asignaciones activas: {active}")
# Output: Asignaciones activas: 60

# Quejas
from apps.operations.models import Complaint
print(f"Quejas pendientes: {Complaint.objects.filter(status='pendiente').count()}")
# Output: Quejas pendientes: 5
```

---

## Casos de Uso Incluidos

### Caso 1: Estudiante Consulta Sus Datos

```http
GET /api/v1/auth/me/
Authorization: Bearer <luis_garcia_token>

Response 200:
{
  "id": 50,
  "username": "luis_garcia",
  "email": "luis@uclv.cu",
  "roles": ["estudiante"],
  "student_info": {
    "student_id": "ICI-2025-001",
    "group": "C-311",
    "current_room": "101 - Ala Norte",
    "evaluations_avg": "B"
  }
}
```

### Caso 2: Estudiante Ve Sus Evaluaciones

```http
GET /api/v1/evaluaciones/mis-evaluaciones/
Authorization: Bearer <luis_garcia_token>

Response 200:
[
  {
    "id": 1,
    "date": "2025-10-15",
    "grade": "B",
    "comment": "Buen desempeño"
  },
  {
    "id": 2,
    "date": "2025-12-10",
    "grade": "B",
    "comment": "Participación activa"
  },
  ...
]
```

### Caso 3: Estudiante Presenta Queja

```http
POST /api/v1/quejas/
Authorization: Bearer <luis_garcia_token>
Content-Type: application/json

{
  "date": "2025-10-20",
  "building": 1,
  "description": "Fuga de agua en el baño",
  "type": "administrativa"
}

Response 201:
{
  "id": 21,
  "student": "Luis García",
  "description": "Fuga de agua en el baño",
  "status": "pendiente",
  "visibility": false
}
```

### Caso 4: Instructor Crea Evaluación

```http
POST /api/v1/evaluaciones/
Authorization: Bearer <carlos_instructor_token>
Content-Type: application/json

{
  "student": 1,
  "date": "2025-10-25",
  "grade": "R",
  "comment": "Incumplimiento de cuartelería"
}

Response 201:
{
  "id": 31,
  "student": "Luis García",
  "grade": "R",
  "created_by": "carlos_instructor"
}
```

### Caso 5: Subdirector Responde Queja

```http
PATCH /api/v1/quejas/21/estado/
Authorization: Bearer <juan_subdirector_token>

{"status": "en_proceso"}

Response 200:
{
  "id": 21,
  "status": "en_proceso"
}

---

POST /api/v1/quejas/21/respuesta/
Authorization: Bearer <juan_subdirector_token>

{"response": "Orden enviada a mantenimiento. Reparación estimada 3 días."}

Response 200:
{
  "id": 21,
  "status": "resuelta",
  "response": "Orden enviada a mantenimiento...",
  "response_date": "2025-10-26"
}
```

### Caso 6: Comunicador Publica Información

```http
POST /api/v1/informaciones/
Authorization: Bearer <maria_comunicador_token>
Content-Type: application/json

{
  "title": "Suspensión de agua caliente",
  "content": "Por mantenimiento, el agua caliente estará suspendida...",
  "published_date": "2025-10-30",
  "expires_date": "2025-11-02",
  "is_public": true
}

Response 201:
{
  "id": 6,
  "title": "Suspensión de agua caliente",
  "published_date": "2025-10-30"
}
```

### Caso 7: Directivo Genera Reporte

```http
POST /api/v1/reportes/
Authorization: Bearer <ana_directivo_token>
Content-Type: application/json

{
  "name": "Ocupancia por Ala - Octubre 2025",
  "type": "occupancy",
  "parameters": {
    "building_id": 1,
    "month": "2025-10"
  }
}

Response 201:
{
  "id": 1,
  "name": "Ocupancia por Ala - Octubre 2025",
  "generated_date": "2025-10-30T15:45:00Z",
  "file_url": "/media/reports/occupancy_20251030.pdf"
}
```

---

## Flujo Temporal Simulado

El seed distribuye datos a lo largo del semestre (Sep 2025 — Jul 2026):

```
SEPTIEMBRE 2025
├─ Asignación de cuartos (semana 1)
├─ Primeras cuartelerías (semana 2)
└─ Primeras evaluaciones (fin de mes)

OCTUBRE-DICIEMBRE 2025
├─ Evaluaciones normales (cada 4 semanas)
├─ Presentación de quejas (dispersadas)
├─ Cuartelerías activas
└─ Algunas respuestas de quejas

ENERO-JULIO 2026
├─ Evaluaciones continuas
├─ Quejas resueltas and archivadas
├─ Reportes de período
└─ Preparación para fin de semestre
```

---

## Troubleshooting

### Error: "Roles don't exist"

```bash
# Solución: crear roles primero
python manage.py create_roles
python manage.py seed_database
```

### Error: "Migrations haven't been applied"

```bash
# Solución: migrar
python manage.py migrate
python manage.py seed_database
```

### Error: "Database connection failed"

```bash
# Si usas PostgreSQL: verificar que está corriendo
# Si usas SQLite: el archivo se crea automáticamente

# Para usar SQLite (testing)
export DJANGO_SETTINGS_MODULE=config.settings.test
python manage.py migrate
python manage.py seed_database
```

### El seed se ejecutó parcialmente (crash)

```bash
# Opción A: Flush y rehacer
python manage.py flush
python manage.py seed_database

# Opción B: Verificar error específico
python manage.py seed_database --verbosity=3
```

---

## Próximos Pasos

Una vez que el seed esté cargado:

1. **Explorar API:** En Swagger `http://localhost:8000/api/v1/docs/`
2. **Probar Roles:** Login con diferentes usuarios (estudiante, instructor, etc)
3. **Ejecutar Tests:** `pytest -v` (debe pasar 140 tests)
4. **Revisar Documentación:** [docs/SISTEMA_FLUJO_COMPLETO.md](SISTEMA_FLUJO_COMPLETO.md) para usar el sistema

---

**Última actualización:** 21 de mayo de 2026
