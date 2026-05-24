# 🌱 Seeding de Base de Datos

Guía para cargar datos realistas de prueba en la base de datos. El seed actual crea un escenario completo con relaciones académicas, infraestructura y operaciones coherentes.

---

## Tabla de contenidos

1. [Qué carga el seed](#qué-carga-el-seed)
2. [Instalación y uso](#instalación-y-uso)
3. [Datos de login](#datos-de-login)
4. [Verificación](#verificación)
5. [Casos de uso incluidos](#casos-de-uso-incluidos)
6. [Troubleshooting](#troubleshooting)

---

## Qué carga el seed

El comando `seed_database` puebla la BD con datos completos e íntegros para simular un semestre académico realista.

### Cantidad de datos

```text
🏢 INFRAESTRUCTURA
├─ 3 sedes
├─ 8 edificios
├─ 24 alas
└─ 120 cuartos

🎓 ACADÉMICO
├─ 2 facultades
├─ 3 carreras
├─ 15 años académicos
└─ 45 grupos de estudiantes

👥 PERSONAS
├─ 50+ profesores con roles completos
│  ├─ 2 decanos
│  ├─ 5 PPAs
│  ├─ 15 PGs
│  ├─ 24 responsables de ala
│  ├─ 2 subdirectores
│  ├─ 2 comunicadores
│  └─ 1 administrador
└─ 150 estudiantes

📋 OPERACIONES
├─ 80+ evaluaciones
├─ 50+ quejas
├─ 60+ cuartelerías
├─ 105+ asignaciones activas
├─ 12 informaciones
└─ 8 reportes
```

### Cobertura funcional

- Jerarquía académica completa: Facultad → Carrera → Año → Grupo → Estudiante
- Roles y permisos creados para todo el sistema
- Ocupancia y asignaciones útiles para pruebas de frontend
- Estados variados en quejas, evaluaciones y cuartelerías
- Datos listos para paginación, filtros y búsquedas

---

## Instalación y uso

### Requisitos previos

- Python 3.12+
- Proyecto configurado con UV
- Migraciones aplicadas
- Roles creados si aún no existen

### Ejecutar migraciones y roles

```bash
python manage.py migrate
python manage.py create_roles
```

### Ejecutar el seed

```bash
python manage.py seed_database
```

### Salida esperada

```text
✅ Seed database completado exitosamente!
📊 DATOS CARGADOS:
   🏗️  Infraestructura: 3 sedes, 8 edificios, 24 alas, 120 cuartos
   👥 Estudiantes: 150 (con 105+ asignaciones activas)
   📋 Evaluaciones: 80+
   🗣️  Quejas: 50+
   🧹 Cuartelerías: 60+
   📢 Informaciones: 12
   📊 Reportes: 8
```

### Limpiar la base de datos y repetir

```bash
python manage.py flush --no-input
python manage.py seed_database
```

Si usas SQLite y prefieres reiniciar desde cero:

```bash
del db_dev.sqlite3
python manage.py migrate
python manage.py seed_database
```

---

## Datos de login

### Estudiantes

- Patrón: `student_0001` a `student_0150`
- Password: `Pass1234!`
- Rol: `estudiante`

Ejemplo:

```text
username: student_0001
password: Pass1234!
email: student_0001@uclv.cu
roles: estudiante
```

### Profesores y personal

- Decanos: `dean_faculty_01`, `dean_faculty_02`
- PPAs: `profesor_ppa_01` a `profesor_ppa_05`
- PGs: `profesor_pg_01` a `profesor_pg_15`
- Responsables de ala: `wing_supervisor_01` a `wing_supervisor_24`
- Subdirectores: `subdirector_admin_01`, `subdirector_admin_02`
- Comunicadores: `comunicador_01`, `comunicador_02`

Password para estos usuarios: `Pass1234!`

### Administrador

```text
username: admin
password: admin123
email: admin@uclv.cu
roles: admin
```

---

## Verificación

### En Django Admin

```text
http://localhost:8000/admin/
```

Verificar:

- Users: 150+ estudiantes y 50+ profesores
- Faculties: 2
- Careers: 3
- Career Years: 15
- Groups: 45
- Sites: 3
- Buildings: 8
- Wings: 24
- Rooms: 120
- Students: 150
- Professors: 50+
- Complaints: 50+
- Evaluations: 80+

### En Swagger

```text
http://localhost:8000/api/v1/docs/
```

Pruebas recomendadas:

- `GET /api/v1/estudiantes/` → 150 estudiantes paginados
- `GET /api/v1/cuartos/` → 120 cuartos
- `GET /api/v1/evaluaciones/` → 80 evaluaciones
- `GET /api/v1/quejas/` → 50+ quejas
- `GET /api/v1/grupos/` → 45 grupos

### En shell de Django

```bash
python manage.py shell
```

```python
from apps.actors.models import Student, Professor
from apps.infrastructure.models import Room, Assignment
from apps.operations.models import Complaint, Evaluation, CleaningSchedule

print(Student.objects.count())
print(Professor.objects.count())
print(Room.objects.count())
print(Assignment.objects.filter(released_date__isnull=True).count())
print(Evaluation.objects.count())
print(Complaint.objects.count())
print(CleaningSchedule.objects.count())
```

---

## Casos de uso incluidos

- Consulta de datos propios por parte del estudiante
- Evaluaciones distribuidas a lo largo del semestre
- Quejas con varios estados de flujo
- Cuartelerías con avance y finalización
- Informaciones públicas y reportes administrativos
- Pruebas de permisos por rol

---

## Troubleshooting

### Error: roles no creados

```bash
python manage.py create_roles
python manage.py seed_database
```

### Error: migraciones pendientes

```bash
python manage.py migrate
python manage.py seed_database
```

### Error: seed parcial o datos duplicados

```bash
python manage.py flush --no-input
python manage.py seed_database
```

### En Windows, borrar SQLite

```bash
del db_dev.sqlite3
```
