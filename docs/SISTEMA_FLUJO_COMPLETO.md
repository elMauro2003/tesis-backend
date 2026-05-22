# Sistema de Gestión de Residencias Estudiantiles — UCLV

## Flujo Operativo Completo del Sistema

> Documento de referencia que describe cómo el sistema maneja el ciclo de vida completo de gestión y control de becas estudiantiles residenciales en la Universidad Central "Marta Abreu" de Las Villas (UCLV).

---

## Tabla de Contenidos

1. [Descripción General del Sistema](#descripción-general-del-sistema)
2. [Actores y Roles](#actores-y-roles)
3. [Caso de Uso Completo: Ciclo de Vida de un Estudiante Becado](#caso-de-uso-completo-ciclo-de-vida-de-un-estudiante-becado)
4. [Estructuras de Datos](#estructuras-de-datos)
5. [Endpoints y Operaciones Disponibles](#endpoints-y-operaciones-disponibles)
6. [Flujo de Autenticación y Autorización](#flujo-de-autenticación-y-autorización)
7. [Procesos Operativos](#procesos-operativos)
8. [Reportes y Auditoría](#reportes-y-auditoría)

---

## Descripción General del Sistema

El **Sistema de Gestión de Residencias Estudiantiles** es una plataforma de control integral que permite:

- **Gestión de Infraestructura**: Administración de sedes, edificios, alas y cuartos (dormitorios)
- **Gestión Humana**: Registro y clasificación de estudiantes, instructores, directivos y profesores
- **Asignación de Alojamiento**: Distribución inteligente de cuartos residenciales a estudiantes con control de ocupancia
- **Evaluación y Seguimiento**: Evaluaciones periódicas del comportamiento y desempeño de estudiantes
- **Gestión de Conflictos**: Sistema de quejas, sugerencias y resolución de problemáticas
- **Comunicaciones**: Publicación de informaciones, noticias y notificaciones
- **Cuartelerías**: Programa rotativo de labores de limpieza compartidas
- **Reportería**: Generación de reportes para análisis administrativo

---

## Actores y Roles

El sistema implementa **Role-Based Access Control (RBAC)** con 9 roles distintos:

| Rol | Descripción | Responsabilidades |
|-----|-------------|-------------------|
| **Administrador (admin)** | Gestor técnico del sistema | Gestión de roles, usuarios, reset de contraseñas, supervisión general |
| **Directivo** | Director de la residencia | CRUD completo: infraestructura, estudiantes, reportes; autoriza cambios mayores |
| **Instructor** | Monitor/instructor de beca | Gestiona estudiantes (CRUD), asignaciones, evaluaciones, limpieza, quejas |
| **Subdirector** | Subdirector administrativo | Gestiona quejas: cambia estado, responde, controla visibilidad |
| **Comunicador** | Encargado de comunicaciones | CRUD de informaciones/noticias para la comunidad |
| **Decano** | Decano de facultad | Consulta estudiantes de su facultad (solo lectura) |
| **PPA** | Profesor Principal de Año | Consulta estudiantes de su año académico (solo lectura) |
| **PG** | Profesor Guía | Consulta estudiantes de su grupo (solo lectura) |
| **Estudiante** | Becado residente | CRUD de sus propias quejas, ve evaluaciones, informaciones públicas |

---

## Caso de Uso Completo: Ciclo de Vida de un Estudiante Becado

### Fase 1: Preparación del Año Académico (Septiembre↑)

#### 1.1 Preparación Estructural

**Actor**: Directivo  
**Descripción**: Se estructura la infraestructura física del año académico

```http
POST /api/v1/sedes/
{
  "name": "Sede Central",
  "address": "Campus Principal, Las Villas"
}
→ 201 Created

POST /api/v1/edificios/
{
  "site": 1,
  "name": "Edificio de Ciencias"
}
→ 201 Created

POST /api/v1/alas/
{
  "building": 1,
  "name": "Ala Norte"
}
→ 201 Created

POST /api/v1/cuartos/
{
  "wing": 1,
  "number": "101",
  "capacity": 4,
  "is_active": true
}
→ 201 Created (se crea cuarto con capacidad máxima de 4 ocupantes)
```

#### 1.2 Estructura Académica

**Actor**: Directivo  
**Descripción**: Se registran facultades, carreras, años académicos y grupos

```http
POST /api/v1/facultades/
{
  "name": "Facultad de Matemática, Física y Computación",
  "code": "MATFISCOM"
}
→ 201 Created

POST /api/v1/carreras/
{
  "faculty": 1,
  "name": "Ingeniería en Ciencias Informáticas",
  "code": "ICI"
}
→ 201 Created

POST /api/v1/anios-academicos/
{
  "career": 1,
  "year": 3
}
→ 201 Created

POST /api/v1/grupos/
{
  "career_year": 1,
  "name": "C-311"
}
→ 201 Created
```

#### 1.3 Asignación de Responsables

**Actor**: Directivo  
**Descripción**: Se asignan roles especiales a profesores

```http
POST /api/v1/profesores/
{
  "user": 15,  # ID del usuario profesor
  "employee_id": "EMP-20201234",
  "department": "Dirección de Becas"
}
→ 201 Created

POST /api/v1/profesores/1/decano/
{
  "faculty": 1  # Asigna como Decano de MATFISCOM
}
→ 201 Created

POST /api/v1/profesores/2/profesor-guia/
{
  "group": 1  # Asigna como Profesor Guía del grupo C-311
}
→ 201 Created

POST /api/v1/profesores/3/ppa/
{
  "career_year": 1  # Asigna como PPA del 3er año de ICI
}
→ 201 Created
```

### Fase 2: Ingreso de Estudiantes (Septiembre)

#### 2.1 Registro de Estudiantes

**Actor**: Instructor  
**Descripción**: Se registran los datos académicos y personales de estudiantes entrantes

```http
POST /api/v1/estudiantes/
{
  "user": 20,  # Usuario creado previamente (username, email, nombre, apellido)
  "ci": "90010112345",
  "student_id": "ICI-2024-001",
  "birth_date": "2004-01-15",
  "gender": "M",
  "group": 1,
  "address": "Calle 5, Apt 302, Santa Clara",
  "province": "Villa Clara",
  "municipality": "Santa Clara",
  "phone": "+53 4222-5555",
  "emergency_phone": "+53 4222-6666",
  "illnesses": "Alergia a penicilina",
  "is_militant": true,
  "is_cadet_far": false
}
→ 201 Created

# Se registran 40 estudiantes de la misma forma...
```

#### 2.2 Verificación de Datos

**Actor**: Instructor  
**Descripción**: Se consultan listados y se aplican filtros

```http
GET /api/v1/estudiantes/?group=1&ordering=-user__last_name
→ 200 OK
[
  {
    "id": 1,
    "student_id": "ICI-2024-001",
    "ci": "90010112345",
    "full_name": "Luis García López",
    "birth_date": "2004-01-15",
    "gender": "M",
    "group": {
      "id": 1,
      "name": "C-311",
      "career_year": { "year": 3, "career": {...} }
    },
    "is_militant": true
  },
  ...
]

# Búsqueda por nombre
GET /api/v1/estudiantes/?search=López
→ 200 OK

# Filtrado por campos
GET /api/v1/estudiantes/?is_militant=true&gender=F
→ 200 OK
```

### Fase 3: Asignación de Alojamiento (Septiembre-Octubre)

#### 3.1 Asignación de Cuartos

**Actor**: Instructor  
**Descripción**: Sistema automático de asignación de cuartos residenciales

```http
# Primero, verificar cuartos disponibles
GET /api/v1/cuartos/activas?wing=1
→ 200 OK
[
  {
    "id": 1,
    "number": "101",
    "wing": "Ala Norte",
    "capacity": 4,
    "current_occupancy": 3,
    "available_spots": 1,
    "is_full": false,
    "is_active": true
  },
  ...
]

# Asignar estudiante a cuarto
POST /api/v1/asignaciones/
{
  "student": 1,
  "room": 1,
  "assigned_date": "2025-09-15"
}
→ 201 Created
Response:
{
  "id": 1,
  "student": {"id": 1, "student_id": "ICI-2024-001", "full_name": "Luis García López"},
  "room": {"id": 1, "number": "101", "wing": "Ala Norte"},
  "assigned_date": "2025-09-15",
  "released_date": null,
  "is_active": true,
  "assigned_by": "instructor@uclv.cu"
}

# Se asignan 40 estudiantes... El sistema incrementa automáticamente
# current_occupancy en el cuarto (signal en modelo Assignment)

# Verificar ocupancia actualizada
GET /api/v1/cuartos/1/
→ 200 OK
{
  "current_occupancy": 4,  # Subió de 3 a 4
  "is_full": true  # Ahora está lleno
}
```

#### 3.2 Validaciones de Negocio

```http
# Intentar asignar estudiante que ya tiene asignación activa
POST /api/v1/asignaciones/
{
  "student": 1,  # Ya asignado en sección 3.1
  "room": 2
}
→ 400 Bad Request
{
  "student": "El estudiante 'Luis García López' ya tiene una asignación activa. Libera el cuarto..."
}

# Intentar asignar a cuarto lleno
POST /api/v1/asignaciones/
{
  "student": 2,
  "room": 1  # Ya tiene 4/4 ocupantes
}
→ 400 Bad Request
{
  "room": "El cuarto 101 está lleno (4/4 plazas)."
}

# Intentar asignar a cuarto inactivo
POST /api/v1/asignaciones/
{
  "student": 2,
  "room": 99  # Deshabilitado
}
→ 400 Bad Request
{
  "room": "El cuarto 99 está deshabilitado."
}
```

#### 3.3 Consulta de Asignaciones Activas

**Actor**: Instructor o Estudiante  
**Descripción**: Ver quién está asignado dónde

```http
# Listar todas las asignaciones (instructor)
GET /api/v1/asignaciones/activas/
→ 200 OK
[
  {
    "id": 1,
    "student": {"student_id": "ICI-2024-001", "full_name": "Luis García López"},
    "room": {"number": "101", "wing": "Ala Norte"},
    "assigned_date": "2025-09-15",
    "is_active": true
  },
  { "id": 2, ... },
  { "id": 3, ... }
]

# Estudiante ver su asignación actual
GET /api/v1/estudiantes/1/
→ 200 OK
{
  "student_id": "ICI-2024-001",
  "full_name": "Luis García López",
  "current_room": {
    "number": "101",
    "wing": "Ala Norte",
    "building": "Edificio de Ciencias"
  }
}
```

### Fase 4: Evaluación Continua (Semestral)

#### 4.1 Creación de Evaluaciones

**Actor**: Instructor  
**Descripción**: Evaluar comportamiento y desempeño de estudiantes

```http
POST /api/v1/evaluaciones/
{
  "student": 1,
  "date": "2025-10-31",
  "grade": "B",  # Bien, Regular (R), Mal (M)
  "comment": "Comportamiento ejemplar, participación en actividades de limpieza"
}
→ 201 Created
# created_by se asigna automáticamente al usuario autenticado

POST /api/v1/evaluaciones/
{
  "student": 2,
  "date": "2025-10-31",
  "grade": "R",
  "comment": "Incumplimiento de cuartelerías en dos ocasiones"
}
→ 201 Created
```

#### 4.2 Vista de Evaluaciones por Estudiante

**Actor**: Estudiante  
**Descripción**: El estudiante ve sus evaluaciones (solo las suyas)

```http
GET /api/v1/evaluaciones/mis-evaluaciones/
→ 200 OK
[
  {
    "id": 1,
    "student_id": "ICI-2024-001",
    "date": "2025-10-31",
    "grade": "B",
    "grade_display": "Bien",
    "comment": "Comportamiento ejemplar...",
    "created_by": "instructor@uclv.cu"
  }
]

# Otro estudiante no puede ver la evaluación de su compañero
GET /api/v1/evaluaciones/1/  # Intenta ver eval de otro
→ 404 Not Found
```

### Fase 5: Sistema de Quejas (Continuo)

#### 5.1 Estudiante Presenta Queja

**Actor**: Estudiante  
**Descripción**: Presentación de quejas, sugerencias o planteamientos

```http
POST /api/v1/quejas/
{
  "date": "2025-11-15",
  "building": 1,  # Opcional: el edificio donde ocurrió la falla
  "description": "Fugas de agua en el baño del cuarto 101. Necesita mantenimiento urgente.",
  "type": "administrativa"  # o "educativa"
}
→ 201 Created
# student se asigna automáticamente al usuario autenticado
# status = "pendiente" por defecto
# visibility = false por defecto (solo subdirector la ve)

Response:
{
  "id": 1,
  "student": "Luis García López",
  "date": "2025-11-15",
  "building": "Edificio de Ciencias",
  "description": "Fugas de agua...",
  "type": "administrativa",
  "status": "pendiente",
  "visibility": false,
  "response": null,
  "response_date": null,
  "created_at": "2025-11-15T14:23:10Z"
}
```

#### 5.2 Estudiante Consulta Sus Quejas

**Actor**: Estudiante  
**Descripción**: El estudiante ve solo sus propias quejas

```http
GET /api/v1/quejas/mis-quejas/
→ 200 OK
[
  {
    "id": 1,
    "description": "Fugas de agua en el baño del cuarto 101...",
    "status": "pendiente",
    "type": "administrativa"
  },
  {
    "id": 2,
    "description": "Falta coordinación en horarios de limpieza...",
    "status": "en_proceso",
    "type": "administrativa"
  }
]

# Ver quejas públicas (resueltas, visibles por otros)
GET /api/v1/quejas/visibles/
→ 200 OK
[
  {
    "id": 3,
    "description": "Sistema de agua caliente averiado en ala sur",
    "status": "resuelta",
    "response": "Se reparó el calentador. Fuente: mantenimiento",
    "visibility": true
  }
]
```

#### 5.3 Subdirector Gestiona Quejas

**Actor**: Subdirector  
**Descripción**: Cambio de estado, respuesta y control de visibilidad

```http
# Cambiar estado a "en_proceso"
PATCH /api/v1/quejas/1/estado/
{
  "status": "en_proceso"
}
→ 200 OK

# Responder queja (con mínimo 10 caracteres)
POST /api/v1/quejas/1/respuesta/
{
  "response": "Orden enviada a mantenimiento. Se espera reparación en 3 días."
}
→ 200 OK
# El status cambia automáticamente a "resuelta"

# Controlar visibilidad (si otros estudiantes la ven)
PATCH /api/v1/quejas/1/visibilidad/
{
  "visibility": true  # Otros estudiantes ahora la ven (anonimizada)
}
→ 200 OK
```

### Fase 6: Cuartelerías (Semanal/Rotativo)

#### 6.1 Instructor Crea Cuartelerías

**Actor**: Instructor  
**Descripción**: Asignación rotativa de labores de limpieza

```http
POST /api/v1/cuartelerias/
{
  "room": 1,
  "student": 1,
  "assigned_date": "2025-11-16"
}
→ 201 Created
Response:
{
  "id": 1,
  "room": "101 - Ala Norte",
  "student": "Luis García López",
  "assigned_date": "2025-11-16",
  "completed": false,
  "evaluation": null,
  "comments": ""
}

# Se crea cuartelería para estudiantes de ese cuarto (tarea de limpieza colectiva)
POST /api/v1/cuartelerias/
{
  "room": 1,
  "student": 2,
  "assigned_date": "2025-11-16"
}
→ 201 Created
```

#### 6.2 Estudiante Consulta Sus Cuartelerías

**Actor**: Estudiante  
**Descripción**: Ver cuartos que debe limpiar

```http
GET /api/v1/cuartelerias/mis-cuartelerias/
→ 200 OK
[
  {
    "id": 1,
    "room": "101 - Ala Norte",
    "assigned_date": "2025-11-16",
    "completed": false,
    "evaluation": null
  }
]
```

#### 6.3 Marcar Cuartelería Completada

**Actor**: Instructor  
**Descripción**: Instructor inspecciona y marca como completada con evaluación

```http
PATCH /api/v1/cuartelerias/1/completar/
{
  "evaluation": "B",  # B (Bien), R (Regular), M (Mal)
  "comments": "Se limpió satisfactoriamente. Fregado incluido."
}
→ 200 OK
Response:
{
  "id": 1,
  "room": "101",
  "student": "Luis García López",
  "completed": true,
  "evaluation": "B",
  "comments": "Se limpió satisfactoriamente. Fregado incluido."
}
```

### Fase 7: Comunicaciones

#### 7.1 Comunicador Publica Información

**Actor**: Comunicador  
**Descripción**: Publicación de informaciones, noticias y avisos

```http
POST /api/v1/informaciones/
{
  "title": "Suspensión de agua caliente - 20 de noviembre",
  "content": "Por mantenimiento de tuberías, el agua caliente estará suspendida...",
  "published_date": "2025-11-18",
  "expires_date": "2025-11-21",
  "is_public": true  # Visible para todos los estudiantes
}
→ 201 Created
# created_by se asigna automáticamente

POST /api/v1/informaciones/
{
  "title": "Reunión de instructores - Confidencial",
  "content": "Se discutirán políticas internas de asignaciones...",
  "is_public": false  # Solo para instructores/directivos
}
→ 201 Created
```

#### 7.2 Estudiante Ve Informaciones Públicas

**Actor**: Estudiante  
**Descripción**: Consultar avisos y comunicaciones públicas

```http
GET /api/v1/informaciones/publicas/
→ 200 OK
[
  {
    "id": 1,
    "title": "Suspensión de agua caliente - 20 de noviembre",
    "content": "Por mantenimiento de tuberías, el agua caliente estará suspendida...",
    "published_date": "2025-11-18",
    "expires_date": "2025-11-21"
  }
]
# Note: No incluye campos como created_by, is_public (ocultos para no exposer internals)

# Información expirada no aparece
GET /api/v1/informaciones/publicas/?expires_date__gte=2025-11-15
→ 200 OK (solo informaciones vigentes)
```

### Fase 8: Liberación de Cuarto (Julio)

#### 8.1 Instructor Libera Asignación

**Actor**: Instructor  
**Descripción**: Fin de la residencia, estudiante se va

```http
POST /api/v1/asignaciones/1/liberar/
{
  "released_date": "2026-07-31"  # Fecha en que se libera el cuarto
}
→ 200 OK
Response:
{
  "id": 1,
  "student": "Luis García López",
  "room": "101",
  "assigned_date": "2025-09-15",
  "released_date": "2026-07-31",  # Ahora tiene fecha
  "is_active": false  # Ya no está activo
}

# El sistema automáticamente decrementa current_occupancy del cuarto
GET /api/v1/cuartos/1/
→ 200 OK
{
  "current_occupancy": 3,  # Bajó de 4 a 3
  "is_full": false  # Ya no está lleno
}
```

#### 8.2 Historial de Asignaciones

**Actor**: Instructor o Directivo  
**Descripción**: Ver historial completo de quién estuvo dónde

```http
GET /api/v1/asignaciones/?student=1&ordering=-assigned_date
→ 200 OK
[
  {
    "id": 1,
    "student": "Luis García López",
    "room": "101",
    "assigned_date": "2025-09-15",
    "released_date": "2026-07-31",
    "is_active": false
  },
  { "id": 25, ... },  # Asignaciones anteriores del mismo estudiante
]
```

### Fase 9: Reportería

#### 9.1 Directivo Solicita Reporte

**Actor**: Directivo  
**Descripción**: Generación de reportes para análisis

```http
POST /api/v1/reportes/
{
  "name": "Ocupancia por Ala - Noviembre 2025",
  "type": "occupancy",  # o "assignments", "evaluations", "complaints", etc.
  "parameters": {
    "wing_id": 1,
    "month": "2025-11",
    "format": "pdf"
  }
}
→ 201 Created
Response:
{
  "id": 1,
  "name": "Ocupancia por Ala - Noviembre 2025",
  "type": "occupancy",
  "generated_date": "2025-11-20T15:45:00Z",
  "generated_by": "directivo@uclv.cu",
  "file_url": "/media/reports/occupancy_20251120_154500.pdf"
}
```

#### 9.2 Consultar Reportes Generados

**Actor**: Directivo  
**Descripción**: Historial de reportes

```http
GET /api/v1/reportes/?type=occupancy
→ 200 OK
[
  {
    "id": 1,
    "name": "Ocupancia por Ala - Noviembre 2025",
    "type": "occupancy",
    "generated_date": "2025-11-20T15:45:00Z",
    "file_url": "/media/reports/occupancy_20251120_154500.pdf"
  }
]
```

---

## Estructuras de Datos

### Modelo Relacional Simplificado

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Django User (auth_user)                     │
│  PK: id │ username │ email │ first_name │ last_name│ password     │
└──────────┬──────────────────────────────────────────────────────────┘
           │ (OneToOneField)
           ├─── ┌────────────────────────┐
           │    │      Student           │
           │    │ PK: id                 │
           │    │ ci (unique)            │
           │    │ student_id (unique)    │
           │    │ birth_date             │
           │    │ gender                 │
           │    │ group_id (FK)          │
           │    └────────────────────────┘
           │
           └─── ┌────────────────────────┐
                │      Professor         │
                │ PK: id                 │
                │ employee_id (unique)   │
                │ department             │
                └──────────┬─────────────┘
                           │
                ┌──────────┼──────────┐
                │          │          │
            ┌───▼──┐  ┌───▼──┐  ┌───▼────┐
            │ Dean │  │ PPA  │  │   PG   │
            └──────┘  └──────┘  └────────┘


┌─────────────────────┐
│       Group         │
│ PK: id              │
│ name                │
│ career_year_id (FK) │
└──────────┬──────────┘
           │ (OneToMany)
           └─── ┌────────────────┐
                │   Students *   │
                └────────────────┘


┌──────────────────────┐
│ CareerYear           │
│ PK: id               │
│ year                 │
│ career_id (FK)       │
└─────────┬────────────┘
          │ (OneToMany)
          └─── ┌────────────────────┐
               │ Groups *           │
               └────────────────────┘

┌──────────────────────┐
│   Career             │
│ PK: id               │
│ name                 │
│ code                 │
│ faculty_id (FK)      │
└─────────┬────────────┘
          │ (OneToMany)
          └─── ┌────────────────────┐
               │ CareerYears *      │
               └────────────────────┘

┌──────────────────────┐
│   Faculty            │
│ PK: id               │
│ name                 │
│ code                 │
└──────────────────────┘

┌──────────────────────┐
│   Site               │
│ PK: id               │
│ name                 │
│ address              │
└─────────┬────────────┘
          │ (OneToMany)
          └─── ┌────────────────────┐
               │ Buildings *        │
               └────────────────────┘

┌──────────────────────┐
│   Building           │
│ PK: id               │
│ name                 │
│ site_id (FK)         │
└─────────┬────────────┘
          │ (OneToMany)
          └─── ┌────────────────────┐
               │ Wings *            │
               └────────────────────┘

┌──────────────────────┐
│   Wing               │
│ PK: id               │
│ name                 │
│ building_id (FK)     │
└─────────┬────────────┘
          │ (OneToMany)
          └─── ┌────────────────────┐
               │ Rooms *            │
               └────────────────────┘

┌────────────────────────┐
│   Room                 │
│ PK: id                 │
│ number                 │
│ capacity               │
│ current_occupancy      │
│ is_active              │
│ wing_id (FK)           │
└─────────┬──────────────┘
          │ (OneToMany)
          └─── ┌────────────────────┐
               │ Assignments *      │
               └────────────────────┘

┌──────────────────────┐
│  Assignment          │
│ PK: id               │
│ student_id (FK)      │
│ room_id (FK)         │
│ assigned_date        │
│ released_date        │
│ assigned_by_id (FK)  │
└──────────────────────┘

┌────────────────────────┐
│   Complaint            │
│ PK: id                 │
│ student_id (FK)        │
│ date                   │
│ building_id (FK, null) │
│ description            │
│ type                   │
│ status                 │
│ visibility             │
│ response               │
│ response_date          │
└────────────────────────┘

┌────────────────────────┐
│   Evaluation           │
│ PK: id                 │
│ student_id (FK)        │
│ date                   │
│ grade                  │
│ comment                │
│ created_by_id (FK)     │
└────────────────────────┘

┌────────────────────────┐
│   CleaningSchedule     │
│ PK: id                 │
│ room_id (FK)           │
│ student_id (FK)        │
│ assigned_date          │
│ completed              │
│ evaluation             │
│ comments               │
└────────────────────────┘

┌────────────────────────┐
│   Information          │
│ PK: id                 │
│ title                  │
│ content                │
│ published_date         │
│ expires_date           │
│ is_public              │
│ created_by_id (FK)     │
└────────────────────────┘

┌────────────────────────┐
│   Report               │
│ PK: id                 │
│ name                   │
│ type                   │
│ parameters (JSON)      │
│ generated_date         │
│ generated_by_id (FK)   │
│ file_url               │
└────────────────────────┘
```

---

## Endpoints y Operaciones Disponibles

### Autenticación

```http
POST   /api/v1/auth/login/               # Obtener tokens JWT
POST   /api/v1/auth/refresh/             # Refrescar access token
POST   /api/v1/auth/logout/              # Logout (client-side)
POST   /api/v1/auth/cambiar-contrasena/  # Cambiar contraseña
GET    /api/v1/auth/me/                  # Datos del usuario autenticado

GET    /api/v1/roles/                    # Listar roles
GET    /api/v1/usuarios/                 # Listar usuarios (admin)
POST   /api/v1/usuarios/                 # Crear usuario (admin)
GET    /api/v1/usuarios/{id}/            # Detalle de usuario
PATCH  /api/v1/usuarios/{id}/            # Actualizar usuario
DELETE /api/v1/usuarios/{id}/            # Eliminar usuario
POST   /api/v1/usuarios/{id}/roles/      # Asignar rol
DELETE /api/v1/usuarios/{id}/roles/{rol_id}/  # Remover rol
GET    /api/v1/usuarios/{id}/permisos/   # Listar permisos
```

### Estructura Académica

```http
GET    /api/v1/facultades/               # Listar
POST   /api/v1/facultades/               # Crear
GET    /api/v1/facultades/{id}/          # Detalle
PATCH  /api/v1/facultades/{id}/          # Actualizar
DELETE /api/v1/facultades/{id}/          # Eliminar

GET    /api/v1/carreras/?faculty={id}    # Listar por facultad
POST   /api/v1/carreras/                 # Crear
GET    /api/v1/carreras/{id}/            # Detalle
PATCH  /api/v1/carreras/{id}/            # Actualizar
DELETE /api/v1/carreras/{id}/            # Eliminar

GET    /api/v1/anios-academicos/?career={id}  # Listar por carrera
POST   /api/v1/anios-academicos/              # Crear
GET    /api/v1/anios-academicos/{id}/        # Detalle
...

GET    /api/v1/grupos/?career_year={id}  # Listar por año
POST   /api/v1/grupos/                   # Crear
GET    /api/v1/grupos/{id}/              # Detalle
...
```

### Infraestructura Física

```http
GET    /api/v1/sedes/                    # Listar
POST   /api/v1/sedes/                    # Crear
GET    /api/v1/sedes/{id}/               # Detalle
PATCH  /api/v1/sedes/{id}/               # Actualizar
DELETE /api/v1/sedes/{id}/               # Eliminar (con protección)

GET    /api/v1/edificios/?site={id}      # Listar por sede
POST   /api/v1/edificios/                # Crear
GET    /api/v1/edificios/{id}/           # Detalle
...

GET    /api/v1/alas/?building={id}       # Listar por edificio
POST   /api/v1/alas/                     # Crear
...

GET    /api/v1/cuartos/?wing={id}        # Listar por ala (paginated)
POST   /api/v1/cuartos/                  # Crear
GET    /api/v1/cuartos/{id}/             # Detalle con ocupancia
PATCH  /api/v1/cuartos/{id}/             # Actualizar
DELETE /api/v1/cuartos/{id}/             # Eliminar
```

### Gestión de Personas

```http
# Estudiantes
GET    /api/v1/estudiantes/?group={id}&search=apellido  # Listar con filtros
POST   /api/v1/estudiantes/              # Crear
GET    /api/v1/estudiantes/{id}/         # Detalle
PATCH  /api/v1/estudiantes/{id}/         # Actualizar
DELETE /api/v1/estudiantes/{id}/         # Eliminar

# Profesores
GET    /api/v1/profesores/
POST   /api/v1/profesores/
GET    /api/v1/profesores/{id}/
PATCH  /api/v1/profesores/{id}/
DELETE /api/v1/profesores/{id}/

# Sub-roles de profesores
GET    /api/v1/profesores/{id}/decano/
POST   /api/v1/profesores/{id}/decano/
DELETE /api/v1/profesores/{id}/decano/

GET    /api/v1/profesores/{id}/profesor-guia/
POST   /api/v1/profesores/{id}/profesor-guia/
DELETE /api/v1/profesores/{id}/profesor-guia/

GET    /api/v1/profesores/{id}/ppa/
POST   /api/v1/profesores/{id}/ppa/
DELETE /api/v1/profesores/{id}/ppa/
```

### Operaciones Continuas

```http
# Asignaciones de Cuartos
POST   /api/v1/asignaciones/             # Asignar cuarto
GET    /api/v1/asignaciones/activas/     # Ver activas
GET    /api/v1/asignaciones/{id}/        # Detalle
POST   /api/v1/asignaciones/{id}/liberar/  # Liberar

# Evaluaciones
POST   /api/v1/evaluaciones/             # Crear
GET    /api/v1/evaluaciones/             # Listar
GET    /api/v1/evaluaciones/{id}/        # Detalle
PATCH  /api/v1/evaluaciones/{id}/        # Actualizar
DELETE /api/v1/evaluaciones/{id}/        # Eliminar
GET    /api/v1/evaluaciones/mis-evaluaciones/  # Ver mías

# Cuartelerías
POST   /api/v1/cuartelerias/             # Crear
GET    /api/v1/cuartelerias/             # Listar
GET    /api/v1/cuartelerias/mis-cuartelerias/  # Ver mías
PATCH  /api/v1/cuartelerias/{id}/completar/   # Marcar completada

# Quejas
POST   /api/v1/quejas/                   # Crear
GET    /api/v1/quejas/mis-quejas/        # Ver mías
GET    /api/v1/quejas/{id}/              # Detalle
PATCH  /api/v1/quejas/{id}/              # Actualizar
DELETE /api/v1/quejas/{id}/              # Eliminar
GET    /api/v1/quejas/visibles/          # Ver públicas
PATCH  /api/v1/quejas/{id}/estado/       # Cambiar estado
POST   /api/v1/quejas/{id}/respuesta/    # Responder
PATCH  /api/v1/quejas/{id}/visibilidad/  # Controlar visibilidad

# Informaciones
POST   /api/v1/informaciones/            # Crear
GET    /api/v1/informaciones/            # Listar
GET    /api/v1/informaciones/{id}/       # Detalle
PATCH  /api/v1/informaciones/{id}/       # Actualizar
DELETE /api/v1/informaciones/{id}/       # Eliminar
GET    /api/v1/informaciones/publicas/   # Ver públicas

# Reportes
POST   /api/v1/reportes/                 # Crear reporte
GET    /api/v1/reportes/{id}/            # Detalle
GET    /api/v1/reportes/                 # Listar
```

---

## Flujo de Autenticación y Autorización

### 1. Login

```http
POST /api/v1/auth/login/
Content-Type: application/json

{
  "username": "luis_garcia",
  "password": "MiPassword123!"
}

Response 200 OK:
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": 20,
    "username": "luis_garcia",
    "email": "luis@uclv.cu",
    "first_name": "Luis",
    "last_name": "García",
    "roles": ["estudiante", "lider_udjc"]  # Roles en payload JWT
  }
}
```

### 2. Uso del Token

```http
GET /api/v1/estudiantes/1/
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
Accept: application/json

Response 200 OK:
{ "id": 1, "student_id": "ICI-2024-001", ... }
```

### 3. Refrescar Token

```http
POST /api/v1/auth/refresh/
Content-Type: application/json

{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}

Response 200 OK:
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."  # Nuevo access
}
```

### 4. Logout

```http
POST /api/v1/auth/logout/
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...

Response 200 OK:
{
  "message": "Logout exitoso. Descarta los tokens en el cliente."
}
```

### 5. Matriz de Permisos por Rol

| Recurso | Estudiante | Instructor | Directivo | Subdirector | Comunicador | Admin |
|---------|-----------|------------|-----------|-------------|-------------|-------|
| CRUD Estudiantes | - | ✓ (R) | ✓ (RWD) | - | - | ✓ |
| CRUD Infraestructura | - | - | ✓ (RWD) | - | - | ✓ |
| Crear Evaluación | - | ✓ | ✓ | - | - | ✓ |
| Ver Evaluaciones Propias | ✓ | ✓ | ✓ | - | - | ✓ |
| Crear Queja | ✓ | - | - | - | - | ✓ |
| Responder Queja | - | - | - | ✓ | - | ✓ |
| Crear Información | - | - | - | - | ✓ | ✓ |
| Ver Info Pública | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Asignar Cuartos | - | ✓ | ✓ | - | - | ✓ |
| Crear Reporte | - | - | ✓ | - | - | ✓ |
| Gestionar Roles | - | - | - | - | - | ✓ |

---

## Procesos Operativos

### Señales Automáticas del Sistema

El sistema implementa **Django Signals** para automaticidad:

#### Signal 1: Incremento de Ocupancia (Assignment Created)

```python
# Cuando se crea una asignación
Assignment.objects.create(student=Luis, room=101)
# → Se dispara signal post_save
# → Incrementa Room.current_occupancy en 1
# → Si current_occupancy == capacity → Room.is_full = True
```

#### Signal 2: Decremento de Ocupancia (Assignment Released)

```python
# Cuando se libera una asignación
assignment.released_date = "2026-07-31"
assignment.save()
# → Se dispara signal post_save
# → Decrementa Room.current_occupancy en 1
# → Si current_occupancy < capacity → Room.is_full = False
```

### Validaciones de Negocio

1. **No duplicados de Matrículas**
   - Campo `student_id` es UNIQUE
   - Intento de crear duplicado → IntegrityError

2. **No duplicados de CI**
   - Campo `ci` es UNIQUE
   - Fuerza identificación única

3. **Asignación Única Activa**
   - Un estudiante solo puede tener 1 asignación con `released_date=NULL`
   - Intento de crear segunda → ValidationError

4. **Ocupancia Máxima de Cuartos**
   - `current_occupancy <= capacity`
   - Intento de exceder → ValidationError

5. **Cuartos Inactivos No se Asignan**
   - Campo `is_active` False bloquea asignaciones
   - Para mantenimiento o desuso

6. **Respuesta de Queja Mínima**
   - Mínimo 10 caracteres
   - Evita respuestas triviales

---

## Reportes y Auditoría

### Campos de Auditoría en Todos los Modelos

```python
created_at = models.DateTimeField(auto_now_add=True)  # No se modifica
updated_at = models.DateTimeField(auto_now=True)      # Se actualiza siempre
```

### Trazabilidad

```python
# Asignaciones: quién asignó
assignment.assigned_by = request.user  # Capturado automáticamente

# Evaluaciones: quién evaluó
evaluation.created_by = request.user   # Capturado automáticamente

# Información: quién publicó
information.created_by = request.user   # Capturado automáticamente

# Reportes: quién los generó
report.generated_by = request.user      # Capturado automáticamente
```

### Consultas Analíticas (Ejemplos)

```http
# Estudiantes evaluados en el mes
GET /api/v1/evaluaciones/?date__gte=2025-11-01&date__lte=2025-11-30

# Quejas resueltas por edificio
GET /api/v1/quejas/?building=1&status=resuelta

# Ocupancia por ala
GET /api/v1/cuartos/?wing=1&ordering=number

# Estudiantes de facultad específica (solo decano)
GET /api/v1/estudiantes/?group__career_year__career__faculty=1
```

---

## Resumen: Ciclo Completo de Operación

```
┌─────────────────────────────────────────────────────────────────────┐
│              AÑO ACADÉMICO TÍPICO (SEPT 2025 - JUL 2026)           │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  SEP: Preparación                                                 │
│    1. Directivo prepara infraestructura (sedes, edificios, alas)  │
│    2. Directivo registra estructura académica (facultades, carreras)│
│    3. Directivo asigna roles especiales a profesores             │
│                                                                     │
│  SEPT: Ingreso                                                    │
│    4. Instructor registra estudiantes nuevos                      │
│    5. Instructor verifica datos académicos (filtros, búsquedas)   │
│                                                                     │
│  SEPT-OCT: Alojamiento                                             │
│    6. Instructor asigna cuartos con validaciones automáticas      │
│    7. Sistema incrementa ocupancia en cuartos (signals)           │
│    8. Estudiante consulta su cuarto asignado                      │
│                                                                     │
│  OCT-JUN: Operación Continua                                       │
│    9. Instructor crea evaluaciones (semestral)                    │
│   10. Estudiante ve sus evaluaciones y quejas                     │
│   11. Estudiante presenta quejas (problema/sugerencia)            │
│   12. Subdirector responde quejas (estado, respuesta, visibilidad)│
│   13. Instructor asigna cuartelerías (semanal)                    │
│   14. Instructor marca cuartelerías completadas                   │
│   15. Comunicador publica informaciones/noticias                  │
│   16. Estudiante ve informaciones públicas                        │
│                                                                     │
│  JUL: Cierre                                                      │
│   17. Instructor libera cuartos (fin de semestre)                 │
│   18. Sistema decrementa ocupancia (signals)                      │
│   19. Directivo genera reportes analíticos                        │
│                                                                     │
│  Cualquier momento: Auditoría                                     │
│   • Todos los cambios registrados con timestamp y usuario         │
│   • Historial de asignaciones completo                           │
│   • Trazabilidad de decisiones (quién hizo qué)                  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Configuración del Entorno

### Variables de Entorno Requeridas

```bash
# .env file (JAMAS incluir en VCS)
SECRET_KEY=una-clave-muy-secreta-minimo-50-caracteres
DEBUG=True                                    # Nunca True en producción
ALLOWED_HOSTS=localhost,127.0.0.1,tu-dominio.com

# Base de Datos PostgreSQL (producción)
DB_NAME=uclv_residencias
DB_USER=postgres
DB_PASSWORD=tu-contraseña-fuerte
DB_HOST=localhost
DB_PORT=5432

# CORS (frontend desacoplado)
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173,https://mi-frontend.com
```

### Ejecución del Sistema

```bash
# 1. Crear .env desde .env.example
cp .env.example .env

# 2. Instalar dependencias
uv pip install -r requirements/dev.txt

# 3. Migraciones
python manage.py migrate

# 4. Crear superusuario
python manage.py createsuperuser

# 5. Crear roles iniciales
python manage.py create_roles

# 6. Ejecutar servidor
python manage.py runserver

# 7. Acceder a API
# http://localhost:8000/api/v1/docs/     # Swagger UI
# http://localhost:8000/admin/           # Django Admin
```

### Ejecución de Tests

```bash
# Suite completa
pytest

# Con cobertura
pytest --cov=apps --cov-report=html

# Tests específicos
pytest tests/integration/test_assignments.py -v
pytest tests/unit/test_permissions.py -v
```

---

## Conclusión

Este sistema implementa un control integral y robusto de residencias estudiantiles, capaz de manejar:

✅ **140 tests de cobertura completa** (100% de endpoints)  
✅ **RBAC de 9 roles** con permisos a nivel de objeto  
✅ **Validaciones de negocio** automáticas (signals)  
✅ **Auditoría completa** de cambios  
✅ **API REST** documentada con OpenAPI/Swagger  
✅ **Escalabilidad horizontal** (arquitectura stateless JWT)  

Está listo para producción tras configurar la base de datos PostgreSQL y las variables de entorno aproppiadas.

---

**Última actualización**: 21 de mayo de 2026  
**Versión del Sistema**: 1.0.0  
**Framework**: Django 5.0.6 + Django REST Framework 3.15.2  
**Año Académico**: Septiembre 2025 — Julio 2026
