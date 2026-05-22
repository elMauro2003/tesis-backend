# Backend para Sistema de Gestión de Residencia Estudiantil

**Título:** Backend para Sistema de Gestión de Residencia Estudiantil  
**Autor:** Mauricio Jesús Avalo Tamayo  
**Tutor:** MSc. Enrique Osvaldo Pérez Riverón  
**Tutor Consultante:** Lic. Juan Manuel Castellón Ruiz  
**Fecha:** Febrero, 2026  
**Institución:** Universidad Central "Marta Abreu" de Las Villas (UCLV)

---

## Resumen

La gestión de residencias estudiantiles en la UCLV enfrenta limitaciones críticas por la ausencia de un sistema centralizado. Los procesos de asignación de cuartos, programación de cuartelerías, atención a quejas y control disciplinario se hacen de forma manual y con herramientas ofimáticas desarticuladas, generando ineficiencias, errores, falta de trazabilidad y vulnerabilidades de seguridad.

Este trabajo diseña e implementa el **backend** de un sistema de gestión de residencias bajo una **arquitectura completamente desacoplada**: el backend es el núcleo independiente, responsable del modelado del dominio, encapsulamiento de reglas de negocio, integridad de datos, y exposición de funcionalidades via **API RESTful segura, escalable y documentada**.

---

## 1. Contexto Institucional

- La UCLV es el centro de educación superior más importante de la región central de Cuba.
- Tiene más de **7.774 estudiantes nacionales** y **156 extranjeros**, distribuidos en 12 facultades.
- Posee la mayor matrícula de estudiantes becados del país.
- Cuenta con **22 edificios** de residencias estudiantiles distribuidos en 3 sedes: **Central, Pedagógico y Fajardo**.
- La **Dirección de Becas y Residencias Estudiantiles** gestiona el alojamiento, alimentación y bienestar de los becados.

---

## 2. Problema de Investigación

El modelo actual de gestión es descentralizado y manual:
- Documentos físicos y hojas de cálculo no consolidadas.
- Imposibilidad de responder consultas básicas en tiempo real.
- Sin reglas de negocio formalizadas para asignación de cuartos/cuartelerías.
- Datos sensibles en archivos planos compartidos sin control de acceso ni auditoría.
- Intentos previos fragmentados: soluciones propietarias costosas o desarrollos monolíticos locales sin posibilidad de integración institucional.

**La necesidad real no es solo una aplicación web, sino una plataforma backend centralizada** que garantice integridad, seguridad y disponibilidad de los datos como eje integrador de la gestión residencial.

---

## 3. Objetivos

### Objetivo General
Desarrollar el backend de la plataforma usando Django REST Framework, garantizando integridad y seguridad de los datos, lógica de negocio, y exponiendo una **API RESTful documentada** para consumo por un frontend independiente.

### Objetivos Específicos
1. Caracterizar las tecnologías seleccionadas para el diseño e implementación del backend.
2. Desarrollar mediante métodos de ingeniería de software un prototipo inicial del backend.
3. Validar la calidad del backend mediante pruebas unitarias, de integración, de carga y de seguridad.

### Preguntas de Investigación
- ¿Qué diseño de BD relacional representa fielmente las entidades del dominio (edificios, alas, cuartos, estudiantes, cuartelerías, quejas, roles) garantizando normalización, integridad referencial y eficiencia en consultas?
- ¿Cómo implementar autenticación y autorización basada en JWT y roles (RBAC) garantizando acceso mínimo por perfil?
- ¿Cómo validar que el backend cumple los estándares de calidad en funcionalidad, rendimiento bajo carga y seguridad?

---

## 4. Stack Tecnológico Seleccionado

| Tecnología | Rol |
|---|---|
| **Python / Django REST Framework** | Framework backend principal |
| **PostgreSQL** | Base de datos relacional |
| **djangorestframework-simplejwt** | Autenticación JWT |
| **drf-spectacular** | Documentación OpenAPI 3.0 / Swagger |
| **django-axes** | Rate limiting y bloqueo de cuentas |
| **django-cors-headers** | Gestión de CORS |
| **django-filter** | Filtrado avanzado en endpoints |
| **Docker / Docker Compose** | Contenerización y orquestación |
| **Dokploy** | PaaS self-hosted para CI/CD y despliegue |
| **GitHub + GitHub Actions** | Control de versiones y CI/CD |
| **Postman / Newman** | Testing y documentación de API |
| **Visual Studio Code** | Editor principal |

### Justificación: ¿Por qué Django REST Framework?

1. **Adecuación al tamaño del proyecto:** no requiere microservicios ni ultra-alta concurrencia; DRF tiene el nivel de abstracción justo.
2. **Productividad:** principio "batteries included", serializadores que reducen boilerplate, ViewSets + Routers con generación automática de rutas CRUD.
3. **ORM robusto:** manejo eficiente de jerarquías profundas con `ForeignKey`, `ManyToManyField`, `select_related` y `prefetch_related` para evitar el problema N+1.
4. **Seguridad por defecto:** protección integrada contra OWASP Top 10 (SQL Injection, XSS, CSRF, Clickjacking).
5. **Contexto institucional:** Python es ampliamente adoptado en la UCLV; facilita transferencia tecnológica y mantenimiento futuro.
6. **Madurez:** 15+ años de desarrollo continuo; usado en producción por Instagram, Pinterest, Mozilla.

---

## 5. Procesos de Negocio Automatizados

| Área | Proceso Objeto de Automatización |
|---|---|
| Administración de Estudiantes | Gestión integral de la matrícula: centralización y actualización de datos del becado |
| Gestión de Infraestructura | Asignación, reasignación y control en tiempo real de ocupación de cuartos y edificios |
| Seguimiento y Control | Trazabilidad de quejas y evaluaciones: flujos de respuesta predefinidos y seguimiento estructurado |

### Problemas del esquema actual
- **Inconsistencia y duplicidad de datos** (datos de salud y disciplinarios gestionados manualmente).
- **Deficiente toma de decisiones:** información no disponible de forma agregada ni en tiempo real.
- **Falta de trazabilidad:** las quejas no tienen mecanismo formal de estado, visibilidad ni respuesta.

---

## 6. Arquitectura del Backend

### Patrón: Arquitectura en Capas (MVC adaptado a DRF)

| Capa | Responsabilidad |
|---|---|
| **Modelos (Datos)** | Entidades del dominio, relaciones, validaciones a nivel de modelo, métodos de negocio. Implementado con Django ORM. |
| **Serializadores** | Conversión modelos ↔ JSON, validación de datos de entrada/salida, manejo de relaciones anidadas. |
| **Vistas / ViewSets** | Procesamiento de solicitudes HTTP, lógica de negocio, respuestas. Con QuerySets optimizados via `select_related` y `prefetch_related`. |
| **URLs (Enrutamiento)** | Mapeo de URLs a ViewSets. DRF Routers generan automáticamente rutas CRUD estándar. |
| **Middleware** | Funcionalidades globales: autenticación, CORS, logging, compresión. |

### Principios SOLID aplicados

- **S (SRP):** cada modelo, serializador o viewset tiene una única responsabilidad.
- **O (OCP):** extensión mediante mixins y herencia sin modificar código existente.
- **L (LSP):** permisos personalizados heredan de `BasePermission` e intercambiables.
- **I (ISP):** DRF separa interfaces en mixins (`ListModelMixin`, `CreateModelMixin`, etc.).
- **D (DIP):** dependencias inyectadas mediante el sistema de clases de DRF.

### Ventajas de la arquitectura desacoplada

- **Desacoplamiento total:** el backend no conoce ni depende del frontend; puede consumirse por web, móvil, IoT.
- **Escalabilidad horizontal:** stateless (JWT), cualquier instancia puede manejar cualquier solicitud.
- **Mantenibilidad:** separación en capas facilita localización de errores y nuevas funcionalidades.
- **Reutilización:** mismos endpoints para panel administrativo, app móvil, quioscos, etc.
- **Estandarización:** DRF promueve buenas prácticas REST con API consistente.

---

## 7. Modelo de Datos

### Dominios del Modelo

#### Dominio Académico-Administrativo

| Entidad (tabla) | Descripción | Relaciones clave |
|---|---|---|
| `faculties` | Unidades organizativas de nivel superior | 1:N con `careers`; 1:1 con `deans` |
| `careers` | Programas académicos | N:1 con `faculties`; 1:N con `career_years` |
| `career_years` | Niveles dentro de una carrera (1er a 5to año) | N:1 con `careers`; 1:N con `groups`; 1:1 con `year_lead_professors` |
| `groups` | Unidad básica de organización estudiantil | N:1 con `career_years`; 1:N con `students`; 1:1 con `group_advisors` |

#### Dominio de Infraestructura

| Entidad (tabla) | Descripción | Relaciones clave |
|---|---|---|
| `sites` (sedes) | Complejos residenciales que agrupan edificios | 1:N con `buildings` |
| `buildings` (edificios) | Edificios de la residencia estudiantil | N:1 con `sites`; 1:N con `wings`; 1:N con `complaints` |
| `wings` (alas) | Subdivisiones dentro de edificios (Ala A, B, C) | N:1 con `buildings`; 1:N con `rooms`; 1:1 con `wing_supervisors` |
| `rooms` (cuartos) | Unidad física de alojamiento con capacidad máxima | N:1 con `wings`; 1:N con `assignments`; 1:N con `cleaning_schedules` |

#### Dominio de Actores (con herencia multi-tabla)

> **Estrategia de herencia seleccionada:** herencia multi-tabla via `OneToOneField`.  
> - Herencia abstracta: descartada (impide consultar todos los usuarios desde una sola tabla para autenticación).  
> - Herencia proxy: descartada (los subtipos tienen campos propios que requieren tablas independientes).  
> - **Multi-tabla (seleccionada):** permite consultar `User` para autenticación y mantener atributos específicos en tablas separadas, garantizando normalización y consultas eficientes con `select_related`.

| Entidad (tabla) | Descripción | Relaciones clave |
|---|---|---|
| `users` | Entidad base del sistema de autenticación de Django | 1:1 con `students`; 1:1 con `professors` |
| `students` | Estudiantes becados residentes | 1:1 con `users`; N:1 con `groups`; 1:N con `complaints`, `evaluations`, `cleaning_schedules`, `assignments` |
| `professors` | Supertipo para todos los roles de profesorado | 1:1 con `users`; 1:1 con `deans`, `group_advisors`, `year_lead_professors`, `wing_supervisors` |
| `deans` | Decanos: supervisan una facultad | 1:1 con `professors`; 1:1 con `faculties` |
| `group_advisors` | Profesores guías: asesoran un grupo | 1:1 con `professors`; 1:1 con `groups` |
| `year_lead_professors` | Profesores principales de año (PPA) | 1:1 con `professors`; 1:1 con `career_years` |
| `wing_supervisors` | Responsables de ala (instructores de beca) | 1:1 con `professors`; 1:1 con `wings` |

#### Dominio de Procesos Operativos

| Entidad (tabla) | Descripción | Relaciones clave |
|---|---|---|
| `complaints` | Quejas/reclamaciones de estudiantes con ciclo de vida | N:1 con `students`; N:1 con `buildings` (opcional) |
| `evaluations` | Evaluaciones periódicas de disciplina y comportamiento | N:1 con `students`; N:1 con `users` (instructor que crea) |
| `cleaning_schedules` | Cuartelerías: asignación de tareas de limpieza | N:1 con `students`; N:1 con `rooms` |
| `assignments` | Histórico completo de asignaciones de cuartos. `released_date IS NULL` = asignación activa | N:1 con `students`; N:1 con `rooms`; N:1 con `users` |
| `information` | Noticias, avisos y comunicados para estudiantes | N:1 con `users` (directivo/comunicador) |
| `reports` | Reportes generados por directivos con parámetros y referencia a archivo | N:1 con `users` |

> **Nota de integridad:** se usa `assignments` como **única fuente de verdad** para asignaciones activas, eliminando redundancia de `students.room_id`. Se implementa un **índice parcial** para garantizar una única asignación activa por estudiante, y **triggers** para sincronizar `rooms.current_occupancy` y aplicar el límite diario de quejas.

---

## 8. API RESTful

### Principios REST aplicados (constraints de Fielding)

1. **Cliente-Servidor:** separación clara entre frontend y backend.
2. **Stateless:** el servidor no almacena estado de sesión; ni access ni refresh tokens se almacenan en servidor.
3. **Cacheable:** respuestas indican explícitamente si pueden cachearse.
4. **Interfaz uniforme:** recursos por URLs, representaciones JSON estándar.
5. **Sistema en capas:** el cliente no sabe si se comunica con el servidor directamente o con intermediarios.

### Convenciones de URLs

- **Versionado:** `/api/v1/` (v2 para cambios incompatibles).
- **Recursos en plural:** `/estudiantes/`, `/quejas/`, `/evaluaciones/`.
- **Anidamiento solo por pertenencia estricta:** `/estudiantes/{id}/quejas/`.
- **Acciones personalizadas con verbos:** `/quejas/{id}/responder/` (POST), `/asignaciones/{id}/liberar/` (POST).

### Formato de respuestas

**Éxito:**
```json
{
  "data": { "..." },
  "message": "Operación exitosa"
}
```

**Error:**
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Los datos proporcionados no son válidos",
    "details": {
      "field_name": ["Este campo es obligatorio.", "Debe tener al menos 3 caracteres."]
    }
  }
}
```

**Paginación:**
```json
{
  "count": 150,
  "next": "http://api.example.com/api/v1/estudiantes/?page=3",
  "previous": "http://api.example.com/api/v1/estudiantes/?page=1",
  "results": ["..."]
}
```

- Paginación por defecto: 20 elementos/página. Personalizable con `page` y `page_size`.
- Filtrado: `/api/v1/estudiantes/?facultad=5&year=3`
- Búsqueda: `/api/v1/estudiantes/?search=Juan`

---

## 9. Requisitos Funcionales (Endpoints)

| ID | Endpoint | Método | Actor Autorizado |
|---|---|---|---|
| RF-1 | `/api/v1/estudiantes/` | POST | Instructor de beca |
| RF-2 | `/api/v1/estudiantes/` | GET | Instructor de beca |
| RF-3 | `/api/v1/estudiantes/{id}/` | GET | Instructor de beca |
| RF-4 | `/api/v1/estudiantes/{id}/` | PUT | Instructor de beca |
| RF-5 | `/api/v1/estudiantes/{id}/` | PATCH | Instructor de beca |
| RF-6 | `/api/v1/estudiantes/{id}/` | DELETE | Instructor de beca |
| RF-7 | `/api/v1/estudiantes/?search=...` | GET | Instructor de beca |
| RF-8 | `/api/v1/evaluaciones/` | POST | Instructor de beca |
| RF-9 | `/api/v1/evaluaciones/` | GET | Instructor de beca |
| RF-10 | `/api/v1/evaluaciones/{id}/` | GET | Instructor de beca |
| RF-11 | `/api/v1/evaluaciones/{id}/` | PATCH | Instructor de beca |
| RF-12 | `/api/v1/evaluaciones/{id}/` | DELETE | Instructor de beca |
| RF-13 | `/api/v1/evaluaciones/mis-evaluaciones/` | GET | Estudiante |
| RF-14 | `/api/v1/quejas/` | POST | Estudiante |
| RF-15 | `/api/v1/quejas/mis-quejas/` | GET | Estudiante |
| RF-16 | `/api/v1/quejas/{id}/` | GET | Estudiante |
| RF-17 | `/api/v1/quejas/{id}/` | PATCH | Estudiante |
| RF-18 | `/api/v1/quejas/{id}/` | DELETE | Estudiante |
| RF-19 | `/api/v1/quejas/visibles/` | GET | Estudiante |
| RF-20 | `/api/v1/quejas/` | GET | Subdirector administrativo |
| RF-21 | `/api/v1/quejas/{id}/` | GET | Subdirector administrativo |
| RF-22 | `/api/v1/quejas/{id}/estado/` | PATCH | Subdirector administrativo |
| RF-23 | `/api/v1/quejas/{id}/respuesta/` | POST | Subdirector administrativo |
| RF-24 | `/api/v1/quejas/{id}/visibilidad/` | PATCH | Subdirector administrativo |
| RF-25 | `/api/v1/sedes/` | POST | Directivo de beca |
| RF-26 | `/api/v1/sedes/` | GET | Directivo de beca |
| RF-27 | `/api/v1/sedes/{id}/` | GET | Directivo de beca |
| RF-28 | `/api/v1/sedes/{id}/` | PATCH | Directivo de beca |
| RF-29 | `/api/v1/sedes/{id}/` | DELETE | Directivo de beca |
| RF-30 | `/api/v1/edificios/` | POST | Directivo de beca |
| RF-31 | `/api/v1/edificios/` | GET | Directivo de beca |
| RF-32 | `/api/v1/edificios/{id}/` | GET | Directivo de beca |
| RF-33 | `/api/v1/edificios/{id}/` | PATCH | Directivo de beca |
| RF-34 | `/api/v1/edificios/{id}/` | DELETE | Directivo de beca |
| RF-35 | `/api/v1/alas/` | POST | Directivo de beca |
| RF-36 | `/api/v1/alas/` | GET | Directivo de beca |
| RF-37 | `/api/v1/alas/{id}/` | GET | Directivo de beca |
| RF-38 | `/api/v1/alas/{id}/` | PATCH | Directivo de beca |
| RF-39 | `/api/v1/alas/{id}/` | DELETE | Directivo de beca |
| RF-40 | `/api/v1/cuartos/` | POST | Directivo de beca |
| RF-41 | `/api/v1/cuartos/` | GET | Directivo de beca |
| RF-42 | `/api/v1/cuartos/{id}/` | GET | Directivo de beca |
| RF-43 | `/api/v1/cuartos/{id}/` | PATCH | Directivo de beca |
| RF-44 | `/api/v1/cuartos/{id}/` | DELETE | Directivo de beca |
| RF-45 | `/api/v1/asignaciones/` | POST | Instructor / Directivo |
| RF-46 | `/api/v1/asignaciones/activas/` | GET | Instructor / Directivo |
| RF-47 | `/api/v1/asignaciones/` | GET | Instructor / Directivo |
| RF-48 | `/api/v1/asignaciones/{id}/` | GET | Instructor / Directivo |
| RF-49 | `/api/v1/asignaciones/{id}/liberar/` | POST | Instructor / Directivo |
| RF-50 | `/api/v1/informaciones/` | POST | Comunicador / Directivo |
| RF-51 | `/api/v1/informaciones/` | GET | Comunicador / Directivo |
| RF-52 | `/api/v1/informaciones/{id}/` | GET | Comunicador / Directivo |
| RF-53 | `/api/v1/informaciones/{id}/` | PATCH | Comunicador / Directivo |
| RF-54 | `/api/v1/informaciones/{id}/` | DELETE | Comunicador / Directivo |
| RF-55 | `/api/v1/informaciones/publicas/` | GET | Estudiante |
| RF-56 | `/api/v1/reportes/solicitar/` | POST | Directivo de beca |
| RF-57 | `/api/v1/reportes/{id}/` | GET | Directivo de beca |
| RF-58 | `/api/v1/reportes/` | GET | Directivo de beca |
| RF-59 | `/api/v1/auth/login/` | POST | Todos (no autenticado) |
| RF-60 | `/api/v1/auth/refresh/` | POST | Todos (autenticado) |
| RF-61 | `/api/v1/auth/logout/` | POST | Todos (autenticado) |
| RF-62 | `/api/v1/auth/cambiar-contraseña/` | POST | Todos (autenticado) |
| RF-63 | `/api/v1/roles/` | GET | Administrador |
| RF-64 | `/api/v1/usuarios/{id}/roles/` | POST | Administrador |
| RF-65 | `/api/v1/usuarios/{id}/roles/{rol_id}/` | DELETE | Administrador |
| RF-66 | `/api/v1/usuarios/{id}/permisos/` | GET | Administrador |
| RF-67 | `/api/v1/cuartelerias/` | POST | Responsable de ala |
| RF-68 | `/api/v1/cuartelerias/?ala={id}` | GET | Responsable de ala |
| RF-69 | `/api/v1/cuartelerias/mis-cuartelerias/` | GET | Estudiante |
| RF-70 | `/api/v1/cuartelerias/{id}/completar/` | PATCH | Responsable de ala |

---

## 10. Requisitos No Funcionales

| ID | Categoría | Requisito | Métrica/Criterio |
|---|---|---|---|
| RNF-1 | Rendimiento | Tiempo de respuesta endpoints críticos | < 500 ms para el 95% de solicitudes en condiciones normales |
| RNF-2 | Rendimiento | Tiempo de respuesta bajo carga | < 2 s para el 95% con 500 usuarios concurrentes |
| RNF-3 | Rendimiento | Disponibilidad | 99% (máx. ≈ 87.6 horas/año de inactividad) |
| RNF-4 | Seguridad | Autenticación JWT | Access token: 15 min / Refresh token: 7 días |
| RNF-5 | Seguridad | Autorización | RBAC (Control de acceso basado en roles) |
| RNF-6 | Seguridad | Protección ataques | Mitigación OWASP Top 10: SQL Injection, XSS, CSRF, BOLA |
| RNF-7 | Seguridad | Rate limiting | Bloqueo temporal tras 5 intentos fallidos en 15 minutos |
| RNF-8 | Escalabilidad | Capacidad | Soporte 5.000+ usuarios y 20.000+ registros sin degradación |
| RNF-9 | Escalabilidad | Concurrencia | 500 solicitudes simultáneas sin errores |
| RNF-10 | Mantenibilidad | Cobertura de pruebas | > 80% en módulos críticos (autenticación, quejas, estudiantes) |
| RNF-11 | Mantenibilidad | Documentación | OpenAPI 3.0 en `/api/v1/docs/` |
| RNF-12 | Mantenibilidad | Código | PEP 8, nombres descriptivos, comentarios en español o inglés |
| RNF-13 | Usabilidad | Interfaz API | Respuestas consistentes, mensajes de error claros, códigos HTTP correctos |
| RNF-14 | Compatibilidad | Browsable API | Chrome, Firefox, Edge, Safari |
| RNF-15 | Compatibilidad | Formatos | JSON (UTF-8), soporte opcional XML |
| RNF-16 | Portabilidad | Contenedores | Dockerizado con Docker Compose para desarrollo y producción |

---

## 11. Autenticación y Autorización

### 11.1 Flujo JWT (`djangorestframework-simplejwt`)

1. Cliente envía credenciales a `POST /api/v1/auth/login/`.
2. Servidor retorna:
   - **Access token:** duración 15 min, se envía en cada request (`Authorization: Bearer <token>`).
   - **Refresh token:** duración 7 días, se usa para obtener nuevos access tokens.
3. Refresh: `POST /api/v1/auth/refresh/` con el refresh token.
4. Logout: `POST /api/v1/auth/logout/` — client-side (el backend no mantiene estado).

#### Configuración `settings.py`

```python
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=15),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': False,       # Stateless: no blacklist en BD
    'BLACKLIST_AFTER_ROTATION': False,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
}
```

> **Decisión de diseño:** `ROTATE_REFRESH_TOKENS: False` se desactiva deliberadamente para mantener coherencia con el principio stateless. La rotación automática exige blacklist en BD, introduciendo estado en servidor y eliminando escalabilidad horizontal. El riesgo (refresh comprometido válido 7 días) se mitiga con: (1) access token de 15 min, (2) HTTPS obligatorio, (3) bloqueo por intentos fallidos (RNF-7).

### 11.2 Roles del Sistema (RBAC)

Cada rol corresponde a un `Group` de Django. Los permisos se asignan a grupos y los usuarios los heredan.

| Rol | Descripción | Permisos clave |
|---|---|---|
| `estudiante` | Estudiante becado | CRUD propias quejas, consultar evaluaciones propias, ver informaciones públicas |
| `instructor` | Instructor de beca | CRUD estudiantes, evaluaciones, asignación de cuartos |
| `directivo` | Directivo de beca | CRUD sedes, edificios, cuartos, reportes, supervisión digital |
| `subdirector` | Subdirector administrativo | Revisar quejas, cambiar estado, controlar visibilidad, responder |
| `comunicador` | Comunicador | CRUD informaciones |
| `decano` | Decano de facultad | Consultar estudiantes de su facultad |
| `ppa` | Profesor principal de año | Consultar estudiantes de su año |
| `pg` | Profesor guía | Consultar estudiantes de su grupo |
| `admin` | Administrador del sistema | Gestión de roles y usuarios |

### 11.3 Permisos a Nivel de Objeto (BOLA mitigation)

```python
# Patrón 1: Propiedad directa (el recurso tiene un campo 'user')
class IsOwnerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return hasattr(obj, 'user') and obj.user == request.user

# Patrón 2: Propiedad a través de estudiante (quejas, evaluaciones)
class IsStudentOwnerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return hasattr(obj, 'student') and obj.student.user == request.user

# Patrón 3: Propiedad a través de instructor (asignaciones)
class IsAssignedByOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return hasattr(obj, 'assigned_by') and obj.assigned_by == request.user
```

| ViewSet | Permiso aplicado |
|---|---|
| `ComplaintViewSet` | `IsStudentOwnerOrReadOnly` |
| `EvaluationViewSet` | `IsStudentOwnerOrReadOnly` (GET) + permisos de rol (escritura) |
| `AssignmentViewSet` | `IsAssignedByOrReadOnly` |
| `StudentViewSet` | Permisos basados en rol (instructor/directivo) |

### 11.4 Rate Limiting (`django-axes`)

```python
# Instalación
# pip install django-axes

# settings.py
INSTALLED_APPS = [..., 'axes']

AUTHENTICATION_BACKENDS = [
    'axes.backends.AxesStandaloneBackend',
    'django.contrib.auth.backends.ModelBackend',
]

MIDDLEWARE = [
    ...,
    'axes.middleware.AxesMiddleware',  # debe ir después de SessionMiddleware
]

AXES_FAILURE_LIMIT = 5           # intentos fallidos antes del bloqueo
AXES_COOLOFF_TIME = 0.25         # bloqueo 15 minutos (en horas: 15/60)
AXES_LOCKOUT_PARAMETERS = ['ip_address']  # bloquear por IP
AXES_RESET_ON_SUCCESS = True     # resetear contador al login exitoso
```

> **Nota:** django-axes usa la misma BD PostgreSQL del sistema, sin requerir Redis ni diseño manual de tablas auxiliares, manteniendo el stack mínimo apropiado.

### 11.5 Validaciones de Negocio (en Serializadores)

- **Límite diario de quejas:** verificado en `validate()` del serializador de quejas.
- **Estudiante no duplicado:** validación de CI único en serializador de estudiantes.
- **Disponibilidad de cuarto:** verificada en la lógica de asignación.
- **Visibilidad de quejas:** solo estudiantes ven quejas marcadas como visibles.

---

## 12. Documentación de la API (OpenAPI 3.0)

### Herramienta: `drf-spectacular`

```python
# pip install drf-spectacular

# settings.py
INSTALLED_APPS = [..., 'drf_spectacular']

REST_FRAMEWORK = {
    ...,
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'API de Gestión de Residencias Estudiantiles UCLV',
    'DESCRIPTION': 'Backend para el sistema de gestión de residencias estudiantiles',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}
```

```python
# urls.py
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    ...,
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]
```

### URLs de documentación

- **Swagger UI (interactiva):** `https://api.uclv.edu.cu/api/docs/`
- **Esquema OpenAPI (JSON):** `https://api.uclv.edu.cu/api/schema/`
- **Colección Postman:** exportada y compartida con equipo de frontend.

### Anotación de endpoints

```python
from drf_spectacular.utils import extend_schema, OpenApiParameter

@extend_schema(
    summary="Listar estudiantes",
    description="Retorna lista paginada de estudiantes. Requiere permisos de instructor o directivo.",
    parameters=[
        OpenApiParameter(name='search', description='Búsqueda por nombre o CI', required=False, type=str),
        OpenApiParameter(name='facultad', description='Filtrar por ID de facultad', required=False, type=int),
    ],
    responses={200: StudentSerializer(many=True), 401: "No autenticado", 403: "No autorizado"}
)
```

---

## 13. Metodología: Scrum + XP

### Roles adaptados (equipo unipersonal)

| Rol Scrum | Adaptación |
|---|---|
| Product Owner | Tutor académico (Enrique Osvaldo Pérez Riverón) |
| Scrum Master | Autor (Mauricio Avalo Tamayo) — auto-gestión |
| Development Team | Autor (Mauricio Avalo Tamayo) — implementación completa |

### Eventos Scrum

| Evento | Frecuencia | Descripción |
|---|---|---|
| Sprint Planning | Al inicio de cada Sprint (2 h) | Objetivo del Sprint y selección de Product Backlog ítems |
| Daily Scrum | Diario (15 min) | Auto-seguimiento: ¿qué hice? ¿qué haré? ¿impedimentos? |
| Sprint Review | Al final de cada Sprint (1 h) | Demo al tutor para validación y retroalimentación |
| Sprint Retrospective | Al final de cada Sprint (30 min) | Análisis de mejoras para el siguiente Sprint |

### Plan de Sprints (6 sprints × 2 semanas = 12 semanas)

| Sprint | Semanas | Objetivo | Entregables clave |
|---|---|---|---|
| Sprint 1 | 1-2 | Fundación y Autenticación | Proyecto configurado, conexión PostgreSQL, endpoints JWT (login, refresh, logout) |
| Sprint 2 | 3-4 | Modelado completo y Estudiantes | Modelo completo con migraciones, triggers, CRUD estudiantes con permisos |
| Sprint 3 | 5-6 | Quejas y Evaluaciones | CRUD evaluaciones (instructor), CRUD quejas (estudiante), revisión quejas (subdirector), permisos a nivel objeto |
| Sprint 4 | 7-8 | Infraestructura y Asignaciones | CRUD edificios/alas/cuartos, asignación/liberación cuartos, validaciones de disponibilidad |
| Sprint 5 | 9-10 | Informaciones y Reportes | CRUD informaciones, endpoint reportes PDF, documentación OpenAPI en `/api/docs/` |
| Sprint 6 | 11-12 | Roles, Permisos y Estabilización | Gestión de roles/permisos (admin), cobertura > 80%, dockerización |

### Prácticas XP aplicadas

| Práctica | Aplicación |
|---|---|
| **TDD** | Se escriben pruebas (unitarias y de integración) antes que el código; se ejecutan localmente y en CI |
| **Continuous Integration** | GitHub Actions ejecuta todas las pruebas automáticamente en cada push a `develop` y `main` |
| **Refactoring** | Mejora continua sin alterar comportamiento externo; especialmente en optimización de QuerySets |
| **Coding Standards** | PEP 8 + convenciones DRF; `flake8` y `black` para automatizar cumplimiento |
| **Collective Code Ownership** | Código completamente documentado (docstrings, comentarios, README) para contribuciones futuras |
| **Simple Design** | Se implementa solo lo necesario; sin sobreingeniería anticipada |
| **Small Releases** | Cada sprint termina con un incremento funcional desplegable |

### Product Backlog Inicial (priorizado)

| ID | Historia / Tarea | Prioridad | Est. (días) | Dependencias |
|---|---|---|---|---|
| HU-1 | Autenticación JWT | Alta | 3 | — |
| HU-2 | CRUD Estudiantes (instructor) | Alta | 5 | HU-1 |
| HU-3 | CRUD Evaluaciones (instructor) | Alta | 4 | HU-1, HU-2 |
| HU-4 | CRUD Quejas propias (estudiante) | Alta | 4 | HU-1 |
| HU-5 | Revisión y respuesta de quejas (subdirector) | Alta | 3 | HU-4 |
| HU-6 | CRUD Infraestructura (directivo) | Media | 5 | HU-1 |
| HU-7 | Asignación de cuartos (instructor) | Media | 4 | HU-2, HU-6 |
| HU-8 | Quejas visibles (estudiante) | Media | 2 | HU-4, HU-5 |
| HU-9 | CRUD Informaciones (comunicador) | Media | 3 | HU-1 |
| HU-10 | Generación de reportes PDF (directivo) | Baja | 4 | HU-2, HU-3, HU-4 |
| HU-11 | Gestión de roles y permisos (admin) | Baja | 3 | HU-1 |
| TT-1 | Configurar proyecto Django + PostgreSQL | Técnica | 1 | — |
| TT-2 | Modelo de datos completo con migraciones | Técnica | 3 | TT-1 |
| TT-3 | Configurar JWT (simplejwt) | Técnica | 1 | TT-1 |
| TT-4 | Triggers en PostgreSQL | Técnica | 2 | TT-2 |
| TT-5 | Permisos personalizados | Técnica | 2 | TT-3 |
| TT-6 | Configurar documentación OpenAPI | Técnica | 1 | TT-1 |
| TT-7 | Pruebas unitarias y de integración | Técnica | 4 | TT-1 |
| TT-8 | Dockerizar la aplicación | Técnica | 1 | TT-1 |

---

## 14. Estrategia de Branching (Git Flow)

| Rama | Propósito |
|---|---|
| `main` | Código listo para producción |
| `develop` | Integración de características |
| `feature/*` | Una rama por funcionalidad/historia de usuario |
| `release/*` | Preparación de releases |
| `hotfix/*` | Correcciones urgentes en producción |

---

## 15. Herramientas del Proyecto

### Visual Studio Code
- Extensiones Python y Pylance para autocompletado, análisis estático y refactorización.
- Terminal integrada para migraciones, servidor de desarrollo, comandos Django.
- Depurador visual con breakpoints e inspección de variables.
- Extensión oficial de Docker para gestión de contenedores.

### Postman / Newman
- Cliente RESTful para probar todos los endpoints durante desarrollo.
- Colecciones organizadas por módulo con variables de entorno (dev/staging/prod).
- **Newman:** ejecutor CLI para integrar pruebas de API en pipelines CI/CD.

### Docker / Docker Compose
- Cada contenedor: espacio aislado con su propio filesystem, red y procesos.
- Docker Compose define y ejecuta aplicaciones multi-contenedor (backend + PostgreSQL).
- Elimina el problema "en mi máquina funciona".
- Facilita incorporación del equipo de frontend para correr el backend localmente.

### Dokploy
- PaaS self-hosted, alternativa a Vercel/Heroku con control total de infraestructura.
- CI/CD desde GitHub/GitLab/Bitbucket.
- Integración automática con Traefik como proxy inverso y balanceador de carga.
- Soporte nativo para multi-servidor y Docker Swarm.

### PostgreSQL
- Cumplimiento ACID completo.
- Integridad referencial real (FK, CHECK, UNIQUE, EXCLUSION, triggers).
- JSONB para datos semiestructurados (indexable, eficiente).
- MVCC para alta concurrencia sin bloqueos innecesarios.
- Extensiones: `pgcrypto` (cifrado de campos sensibles como CI), `pg_stat_statements`.
- **Sobre MySQL:** integridad referencial más estricta, JSONB superior, mejor MVCC, ecosistema de extensiones más rico.

---

## 16. Comparativas de Tecnologías

### Frameworks Backend

| Lenguaje | Python | PHP | TypeScript | Java |
|---|---|---|---|---|
| Curva de Aprendizaje | Baja | Baja | Media-Alta | Alta |
| ORM Integrado | Sí (Django ORM) | Sí (Eloquent) | No (TypeORM/Prisma) | Sí (Spring Data JPA) |
| Tiempo de desarrollo | Rápido | Rápido | Medio | Lento (verboso) |
| Rendimiento en APIs | Bueno | Moderado | Muy Bueno (Async) | Excelente |
| Seguridad por defecto | Excelente | Buena | Buena | Excelente |
| Madurez del ecosistema | Alta | Alta | Media | Muy alta |
| Consumo de recursos | Bajo | Bajo | Medio | Alto |
| Experiencia equipo UCLV | Alta | Media | Baja | Baja |

### Metodologías

| Criterio | RUP | Scrum | XP |
|---|---|---|---|
| Enfoque | Proceso unificado | Gestión de proyectos | Excelencia técnica |
| Tamaño de equipo ideal | Mediano-Grande | Pequeño-Mediano | Pequeño (2-12) |
| Documentación | Extensa | Mínima necesaria | Mínima necesaria |
| Adaptabilidad a cambios | Media | Alta | Muy alta |
| Prácticas de ingeniería | No prescribe | No prescribe | Prescribe (TDD, CI, Pair) |

**Seleccionada:** Scrum + prácticas XP. RUP descartado por exceso de artefactos documentales y sobre-dimensionamiento para el alcance del proyecto.

---

## 17. Seguridad

### Medidas implementadas

- **HTTPS obligatorio** en todos los endpoints.
- **JWT stateless** con access tokens de vida corta (15 min).
- **RBAC** con permisos a nivel de objeto (BOLA mitigation — OWASP API Top 10).
- **django-axes** para bloqueo temporal por intentos fallidos.
- **pgcrypto** para cifrado en reposo de campos sensibles (e.g., `ci`).
- **Enmascaramiento de datos** en respuestas API según rol del usuario.
- **Protecciones Django por defecto:** SQL Injection (ORM parametrizado), XSS (escapado automático), CSRF, Clickjacking.

### OWASP API Security Top 10 — mitigaciones directas

| Vulnerabilidad | Mitigación |
|---|---|
| BOLA (Broken Object Level Authorization) | Permisos personalizados `IsOwnerOrReadOnly`, `IsStudentOwnerOrReadOnly`, `IsAssignedByOrReadOnly` |
| Broken Authentication | JWT con expiración corta + HTTPS + bloqueo por intentos fallidos |
| Broken Object Property Level Authorization | Serializadores que controlan exactamente qué campos se exponen según el rol |
| SQL Injection | ORM parametrizado de Django |
| Security Misconfiguration | Configuración de seguridad por defecto de Django |

---

## 18. Notas de Implementación Importantes

1. **Problema N+1:** todos los ViewSets con relaciones anidadas usan `select_related` y `prefetch_related`. Especialmente crítico en el endpoint de listado de estudiantes, que atraviesa hasta 4 niveles: `estudiante → grupo → año académico → carrera`.

2. **Herencia multi-tabla:** se usa `OneToOneField` para la jerarquía `User → Student/Professor`. Consultar siempre con `select_related` para evitar queries extra.

3. **Asignaciones activas:** `released_date IS NULL` indica asignación activa. Existe un índice parcial que garantiza máximo una asignación activa por estudiante.

4. **Triggers PostgreSQL:**
   - Sincronización de `rooms.current_occupancy` al crear/liberar asignaciones.
   - Límite diario de quejas por estudiante.

5. **Logout es client-side:** el backend no mantiene blacklist de tokens. El cliente simplemente descarta los tokens al hacer logout.

6. **Cobertura de pruebas mínima:** > 80% en módulos críticos (autenticación, quejas, estudiantes).

7. **PEP 8 + `flake8` + `black`** para estandarización automática del código.

---

## 19. Referencias Tecnológicas

- Django: https://docs.djangoproject.com
- DRF: https://www.django-rest-framework.org
- PostgreSQL: https://www.postgresql.org/docs/
- OpenAPI 3.0: https://spec.openapis.org/oas/v3.0.3.html
- OWASP API Security: https://owasp.org/www-project-api-security/
- JWT RFC 7519: https://datatracker.ietf.org/doc/html/rfc7519
- Scrum Guide: https://scrumguides.org/docs/scrumguide/v2020/2020-Scrum-Guide-US.pdf
- Docker: https://docs.docker.com
- Spring Boot (referencia comparativa): https://docs.spring.io/spring-boot/docs/current/reference/html/
