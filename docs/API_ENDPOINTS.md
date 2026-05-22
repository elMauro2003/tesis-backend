# 📡 Catálogo de Endpoints API

**Referencia exhaustiva de los 70+ endpoints REST disponibles, organizados por dominio. Para exploración interactiva, ve a Swagger: [http://localhost:8000/api/v1/docs/](http://localhost:8000/api/v1/docs/)**

---

## Tabla de Contenidos

1. [Autenticación](#autenticación)
2. [Estructura Académica](#estructura-académica)
3. [Infraestructura Física](#infraestructura-física)
4. [Gestión de Personas](#gestión-de-personas)
5. [Operaciones Continuas](#operaciones-continuas)
6. [Administración](#administración)
7. [Códigos HTTP](#códigos-http)
8. [Ejemplos de Filtrado](#ejemplos-de-filtrado)

---

## Autenticación

### Login / Tokens

| Método | Endpoint | Descripción | Requiere Auth |
|--------|----------|-------------|---------------|
| POST | `/api/v1/auth/login/` | Obtener access y refresh tokens | ❌ |
| POST | `/api/v1/auth/refresh/` | Refrescar access token | ❌ |
| POST | `/api/v1/auth/logout/` | Logout (client-side) | ✅ |
| POST | `/api/v1/auth/cambiar-contrasena/` | Cambiar contraseña | ✅ |
| GET | `/api/v1/auth/me/` | Datos del usuario autenticado | ✅ |

**Request/Response Ejemplo:**

```http
POST /api/v1/auth/login/
Content-Type: application/json

{
  "username": "luis_garcia",
  "password": "Password123!"
}

Response 200:
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": 1,
    "username": "luis_garcia",
    "email": "luis@uclv.cu",
    "roles": ["estudiante"]
  }
}
```

---

## Estructura Académica

### Facultades

| Método | Endpoint | Descripción | Roles Autorizados |
|--------|----------|-------------|-------------------|
| GET | `/api/v1/facultades/` | Listar todas | Directivo, Admin |
| POST | `/api/v1/facultades/` | Crear | Directivo, Admin |
| GET | `/api/v1/facultades/{id}/` | Detalle | Directivo, Admin |
| PATCH | `/api/v1/facultades/{id}/` | Actualizar | Directivo, Admin |
| DELETE | `/api/v1/facultades/{id}/` | Eliminar | Directivo, Admin |

### Carreras

| Método | Endpoint | Descripción | Roles |
|--------|----------|-------------|-------|
| GET | `/api/v1/carreras/` | Listar todas | Directivo, Admin |
| GET | `/api/v1/carreras/?faculty={id}` | Listar por facultad | Directivo, Admin |
| POST | `/api/v1/carreras/` | Crear | Directivo, Admin |
| GET | `/api/v1/carreras/{id}/` | Detalle | Directivo, Admin |
| PATCH | `/api/v1/carreras/{id}/` | Actualizar | Directivo, Admin |
| DELETE | `/api/v1/carreras/{id}/` | Eliminar | Directivo, Admin |

### Años Académicos

| Método | Endpoint | Descripción | Roles |
|--------|----------|-------------|-------|
| GET | `/api/v1/anios-academicos/` | Listar todos | Directivo, Admin |
| GET | `/api/v1/anios-academicos/?career={id}` | Por carrera | Directivo, Admin |
| POST | `/api/v1/anios-academicos/` | Crear | Directivo, Admin |
| GET | `/api/v1/anios-academicos/{id}/` | Detalle | Directivo, Admin |
| PATCH | `/api/v1/anios-academicos/{id}/` | Actualizar | Directivo, Admin |
| DELETE | `/api/v1/anios-academicos/{id}/` | Eliminar | Directivo, Admin |

### Grupos de Estudiantes

| Método | Endpoint | Descripción | Roles |
|--------|----------|-------------|-------|
| GET | `/api/v1/grupos/` | Listar todos | Directivo, Instructor, Admin |
| GET | `/api/v1/grupos/?career_year={id}` | Por año académico | Directivo, Instructor, Admin |
| POST | `/api/v1/grupos/` | Crear | Directivo, Admin |
| GET | `/api/v1/grupos/{id}/` | Detalle | Directivo, Instructor, Admin |
| PATCH | `/api/v1/grupos/{id}/` | Actualizar | Directivo, Admin |
| DELETE | `/api/v1/grupos/{id}/` | Eliminar | Directivo, Admin |

---

## Infraestructura Física

### Sedes

| Método | Endpoint | Descripción | Roles |
|--------|----------|-------------|-------|
| GET | `/api/v1/sedes/` | Listar todas | Directivo, Admin |
| POST | `/api/v1/sedes/` | Crear | Directivo, Admin |
| GET | `/api/v1/sedes/{id}/` | Detalle | Directivo, Admin |
| PATCH | `/api/v1/sedes/{id}/` | Actualizar | Directivo, Admin |
| DELETE | `/api/v1/sedes/{id}/` | Eliminar (con protección) | Directivo, Admin |

### Edificios

| Método | Endpoint | Descripción | Roles |
|--------|----------|-------------|-------|
| GET | `/api/v1/edificios/` | Listar todos | Directivo, Admin |
| GET | `/api/v1/edificios/?site={id}` | Por sede | Directivo, Admin |
| POST | `/api/v1/edificios/` | Crear | Directivo, Admin |
| GET | `/api/v1/edificios/{id}/` | Detalle | Directivo, Admin |
| PATCH | `/api/v1/edificios/{id}/` | Actualizar | Directivo, Admin |
| DELETE | `/api/v1/edificios/{id}/` | Eliminar (con protección) | Directivo, Admin |

### Alas

| Método | Endpoint | Descripción | Roles |
|--------|----------|-------------|-------|
| GET | `/api/v1/alas/` | Listar todas | Directivo, Admin |
| GET | `/api/v1/alas/?building={id}` | Por edificio | Directivo, Admin |
| POST | `/api/v1/alas/` | Crear | Directivo, Admin |
| GET | `/api/v1/alas/{id}/` | Detalle | Directivo, Admin |
| PATCH | `/api/v1/alas/{id}/` | Actualizar | Directivo, Admin |
| DELETE | `/api/v1/alas/{id}/` | Eliminar (con protección) | Directivo, Admin |

### Cuartos

| Método | Endpoint | Descripción | Roles | Params |
|--------|----------|-------------|-------|--------|
| GET | `/api/v1/cuartos/` | Listar todos (paginated) | Directivo, Instructor, Admin | wing, is_active, page, page_size |
| GET | `/api/v1/cuartos/?wing={id}` | Por ala | Directivo, Instructor, Admin | |
| GET | `/api/v1/cuartos/activas/` | Solo activos | Directivo, Instructor, Admin | |
| POST | `/api/v1/cuartos/` | Crear | Directivo, Admin | |
| GET | `/api/v1/cuartos/{id}/` | Detalle con ocupancia | Directivo, Instructor, Admin | |
| PATCH | `/api/v1/cuartos/{id}/` | Actualizar | Directivo, Admin | |
| DELETE | `/api/v1/cuartos/{id}/` | Eliminar | Directivo, Admin | |

---

## Gestión de Personas

### Estudiantes

| Método | Endpoint | Descripción | Roles | Params |
|--------|----------|-------------|-------|--------|
| GET | `/api/v1/estudiantes/` | Listar todos (paginated) | Instructor, Directivo, Admin | search, group, gender, is_militant, page |
| POST | `/api/v1/estudiantes/` | Crear | Instructor, Directivo, Admin | |
| GET | `/api/v1/estudiantes/?search=Lopez` | Buscar | Instructor, Directivo, Admin | |
| GET | `/api/v1/estudiantes/{id}/` | Detalle | Instructor, Directivo, Admin | |
| PATCH | `/api/v1/estudiantes/{id}/` | Actualizar | Instructor, Directivo, Admin | |
| DELETE | `/api/v1/estudiantes/{id}/` | Eliminar | Instructor, Directivo, Admin | |

**Ejemplo de filtrado:**

```http
GET /api/v1/estudiantes/?group=1&gender=F&is_militant=true&page=1
Authorization: Bearer <token>
```

### Profesores

| Método | Endpoint | Descripción | Roles |
|--------|----------|-------------|-------|
| GET | `/api/v1/profesores/` | Listar todos | Directivo, Admin |
| POST | `/api/v1/profesores/` | Crear | Admin |
| GET | `/api/v1/profesores/{id}/` | Detalle | Directivo, Admin |
| PATCH | `/api/v1/profesores/{id}/` | Actualizar | Admin |
| DELETE | `/api/v1/profesores/{id}/` | Eliminar | Admin |

### Asignación de Roles a Profesores

| Método | Endpoint | Descripción | Roles |
|--------|----------|-------------|-------|
| POST | `/api/v1/profesores/{id}/decano/` | Asignar decano | Admin |
| DELETE | `/api/v1/profesores/{id}/decano/` | Remover decano | Admin |
| POST | `/api/v1/profesores/{id}/profesor-guia/` | Asignar PG | Admin |
| DELETE | `/api/v1/profesores/{id}/profesor-guia/` | Remover PG | Admin |
| POST | `/api/v1/profesores/{id}/ppa/` | Asignar PPA | Admin |
| DELETE | `/api/v1/profesores/{id}/ppa/` | Remover PPA | Admin |

---

## Operaciones Continuas

### Evaluaciones

| Método | Endpoint | Descripción | Roles | Params |
|--------|----------|-------------|-------|--------|
| GET | `/api/v1/evaluaciones/` | Listar todas | Instructor, Directivo, Admin | student, date, grade, page |
| POST | `/api/v1/evaluaciones/` | Crear | Instructor, Directivo, Admin | |
| GET | `/api/v1/evaluaciones/{id}/` | Detalle | Instructor, Directivo, Admin | |
| PATCH | `/api/v1/evaluaciones/{id}/` | Actualizar | Instructor, Directivo, Admin | |
| DELETE | `/api/v1/evaluaciones/{id}/` | Eliminar | Instructor, Directivo, Admin | |
| GET | `/api/v1/evaluaciones/mis-evaluaciones/` | Mis evaluaciones | Estudiante | |

### Quejas

| Método | Endpoint | Descripción | Roles | Params |
|--------|----------|-------------|-------|--------|
| GET | `/api/v1/quejas/` | Listar todas | Subdirector, Admin | status, type, date, page |
| POST | `/api/v1/quejas/` | Crear | Estudiante | |
| GET | `/api/v1/quejas/{id}/` | Detalle | Estudiante (propia), Subdirector | |
| PATCH | `/api/v1/quejas/{id}/` | Actualizar | Estudiante (propia) | |
| DELETE | `/api/v1/quejas/{id}/` | Eliminar | Estudiante (propia) | |
| GET | `/api/v1/quejas/mis-quejas/` | Mis quejas | Estudiante | |
| GET | `/api/v1/quejas/visibles/` | Quejas públicas | Estudiante | |
| PATCH | `/api/v1/quejas/{id}/estado/` | Cambiar estado | Subdirector | |
| POST | `/api/v1/quejas/{id}/respuesta/` | Responder | Subdirector | |
| PATCH | `/api/v1/quejas/{id}/visibilidad/` | Controlar visibilidad | Subdirector | |

### Asignaciones de Cuartos

| Método | Endpoint | Descripción | Roles | Params |
|--------|----------|-------------|-------|--------|
| GET | `/api/v1/asignaciones/` | Listar todas | Instructor, Directivo, Admin | student, room, is_active, page |
| POST | `/api/v1/asignaciones/` | Crear (asignar) | Instructor, Directivo, Admin | |
| GET | `/api/v1/asignaciones/{id}/` | Detalle | Instructor, Directivo, Admin | |
| GET | `/api/v1/asignaciones/activas/` | Solo activas | Instructor, Directivo, Admin | |
| POST | `/api/v1/asignaciones/{id}/liberar/` | Liberar cuarto | Instructor, Directivo, Admin | |

### Cuartelerías

| Método | Endpoint | Descripción | Roles | Params |
|--------|----------|-------------|-------|--------|
| GET | `/api/v1/cuartelerias/` | Listar todas | Instructor, Directivo, Admin | room, student, completed, page |
| POST | `/api/v1/cuartelerias/` | Crear | Instructor, Directivo, Admin | |
| GET | `/api/v1/cuartelerias/{id}/` | Detalle | Instructor, Directivo, Admin | |
| GET | `/api/v1/cuartelerias/mis-cuartelerias/` | Mis cuartelerías | Estudiante | |
| PATCH | `/api/v1/cuartelerias/{id}/completar/` | Marcar completada | Instructor, Directivo, Admin | |

### Informaciones

| Método | Endpoint | Descripción | Roles | Params |
|--------|----------|-------------|-------|--------|
| GET | `/api/v1/informaciones/` | Listar todas | Comunicador, Directivo, Admin | is_public, expires_date, page |
| POST | `/api/v1/informaciones/` | Crear | Comunicador, Directivo, Admin | |
| GET | `/api/v1/informaciones/{id}/` | Detalle | Comunicador, Directivo, Admin | |
| PATCH | `/api/v1/informaciones/{id}/` | Actualizar | Comunicador, Directivo, Admin | |
| DELETE | `/api/v1/informaciones/{id}/` | Eliminar | Comunicador, Directivo, Admin | |
| GET | `/api/v1/informaciones/publicas/` | Públicas vigentes | Estudiante, autenticados | |

### Reportes

| Método | Endpoint | Descripción | Roles | Params |
|--------|----------|-------------|-------|--------|
| POST | `/api/v1/reportes/` | Crear reporte | Directivo, Admin | |
| GET | `/api/v1/reportes/` | Listar todos | Directivo, Admin | type, generated_date, page |
| GET | `/api/v1/reportes/{id}/` | Detalle | Directivo, Admin | |

---

## Administración

### Roles

| Método | Endpoint | Descripción | Roles |
|--------|----------|-------------|-------|
| GET | `/api/v1/roles/` | Listar todos | Admin |

### Usuarios

| Método | Endpoint | Descripción | Roles |
|--------|----------|-------------|-------|
| GET | `/api/v1/usuarios/` | Listar todos | Admin |
| POST | `/api/v1/usuarios/` | Crear | Admin |
| GET | `/api/v1/usuarios/{id}/` | Detalle | Admin |
| PATCH | `/api/v1/usuarios/{id}/` | Actualizar | Admin |
| DELETE | `/api/v1/usuarios/{id}/` | Eliminar | Admin |
| POST | `/api/v1/usuarios/{id}/roles/` | Asignar roles | Admin |
| DELETE | `/api/v1/usuarios/{id}/roles/{role_id}/` | Remover rol | Admin |
| GET | `/api/v1/usuarios/{id}/permisos/` | Listar permisos | Admin |

---

## Códigos HTTP

| Código | Significado | Caso de Uso |
|--------|------------|-----------|
| **200** | OK | Operación exitosa (GET, PATCH) |
| **201** | Created | Recurso creado exitosamente (POST) |
| **204** | No Content | Recurso eliminado (DELETE) |
| **400** | Bad Request | validación fallida, datos inválidos |
| **401** | Unauthorized | Token faltante o inválido |
| **403** | Forbidden | Usuario autenticado pero sin permisos |
| **404** | Not Found | Recurso no existe |
| **409** | Conflict | Violación de constraint (ej: ocupancia llena) |
| **429** | Too Many Requests | Rate limit alcanzado (5 intentos de login fallidos) |
| **500** | Internal Server Error | Error del servidor |

---

## Ejemplos de Filtrado

### Filtrado Simple

```http
# Por grupo
GET /api/v1/estudiantes/?group=1

# Por género
GET /api/v1/estudiantes/?gender=F

# Combinar filtros (AND)
GET /api/v1/estudiantes/?group=1&gender=F
```

### Búsqueda

```http
# Buscar por nombre o CI
GET /api/v1/estudiantes/?search=Lopez

# Búsqueda case-insensitive
GET /api/v1/estudiantes/?search=luis
```

### Filtrado Avanzado

```http
# Quejas por estado
GET /api/v1/quejas/?status=resuelta

# Evaluaciones por rango de fechas
GET /api/v1/evaluaciones/?date__gte=2025-09-01&date__lte=2025-12-31

# Cuartos activos solamente
GET /api/v1/cuartos/?is_active=true

# Cuartos llenos
GET /api/v1/cuartos/?is_full=true
```

### Paginación

```http
# Página 1 (defecto: 20 elementos)
GET /api/v1/estudiantes/?page=1

# Página 3 con 50 elementos por página
GET /api/v1/estudiantes/?page=3&page_size=50

# Respone paginada:
{
  "count": 150,  # Total de elementos
  "next": "http://localhost:8000/api/v1/estudiantes/?page=2",
  "previous": null,
  "results": [...]  # Los 20 elementos de la página 1
}
```

### Ordenamiento

```http
# Ordenar ascendente (por defecto)
GET /api/v1/estudiantes/?ordering=student_id

# Ordenar descendente
GET /api/v1/estudiantes/?ordering=-created_at

# Múltiples campos
GET /api/v1/estudiantes/?ordering=-group,student_id
```

---

## Documentación Interactiva

### Swagger UI (Recomendado)

```
🌐 http://localhost:8000/api/v1/docs/
```

Características:
- ✅ Exploración interactiva de endpoints
- ✅ Prueba directa de requests
- ✅ Documentación automática de parámetros
- ✅ Ejemplos de request/response
- ✅ Validación de schemas

### ReDoc (Alternativa)

```
🌐 http://localhost:8000/api/v1/redoc/
```

### Esquema OpenAPI (JSON)

```
🌐 http://localhost:8000/api/v1/schema/
```

---

**Última actualización:** 21 de mayo de 2026  
**Total de endpoints:** 70+  
**Versión de API:** v1  
**Autenticación:** JWT
