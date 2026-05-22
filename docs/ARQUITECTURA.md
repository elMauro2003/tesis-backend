# 🏗️ Arquitectura del Sistema

**Guía completa del diseño del backend: capas, modelos, patrones y decisiones técnicas.**

---

## Tabla de Contenidos

1. [Patrón Arquitectónico](#patrón-arquitectónico)
2. [Capas del Sistema](#capas-del-sistema)
3. [Modelo de Datos](#modelo-de-datos)
4. [Principios SOLID](#principios-solid)
5. [Optimizaciones de Base de Datos](#optimizaciones-de-base-de-datos)
6. [Decisiones de Diseño](#decisiones-de-diseño)
7. [Flujos de Datos](#flujos-de-datos)

---

## Patrón Arquitectónico

### MVC Adaptado a DRF

El sistema implementa **patrón MVC (Model-View-Controller)** adaptado a Django REST Framework:

```
┌─────────────────────────────────────────────────────────────────────┐
│                          HTTP REQUEST                               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   URLs (urls.py) ←→ ViewSet (views.py) ←→ Serializer (serializers.py)
│                           ↓                         ↓              │
│                    Permissions                 Validations        │
│                   (permissions.py)              (validators)       │
│                           ↓                         ↓              │
│                      Logic (actions)          Field mappings      │
│                           ↓                         ↓              │
│                     QuerySet Ops         (read_only, required)     │
│                    (select_related,                                │
│                     prefetch_related)          MODELS (models.py)  │
│                           ↓                         ↓              │
│   ┌────────────────────────────────────────────────────────────┐  │
│   │         PostgreSQL DATABASE (ACID Transactions)           │  │
│   │                                                            │  │
│   │  - Integridad referencial (FOREIGN KEYs)                │  │
│   │  - Constraints (UNIQUE, CHECK)                          │  │
│   │  - Índices (normales, parciales)                        │  │
│   │  - Triggers (sincronización automática)                 │  │
│   │  - Audit trail (created_at, updated_at)                │  │
│   └────────────────────────────────────────────────────────────┘  │
│                                                                     │
├─────────────────────────────────────────────────────────────────────┤
│                        HTTP RESPONSE (JSON)                         │
└─────────────────────────────────────────────────────────────────────┘
```

### Principios

- **Separación de Responsabilidades:** cada capa (M, V, C) tiene rol específico
- **Statelessness:** no hay estado en servidor (JWT es stateless)
- **Escalabilidad Horizontal:** cualquier instancia puede manejar cualquier solicitud
- **Seguridad de Capas:** validación en modelo, serializador y vista

---

## Capas del Sistema

### Capa 1: Modelos (models.py)

**Responsabilidad:** Definir entidades del dominio, relaciones, constraints, métodos de negocio.

```python
# apps/actors/models.py
class Student(models.Model):
    # Relación con Django User (herencia multi-tabla)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    # Atributos propios del estudiante
    ci = models.CharField(max_length=11, unique=True)  # Identificación
    student_id = models.CharField(max_length=20, unique=True)  # Matrícula
    birth_date = models.DateField()
    gender = models.CharField(max_length=1, choices=[('M', 'M'), ('F', 'F')])
    
    # Relaciones
    group = models.ForeignKey('academic.Group', on_delete=models.CASCADE)
    
    # Auditoría
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'students'
        ordering = ['-created_at']
        # Índice para búsquedas por CI
        indexes = [
            models.Index(fields=['ci']),
            models.Index(fields=['student_id']),
        ]
    
    def __str__(self):
        return f"{self.student_id} - {self.user.get_full_name()}"
```

**Características:**
- ✅ Validaciones a nivel de modelo (UNIQUE, CHECK, Foreign Keys)
- ✅ Métodos de negocio (querys frecuentes, lógica de dominio)
- ✅ Herencia multi-tabla para polimorfismo (User → Student/Professor)
- ✅ Timestamps automáticos (created_at, updated_at) para auditoría
- ✅ Índices para performance

### Capa 2: Serializadores (serializers.py)

**Responsabilidad:** Convertir modelos ↔ JSON, validar entrada, controlar qué campos se exponen.

```python
# apps/actors/serializers.py
class StudentSerializer(serializers.ModelSerializer):
    # Campo anidado (GET retorna grupo completo)
    group_name = serializers.CharField(source='group.name', read_only=True)
    
    # Campo computed (no está en modelo)
    age = serializers.SerializerMethodField()
    
    class Meta:
        model = Student
        fields = ['id', 'student_id', 'ci', 'user', 'birth_date', 
                  'gender', 'group', 'group_name', 'age', 'created_at']
        read_only_fields = ['id', 'created_at', 'group_name', 'age']
        extra_kwargs = {
            'ci': {'validators': [UnicityValidator()]},  # Validación personalizada
            'student_id': {'required': True},
        }
    
    def get_age(self, obj):
        """Calcula edad actual del estudiante."""
        today = date.today()
        return today.year - obj.birth_date.year - (
            (today.month, today.day) < (obj.birth_date.month, obj.birth_date.day)
        )
    
    def validate_ci(self, value):
        """Valida formato de CI cubano."""
        if len(value) != 11:
            raise serializers.ValidationError("CI debe tener 11 dígitos")
        if not value.isdigit():
            raise serializers.ValidationError("CI solo contiene dígitos")
        return value
```

**Características:**
- ✅ Conversión automática modelos → JSON (y viceversa)
- ✅ Validación de entrada (campos requeridos, formatos, constraints)
- ✅ Campos read_only (no se pueden modificar via API)
- ✅ Anidamiento controlado (mostrar relaciones según necesidad)
- ✅ Campos computed (no en BD, calculados en serialización)

### Capa 3: ViewSets (views.py)

**Responsabilidad:** Procesar HTTP requests, aplicar lógica de negocio, retornar respuestas.

```python
# apps/actors/views.py
class StudentViewSet(ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticated, IsInstructorOrDirectivo]
    filterset_fields = ['group', 'gender', 'is_militant']
    search_fields = ['user__first_name', 'user__last_name', 'student_id', 'ci']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Optimiza queries con select_related para evitar N+1."""
        return Student.objects.select_related(
            'user',           # User fields
            'group'           # Group fields
        ).prefetch_related(
            'assignments'     # Relación inversa (muchos)
        )
    
    def perform_create(self, serializer):
        """Hook ejecuado al crear (POST)."""
        student = serializer.save()
        # Lógica adicional si es necesaria
        send_welcome_email(student)  # Ejemplo
    
    @action(detail=True, methods=['get'])
    def current_room(self, request, pk=None):
        """Acción personalizada: obtener cuarto actual del estudiante."""
        student = self.get_object()
        assignment = Assignment.objects.filter(
            student=student, 
            released_date__isnull=True
        ).first()
        if not assignment:
            return Response(
                {'detail': 'Student has no active assignment'},
                status=status.HTTP_404_NOT_FOUND
            )
        return Response(RoomSerializer(assignment.room).data)
```

**Características:**
- ✅ CRUD automático (GET, POST, PATCH, DELETE)
- ✅ Filtrado, búsqueda, paginación, ordenamiento
- ✅ Optimización de queries (select_related, prefetch_related)
- ✅ Acciones personalizadas (@action)
- ✅ Hooks del ciclo de vida (perform_create, perform_destroy)

### Capa 4: Permisos (permissions.py)

**Responsabilidad:** Autenticación y autorización basada en roles.

```python
# core/permissions.py
class IsInstructor(BasePermission):
    """Solo usuarios con rol 'instructor' pueden acceder."""
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            self._user_has_role(request.user, 'instructor')
        )
    
    @staticmethod
    def _user_has_role(user, *roles):
        """Helper: verifica si usuario tiene alguno de los roles."""
        user_groups = user.groups.values_list('name', flat=True)
        return any(role in user_groups for role in roles)

class IsOwnerOrReadOnly(BasePermission):
    """Propietario puede modificar, otros solo leen."""
    
    def has_object_permission(self, request, view, obj):
        # Lecturas permitidas para todos
        if request.method in SAFE_METHODS:
            return True
        
        # Escritura solo si es propietario
        return obj.user == request.user
```

**Características:**
- ✅ Autorización a nivel de vista (puede acceder?)
- ✅ Autorización a nivel de objeto (puede modificar ESTE recurso?)
- ✅ RBAC centralizado (todos los roles en un lugar)
- ✅ Composición (múltiples permisos en mismo endpoint)

### Capa 5: URLs (urls.py)

**Responsabilidad:** Mapear rutas HTTP a ViewSets.

```python
# apps/actors/urls.py
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'estudiantes', StudentViewSet, basename='student')
router.register(r'profesores', ProfessorViewSet, basename='professor')

urlpatterns = router.urls

# URL generadas automáticamente:
# GET    /api/v1/estudiantes/           → list()
# POST   /api/v1/estudiantes/           → create()
# GET    /api/v1/estudiantes/{id}/      → retrieve()
# PATCH  /api/v1/estudiantes/{id}/      → partial_update()
# DELETE /api/v1/estudiantes/{id}/      → destroy()
# GET    /api/v1/estudiantes/{id}/current_room/  → action personalizada
```

**Características:**
- ✅ Routers automáticos (generan 5 endpoints por ViewSet)
- ✅ Nombres de ruta para generación de URLs
- ✅ Prefijos de versión de API (/api/v1/)

---

## Modelo de Datos

### Jerarquía Relacional

```
┌───────────────────────────────────────────────────┐
│         ACADÉMICO-ADMINISTRATIVO                 │
├───────────────────────────────────────────────────┤
│                                                   │
│  Faculty (1)  ← → Career (N)                      │
│      ↓              ↓                              │
│   Dean (1)    CareerYear (1:5)                    │
│              ↓                                     │
│          Group (1:N)                              │
│              ↓                                     │
│          Student ← – – – – ← ← ← ← ← →            │
│                                      ↓             │
│                                  User (Django)    │
│                                                   │
└───────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────┐
│         INFRAESTRUCTURA FÍSICA                    │
├───────────────────────────────────────────────────┤
│                                                   │
│  Site (1) → Building (1:N) → Wing (1:N) → Room (1:N)
│      ↓          ↓                ↓           ↓     │
│    Sede     Edificio          Ala         Cuarto  │
│                                ↓           ↓       │
│                        WingSupervisor  Assignment  │
│                                           ↓       │
│                                        Student    │
│                                                   │
└───────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────┐
│         OPERACIONAL                              │
├───────────────────────────────────────────────────┤
│                                                   │
│    Student → Complaint (quejas con respuesta)     │
│          → Evaluation (periódicas)                │
│          → CleaningSchedule (cuartelerías)        │
│          → Assignment (histórico de cuartos)      │
│                                                   │
│    User (instructor) → createdBy (Evaluación)     │
│                    → createdBy (Information)      │
│                    → generatedBy (Report)         │
│                                                   │
└───────────────────────────────────────────────────┘
```

### Herencia Multi-Tabla

Django soporta 3 estrategias de herencia; **seleccionamos multi-tabla** porque:

```python
# Estrategia: OneToOneField (multi-tabla)
class User(AbstractUser):
    """Base de Django Auth"""
    pass

class Student(models.Model):
    """Subclase 1: Estudiante"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    ci = models.CharField(max_length=11)
    student_id = models.CharField(max_length=20)

class Professor(models.Model):
    """Subclase 2: Profesor"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    employee_id = models.CharField(max_length=20)

# Ventajas:
# ✅ User se usa para autenticación (login)
# ✅ Student/Professor con campos específicos en tablas separadas
# ✅ select_related('user') trae ambas en 1 query
# ✅ Normalización (evita columnas NULL)

# Alternativa 1: Abstract (DESCARTADA)
# ❌ No hay tabla base
# ❌ Imposible hacer login contra User directamente

# Alternativa 2: Proxy (DESCARTADA)
# ❌ Solo 1 tabla base (no hay lugar para campos específicos)
```

### Constraints y Índices

```sql
-- Integridad Referencial
ALTER TABLE students ADD CONSTRAINT fk_group 
  FOREIGN KEY (group_id) REFERENCES groups(id) ON DELETE CASCADE;

-- Unicidad
ALTER TABLE students ADD CONSTRAINT unique_ci UNIQUE (ci);
ALTER TABLE students ADD CONSTRAINT unique_student_id UNIQUE (student_id);

-- Índices (velocidad de lectura)
CREATE INDEX idx_student_group ON students(group_id);
CREATE INDEX idx_assignment_student ON assignments(student_id);

-- Índice Parcial (asignación activa única)
CREATE UNIQUE INDEX idx_active_assignment 
  ON assignments (student_id) 
  WHERE released_date IS NULL;

-- Índice Compuesto (queries frecuentes)
CREATE INDEX idx_complaint_student_date 
  ON complaints(student_id, date DESC);
```

---

## Principios SOLID

### S — Single Responsibility Principle

✅ Cada clase tiene **una sola razón para cambiar**:

```python
# BIEN ✅
class StudentSerializer(serializers.ModelSerializer):
    """Solo serialización Student → JSON"""
    class Meta:
        model = Student
        fields = [...]

class StudentViewSet(ModelViewSet):
    """Solo manejo HTTP requests de estudiantes"""
    queryset = Student.objects.all()
    serializer_class = StudentSerializer

class IsInstructor(BasePermission):
    """Solo determina si usuario es instructor"""
    pass

# MAL ❌
class StudentManagement:
    def serialize(self, obj): ...
    def get_from_db(self): ...
    def handle_http(self): ...
    def check_permission(self): ...
    # Cambios en serialización, BD, HTTP, etc. afectan esta clase
```

### O — Open for Extension, Closed for Modification

✅ Extendemos sin modificar código existente:

```python
# BIEN ✅
class BasePermission:
    """Base abstracta"""
    def has_permission(self, request, view):
        raise NotImplementedError

class IsInstructor(BasePermission):
    """Extensión: instructor"""
    def has_permission(self, request, view):
        return self._user_has_role(request.user, 'instructor')

class IsDirectivo(BasePermission):
    """Otra extensión: directivo"""
    def has_permission(self, request, view):
        return self._user_has_role(request.user, 'directivo')

# Añadimos nuevo rol SIN modificar BasePermission ✅

# MAL ❌
class Permission:
    def has_permission(self, role):
        if role == 'instructor':
            return ...
        elif role == 'directivo':
            return ...
        elif role == 'estudiante':
            return ...
        # Agregar rol nuevo = modificar esta clase
```

### L — Liskov Substitution Principle

✅ Subclases intercambiables por superclase:

```python
# BIEN ✅
class BasePermission:
    def has_permission(self, request, view) -> bool: ...

# Todos estos intercambiables en permission_classes
permission_classes = [IsInstructor]  # ✅ también IsDirectivo, IsEstudiante, etc
```

### I — Interface Segregation Principle

✅ Interfaces específicas vs. monolíticas:

```python
# BIEN ✅
class CanDelete(BasePermission):
    """Interface: permitir eliminación"""
    def has_permission(self, request, view):
        return request.method != 'DELETE'

class CanCreate(BasePermission):
    """Interface: permitir creación"""
    def has_permission(self, request, view):
        return request.method != 'POST'

# Cada endpoint usa solo lo que necesita:
create_view_perms = [IsAuthenticated, CanCreate]
delete_view_perms = [IsAuthenticated, CanDelete]

# MAL ❌
class AllPermissions(BasePermission):
    """Una interfaz monolítica para todo"""
    # Mixtura de responsabilidades
```

### D — Dependency Inversion Principle

✅ Dependemos de abstracciones (interfaces), no de concretos:

```python
# BIEN ✅
class StudentViewSet:
    serializer_class = StudentSerializer  # Abstracto (interfaz)
    def get_serializer_class(self):
        return self.serializer_class

# Podemos intercambiar: StudentSerializer, StudentDetailSerializer, etc.

# MAL ❌
class StudentViewSet:
    def get_serializer_class(self):
        return StudentSerializer()  # Acoplado a concreto
```

---

## Optimizaciones de Base de Datos

### N+1 Query Problem

❌ **Problema sin optimización:**

```python
students = Student.objects.all()

for student in students:  # 1 query
    print(student.group.name)  # 1+N queries (140 queries para 140 estudiantes!)
    print(student.user.email)  # Otra 1+N

# Total: 1 + (140 * 2) = 281 queries 😱
```

✅ **Con `select_related` y `prefetch_related`:**

```python
students = Student.objects.select_related(
    'group',      # FK: trae en 1 query (JOIN)
    'user',       # OneToOne: trae en 1 query (JOIN)
).prefetch_related(
    'assignments', # Reverse FK: trae en 2 queries (separado pero eficiente)
)

for student in students:  # 2 queries TOTALES
    print(student.group.name)  # Sin query adicional
    print(student.user.email)  # Sin query adicional
    print(list(student.assignments.all()))  # Sin query adicional

# Total: 2 queries (vs. 281) ✅ 140x más rápido!
```

**Regla:**
- `select_related()` para ForeignKey y OneToOneField (relationships "uno a uno")
- `prefetch_related()` para ManyToManyField y reverse ForeignKeys

### Índices Estratégicos

```python
# Búsquedas frecuentes
class Student(models.Model):
    ci = models.CharField(max_length=11, db_index=True)  # Busco por CI
    student_id = models.CharField(max_length=20, db_index=True)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, db_index=True)

# Índices compuestos para queries complejas
class Meta:
    indexes = [
        models.Index(fields=['group', 'is_militant']),  # Filtro por ambos
    ]
```

### Paginación

```python
class StudentViewSet(ModelViewSet):
    pagination_class = PageNumberPagination

# GET /api/v1/estudiantes/?page=1&page_size=20
# Response: { "count": 500, "next": "...", "previous": null, "results": [...] }

# Ventajas:
# ✅ No trae todo a memoria
# ✅ Reduce carga de red
# ✅ Frontend pagina más rápido
```

---

## Decisiones de Diseño

### JWT vs. Session Cookies

| Criterio | JWT | Sessions |
|----------|-----|----------|
| **Stateless** | ✅ Sí | ❌ Requiere BD |
| **Horizontal Scaling** | ✅ Fácil (cualquier servidor) | ❌ Requiere sessión compartida (Redis) |
| **Mobile-Friendly** | ✅ Sí (headers) | ❌ No siempre |
| **CORS** | ✅ Simple | ❌ Complejo |
| **Revocación** | ❌ Difícil | ✅ Inmediata |

**Seleccionado: JWT** porque el proyecto es stateless y escalable horizontalmente.

### Herencia Multi-Tabla vs. Proxy

| Estrategia | Ventajas | Desventajas |
|-----------|----------|------------|
| **Multi-tabla (seleccionada)** | Campos específicos, normalized | Joins adicionales |
| **Proxy** | Sencillo, single table | No soporta campos adicionales |
| **Abstract** | Eficiente | No hay tabla base (problema para login) |

**Seleccionada: Multi-tabla** porque necesitamos campos específicos y tabla base de User para autenticación.

### Soft Delete vs. Hard Delete

```python
# ❌ Hard Delete (actual)
student.delete()  # Desaparece de BD

# ✅ Soft Delete (futuro)
class SoftDeleteModel(models.Model):
    deleted_at = models.DateTimeField(null=True, blank=True)
    
    def soft_delete(self):
        self.deleted_at = timezone.now()
        self.save()

# Ventajas: auditoría, recuperación, reportes históricos
# Actual: usamos hard delete; futuro implementar soft delete si es necesario
```

---

## Flujos de Datos

### Flujo 1: Crear Estudiante (POST)

```
1. Cliente envía:
   POST /api/v1/estudiantes/
   {
     "user": 1,
     "ci": "90010112345",
     "student_id": "ICI-2022-001",
     ...
   }

2. URL Router → StudentViewSet.create()

3. ViewSet.create():
   - Obtiene el Serializer
   - Pasa datos al serializer

4. Serializer.is_valid():
   - ci.validate() → Valida formato
   - student_id.validate() → Verifica unicidad
   - group.validate() → Verifica que grupo existe
   - Retorna True/False

5. Si válido: Serializer.save()
   - Crea instancia: Student(...)
   - Ejecuta Signal: post_save

6. Signal post_save:
   - Log: "estudiante creado"
   - Envía email de bienvenida

7. ViewSet retorna respuesta 201:
   {
     "id": 1,
     "student_id": "ICI-2022-001",
     ...
   }
```

### Flujo 2: Asignar Cuarto (POST con Validación Compleja)

```
1. Cliente envía:
   POST /api/v1/asignaciones/
   {
     "student": 1,
     "room": 5
   }

2. ViewSet.create()
   - Obtiene Student y Room

3. Validaciones:
   a) ¿Student ya tiene asignación activa?
      SELECT * FROM assignments 
      WHERE student_id = 1 AND released_date IS NULL
      → Si existe: ValidationError (400)
   
   b) ¿Room está lleno?
      SELECT current_occupancy, capacity FROM rooms WHERE id = 5
      → Si occupancy == capacity: ValidationError (400)
   
   c) ¿Room activo?
      → Si is_active = False: ValidationError (400)

4. Si todas válidas:
   - Crea Assignment
   - Ejecuta Signal: post_save → increment occupancy

5. Trigger PostgreSQL:
   UPDATE rooms SET current_occupancy = current_occupancy + 1
   WHERE id = 5
   
   IF current_occupancy == capacity THEN
     UPDATE rooms SET is_full = True
   END IF

6. ViewSet retorna 201 con datos asignación:
   {
     "id": 1,
     "student": {...},
     "room": {...},
     "is_active": true,
     "assigned_date": "2022-02-15"
   }
```

---

## 📊 Resumen de Capas

| Capa | Ubicación | Responsabilidad | Ejemplo |
|------|-----------|-----------------|---------|
| **Modelo** | `models.py` | Definir entidades, relaciones, constraints | `class Student(models.Model)` |
| **Serializer** | `serializers.py` | Convertir bidi: modelo ↔ JSON | `class StudentSerializer` |
| **ViewSet** | `views.py` | Procesar HTTP, CRUD, lógica negocio | `class StudentViewSet` |
| **Permisos** | `permissions.py` | Autenticación, autorización, RBAC | `class IsInstructor` |
| **URLs** | `urls.py` | Mapear rutas a vistas | `router.register(...)` |
| **Base Datos** | PostgreSQL | Almacenar datos, garantizar integridad | Tablas, constraints, índices |

---

**Última actualización:** 21 de mayo de 2026
