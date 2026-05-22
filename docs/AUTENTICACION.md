# 🔐 Autenticación, Autorización y Seguridad

**Guía completa sobre JWT, RBAC (9 roles), permisos a nivel de objeto, y medidas de seguridad.**

---

## Tabla de Contenidos

1. [Flujo JWT](#flujo-jwt)
2. [Matriz de Roles y Permisos](#matriz-de-roles-y-permisos)
3. [Permisos a Nivel de Objeto (BOLA Mitigation)](#permisos-a-nivel-de-objeto)
4. [Rate Limiting](#rate-limiting)
5. [Seguridad OWASP](#seguridad-owasp)
6. [Ejemplos de Requests](#ejemplos-de-requests)

---

## Flujo JWT

### Lifetime de Tokens

```
┌─────────────────────────────────────────────┐
│  Usuario hace LOGIN                        │
│                                             │
│  POST /api/v1/auth/login/                  │
│  {                                          │
│    "username": "luis_garcia",              │
│    "password": "MiPassword123!"            │
│  }                                         │
└────────────┬────────────────────────────────┘
             ↓
┌─────────────────────────────────────────────┐
│  Servidor valida credenciales en BD        │
└────────────┬────────────────────────────────┘
             ↓
┌─────────────────────────────────────────────┐
│  Response 200 OK:                           │
│  {                                          │
│    "access": "eyJ0eXAi...",  ← 15 min      │
│    "refresh": "eyJ0eXAi...", ← 7 días     │
│    "user": {                                │
│      "id": 1,                              │
│      "username": "luis_garcia",            │
│      "roles": ["estudiante"]               │
│    }                                        │
│  }                                          │
└────────────┬────────────────────────────────┘
             ↓
  ┌──────────────────────────────────────────┐
  │  Access Token (15 minutos)                │
  │  ────────────────────────────────────────│
  │  • Se incluye en cada request:            │
  │    Authorization: Bearer <access_token>  │
  │  • Caduca en 15 min                      │
  │  • Para extender: usar refresh token    │
  │  • Contiene: user_id, roles, exp, iat   │
  └──────────────────────────────────────────┘
             ↓
  ┌──────────────────────────────────────────┐
  │  Refresh Token (7 días)                  │
  │  ────────────────────────────────────────│
  │  • Se almacena en cliente (localStorage) │
  │  • NO se envía en cada request           │
  │  • Solo para renovar access token       │
  │  • Caduca en 7 días                     │
  │  • POST /api/v1/auth/refresh/ → token  │
  └──────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│  Si access token EXPIRA (>15 min):          │
│                                             │
│  POST /api/v1/auth/refresh/                 │
│  {                                          │
│    "refresh": "eyJ0eXAi..."               │
│  }                                          │
│  ↓                                          │
│  Response 200:                              │
│  {                                          │
│    "access": "eyJ0eXAi..."  ← Nuevo       │
│  }                                          │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│  Si refresh token EXPIRA (>7 días):         │
│                                             │
│  → Usuario debe hacer LOGIN nuevamente     │
│  → No hay auto-refresh indefinido          │
│  → Razón: seguridad (limita compromiso)   │
└─────────────────────────────────────────────┘
```

### Configuración en Django

```python
# config/settings/base.py
from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=15),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': False,  # Stateless: no hay blacklist en BD
    'BLACKLIST_AFTER_ROTATION': False,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,  # ← Ultra-secreto en .env
    'AUTH_HEADER_TYPES': ('Bearer',),
}

# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}
```

### Logout (Client-Side)

```python
# El backend NO mantiene blacklist de tokens
# Logout es responsabilidad del cliente:

# Client:
localStorage.removeItem('access_token')
localStorage.removeItem('refresh_token')
// Token sigue siendo válido 15 minutos en servidor
// Pero cliente no puede usarlo (no tiene cópia)

# Ventaja: arquitectura stateless, escalable horizontalmente
# Si necesitamos revocación inmediata: agregar Redis blacklist (futuro)
```

---

## Matriz de Roles y Permisos

### 9 Roles del Sistema

| Rol | Descripción | Permisos |
|-----|-------------|----------|
| **estudiante** | Estudiante becado | Ver sus evaluaciones, presentar quejas, ver informaciones públicas, ver cuartelerías asignadas |
| **instructor** | Instructor de beca | CRUD estudiantes, CRUD evaluaciones, asignar cuartos, CRUD cuartelerías |
| **directivo** | Director de residencia | CRUD infraestructura, CRUD estudiantes, supervisión global, reportes |
| **subdirector** | Subdirector administrativo | Revisar quejas, cambiar estado, responder quejas, controlar visibilidad |
| **comunicador** | Comunicador/Publicista | CRUD informaciones/noticias |
| **decano** | Decano de facultad | Consultar estudiantes de su facultad (readonly) |
| **ppa** | Profesor Principal de Año | Consultar estudiantes de su año (readonly) |
| **pg** | Profesor Guía | Consultar estudiantes de su grupo (readonly) |
| **admin** | Administrador del sistema | Gestión total: roles, usuarios, permisos |

### Matriz CRUD Detallada

```
┌──────────────┬──────┬──────┬────────┬────────┬──────┬────────┬────────┬────────┬───────┐
│ Recurso      │ E    │ I    │ D      │ Subdir │ Comun│ Decano │ PPA    │ PG     │ Admin │
├──────────────┼──────┼──────┼────────┼────────┼──────┼────────┼────────┼────────┼───────┤
│ Estudiantes  │ R    │ CRUD │ CRUD   │ —      │ —    │ R*     │ R*     │ R*     │ CRUD  │
│ Evaluaciones │ R    │ CRUD │ —      │ —      │ —    │ —      │ —      │ —      │ CRUD  │
│ Quejas (crear)│CREATE│ —    │ —      │ —      │ —    │ —      │ —      │ —      │ —     │
│ Quejas (todas)│ R    │ —    │ —      │ CRUD   │ —    │ —      │ —      │ —      │ —     │
│ Cuartos      │ —    │ —    │ CRUD   │ —      │ —    │ —      │ —      │ —      │ CRUD  │
│ Asignaciones │ —    │ CRUD │ CRUD   │ —      │ —    │ —      │ —      │ —      │ CRUD  │
│ Informaciones│ R    │ —    │ —      │ —      │ CRUD │ R      │ R      │ R      │ CRUD  │
│ Reportes     │ —    │ —    │ CRUD   │ —      │ —    │ —      │ —      │ —      │ CRUD  │
├──────────────┼──────┼──────┼────────┼────────┼──────┼────────┼────────┼────────┼───────┤
│ Cuartelerías │ R*   │ CRUD │ —      │ —      │ —    │ —      │ —      │ —      │ CRUD  │
├──────────────┼──────┼──────┼────────┼────────┼──────┼────────┼────────┼────────┼───────┤

Leyenda:
R    = Read (GET)
CRUD = Create, Read, Update, Delete (POST, GET, PATCH, DELETE)
R*   = Read propio solo (ej: estudiante ve sus evaluaciones)
     = Sin acceso (—)

Explicaciones:
• Estudiante ve SOLO sus evaluaciones/quejas/cuartelerías (object-level permission)
• Directivo ve TODO (administrativo)
• Decano/PPA/PG son "read-only" para supervisión (sin modificar)
• Subdirector especializado en ciclo de vida de quejas
• Comunicador solo gestiona informaciones
```

### Cómo se Asignan Roles

```python
# Crear usuario con rol instructor
user = User.objects.create_user(
    username='carlos_martinez',
    email='carlos@uclv.cu',
    password='MiPassword123!'
)

# Obtener grupo 'instructor' (se crea con manage.py create_roles)
instructor_group = Group.objects.get(name='instructor')

# Asignar grupo al usuario (le da todos los permisos del grupo)
user.groups.add(instructor_group)

# Verificar que tiene el rol
print(user.groups.all())  # <QuerySet [<Group: instructor>]>

# O via management command:
# python manage.py assign_role carlos_martinez instructor
```

### Código de Clases RBAC

```python
# core/permissions.py
from rest_framework.permissions import BasePermission

def _user_has_role(user, *roles):
    """Helper: verifica si usuario tiene alguno de los roles."""
    if not user.is_authenticated:
        return False
    user_groups = user.groups.values_list('name', flat=True)
    return any(role in user_groups for role in roles)

class IsInstructor(BasePermission):
    def has_permission(self, request, view):
        return _user_has_role(request.user, 'instructor')

class IsDirectivo(BasePermission):
    def has_permission(self, request, view):
        return _user_has_role(request.user, 'directivo')

class IsSubdirector(BasePermission):
    def has_permission(self, request, view):
        return _user_has_role(request.user, 'subdirector')

# Uso en ViewSets:
class StudentViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated, IsInstructor]
    # Solo usuarios instructor pueden acceder

class ComplaintViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    
    def get_permissions(self):
        if self.action in ['respuesta', 'estado', 'visibilidad']:
            return [IsAuthenticated(), IsSubdirector()]
        return super().get_permissions()
```

---

## Permisos a Nivel de Objeto

### Problema: BOLA (Broken Object Level Authorization)

❌ **Sin permisos a nivel de objeto:**

```http
# Estudiante Juan (ID 1) puede hacer:
GET /api/v1/evaluaciones/999/   # Evaluación de otro estudiante!

Response 200 OK:
{
  "id": 999,
  "student": "María López",
  "grade": "M",  # Juan ve calificación de María
  "comment": "Comportamiento inaceptable"
}

# Vulnerabilidad: Juan no debería ver datos de otros estudiantes
```

✅ **Con BOLA mitigation:**

```python
# core/permissions.py
class IsStudentOwnerOrReadOnly(BasePermission):
    """Estudiante solo ve/modifica sus propios recursos."""
    
    def has_object_permission(self, request, view, obj):
        # Si es GET: permitido verlo
        if request.method in SAFE_METHODS:
            return True
        
        # Si es POST/PATCH/DELETE: solo si es propietario
        return obj.student.user == request.user

# Uso en ViewSet:
class EvaluationViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated, IsStudentOwnerOrReadOnly]

# Resultado:
GET /api/v1/evaluaciones/999/   # María

# Si ejecuta Juan:
Response 403 Forbidden: "Not allowed to view this object"
```

### Tres Patrones de Object-Level Permission

```python
# Patrón 1: Propiedad Directa
class IsOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.user == request.user

# Uso: Información (quien la creó puede editarla)
info.created_by == request.user  ✅

# Patrón 2: Propiedad a Través de Estudiante
class IsStudentOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.student.user == request.user

# Uso: Evaluaciones, Quejas, Asignaciones
evaluation.student.user == request.user  ✅

# Patrón 3: Asignado Por
class IsAssignedBy(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.assigned_by == request.user

# Uso: Asignaciones
assignment.assigned_by == request.user  ✅
```

---

## Rate Limiting

### Configuración (django-axes)

```python
# config/settings/base.py
INSTALLED_APPS = [
    ...,
    'axes',  # Bloqueo por intentos fallidos
]

MIDDLEWARE = [
    ...,
    'axes.middleware.AxesMiddleware',  # Debe ir después de SessionMiddleware
]

AUTHENTICATION_BACKENDS = [
    'axes.backends.AxesStandaloneBackend',
    'django.contrib.auth.backends.ModelBackend',
]

# Configuración de bloqueo
AXES_FAILURE_LIMIT = 5           # 5 intentos fallidos
AXES_COOLOFF_TIME = timedelta(minutes=15)  # Bloqueo 15 minutos
AXES_LOCKOUT_PARAMETERS = ['ip_address']  # Por dirección IP
AXES_LOCK_OUT_BY_COMBINATION_USER_AND_IP = False
AXES_RESET_ON_SUCCESS = True     # Reset contador al login exitoso
```

### Flujo de Bloqueo

```
Intento 1:  usuario123 + password_INCORR  ← contador = 1
Intento 2:  usuario123 + password_INCORR  ← contador = 2
Intento 3:  usuario123 + password_INCORR  ← contador = 3
Intento 4:  usuario123 + password_INCORR  ← contador = 4
Intento 5:  usuario123 + password_INCORR  ← contador = 5
                                                    ↓
        HTTP 429 Too Many Requests
        "Account locked. Try again in 15 minutes."

┌─────────────────── 15 minutos ──────────────────┐
│                                                 │
Intento 6:  usuario123 + password_CORRECTO  ← Bloqueo aún activo
            → HTTP 429 Too Many Requests
│                                                 │
└─────────────────────────────────────────────────┘
                    ↓ (15 min pasados)
Intento 7:  usuario123 + password_CORRECTO  ← Bloqueo levantado
            → Login exitoso (contador reset a 0)
```

### Ventajas

✅ **Protección Fuerza Bruta:** impide ataques masivos  
✅ **Automático:** django-axes maneja todo  
✅ **SinRedis:** usa misma BD PostgreSQL  
✅ **Auditoría:** registra intentos fallidos  

---

## Seguridad OWASP

### OWASP API Security Top 10 — Mitigaciones

| Vulnerabilidad | Mitigación Implementada |
|---|---|
| **API1: BOLA** | Permisos a nivel de objeto (IsOwner, IsStudentOwner, IsAssignedBy) |
| **API2: Broken Authentication** | JWT con expiración 15min + rate limiting + HTTPS |
| **API3: Broken Object Property Level Authorization** | Serializadores controlan qué campos se exponen por rol |
| **API4: Unrestricted Resource Consumption** | Paginación, filtrado, rate limiting |
| **API5: Broken Function Level Authorization** | RBAC granular (9 roles) + permisos en cada endpoint |
| **API6: Unrestricted Access to Sensitive Business Flows** | Validaciones de negocio en serializadores y signals |
| **API7: Server-Side Request Forgery** | Django CSRF token en forms; API sin estado (no vulnerable) |
| **API8: Lack of Protection from Automated Attacks** | django-axes + rate limiting |
| **API9: Improper Inventory Management** | API versionada (/api/v1/), documentación completa en Swagger |
| **API10: Unsafe Consumption of APIs** | Backend asume input hostil, valida todo en serializadores |

### Django Built-In Security

Django protege contra OWASP Top 10 web por defecto:

| Riesgo | Protección |
|-------|-----------|
| **SQL Injection** | ORM parametrizado (nunca raw SQL) |
| **XSS (Cross-Site Scripting)** | Escapado automático de templating |
| **CSRF (Cross-Site Request Forgery)** | Django CSRF middleware (tokens) |
| **Clickjacking** | X-Frame-Options header |
| **Security Headers** | X-Content-Type-Options, X-XSS-Protection |

---

## Ejemplos de Requests

### 1. Login Exitoso

```bash
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "luis_garcia",
    "password": "MiPassword123!"
  }'

# Response 200 OK
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOjEsImlhdCI6MTY1Mzk...",
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoxLCJyb2xlcyI6WyJl...",
  "user": {
    "id": 1,
    "username": "luis_garcia",
    "first_name": "Luis",
    "last_name": "García",
    "email": "luis@uclv.cu",
    "roles": ["estudiante"]
  }
}
```

### 2. Login Fallido (Password Incorrecto)

```bash
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -d '{"username": "luis_garcia", "password": "WRONG"}'

# Response 401 Unauthorized
{
  "error": "Invalid credentials"
}
```

### 3. Después de 5 Intentos Fallidos

```bash
# Intento 6
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -d '{"username": "luis_garcia", "password": "WRONG"}'

# Response 429 Too Many Requests
{
  "error": "Too many login attempts. Please try again in 15 minutes."
}
```

### 4. Usar Access Token

```bash
curl -X GET http://localhost:8000/api/v1/evaluaciones/mis-evaluaciones/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."

# Response 200 OK
[
  {
    "id": 1,
    "student": "Luis García",
    "date": "2022-04-30",
    "grade": "B",
    "comment": "Comportamiento ejemplar"
  }
]
```

### 5. Token Expirado (>15 min)

```bash
curl -X GET http://localhost:8000/api/v1/estudiantes/ \
  -H "Authorization: Bearer <expired-token>"

# Response 401 Unauthorized
{
  "error": "Token is invalid or expired"
}

# → Usar refresh endpoint para obtener novo access token
```

### 6. Refrescar Token

```bash
curl -X POST http://localhost:8000/api/v1/auth/refresh/ \
  -H "Content-Type: application/json" \
  -d '{"refresh": "eyJ0eXAi..."}'

# Response 200 OK
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."  # Nuevo token
}
```

### 7. Sin Permiso (Estudiante intenta crear otro estudiante)

```bash
curl -X POST http://localhost:8000/api/v1/estudiantes/ \
  -H "Authorization: Bearer <student-token>" \
  -H "Content-Type: application/json" \
  -d '{"user": 1, ...}'

# Response 403 Forbidden
{
  "error": "You do not have permission to perform this action."
}
```

### 8. BOLA Mitigation: Ver Evaluación de Otro

```bash
# Estudiante Juan intenta ver evaluación de María
curl -X GET http://localhost:8000/api/v1/evaluaciones/999/ \
  -H "Authorization: Bearer <juan-token>"

# Response 403 Forbidden
{
  "error": "You do not have permission to access this object."
}
```

---

## Resumen de Seguridad

✅ **Autenticación:** JWT con tokens de vida corta (15 min access)  
✅ **Autorización:** RBAC + permisos a nivel de objeto  
✅ **Rate Limiting:** 5 intentos → 15 min bloqueo  
✅ **OWASP:** Medidas contra API Top 10  
✅ **Django Built-In:** Protecciones contra XSS, SQLi, CSRF, Clickjacking  
✅ **HTTPS:** Obligatorio en producción  
✅ **Auditoría:** Timestamps + user tracking en cada cambio  

**Próximos pasos (futuro):**
- Implementar Redis blacklist para revocación inmediata de tokens
- Cifrado de campos sensibles (CI) con pgcrypto
- Implementar soft-delete para auditoría completa
- 2FA (Two-Factor Authentication)

---

**Última actualización:** 21 de mayo de 2026
