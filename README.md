# 🏫 Sistema de Gestión de Residencias Estudiantiles — UCLV

**Backend RESTful para gestión integral de becas, infraestructura y control disciplinario de estudiantes residenciales.**

[![Python](https://img.shields.io/badge/Python-3.12+-3776ab?logo=python&logoColor=white)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.0+-092E20?logo=django&logoColor=white)](https://www.djangoproject.com/)
[![DRF](https://img.shields.io/badge/DRF-3.15+-a30000?logo=django&logoColor=white)](https://www.django-rest-framework.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-336791?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Tests](https://img.shields.io/badge/Tests-140%2F140%20✓-brightgreen)]()
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 📋 Contenido Rápido

- [Descripción General](#descripción-general)
- [Inicio Rápido](#inicio-rápido)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Documentación Completa](#📚-documentación-completa)
- [Testing](#testing)
- [Despliegue](#despliegue)

---

## 🎯 Descripción General

### ¿Qué es este proyecto?

Sistema backend centralizado que automatiza la gestión completa de residencias estudiantiles en la Universidad Central "Marta Abreu" de Las Villas (UCLV), reemplazando procesos manuales desarticulados con una **API REST documentada, segura y escalable**.

**Tesis asociada:** "Backend para Sistema de Gestión de Residencia Estudiantil"  
**Autor:** Mauricio Jesús Avalo Tamayo  
**Institución:** UCLV, 2026

### Problemas que resuelve

✅ **Centralización:** bases de datos consolidadas en lugar de hojas de cálculo dispersas  
✅ **Integridad:** transacciones ACID garantizan consistencia de datos  
✅ **Seguridad:** autenticación JWT + RBAC + permisos a nivel de objeto  
✅ **Trazabilidad:** auditoría completa de cambios (quién, cuándo, qué)  
✅ **Escalabilidad:** arquitectura stateless, soporta 5.000+ usuarios  
✅ **Documentación:** API autodocumentada con Swagger/OpenAPI 3.0  

### Capacidades principales

| Dominio | Funcionalidades |
|---------|-----------------|
| **Académico** | Gestión de facultades, carreras, años académicos, grupos de estudiantes |
| **Infraestructura** | Control de sedes, edificios, alas, cuartos, ocupancia en tiempo real |
| **Estudiantes** | Registro, evaluación periódica, asignación de vivienda, seguimiento |
| **Operativo** | Sistema de quejas, cuartelerías, asignaciones, informaciones |
| **Administración** | RBAC con 9 roles, reportería, auditoría, gestión de permisos |

---

## 🚀 Inicio Rápido

### Requisitos previos

- **Python 3.12+**
- **PostgreSQL 15+** (o SQLite para desarrollo)
- **UV** (gestor de paquetes) — [instalar](https://docs.astral.sh/uv/getting-started/)
- **Git**
- **Docker & Docker Compose** (opcional, para containers)

### Instalación en 5 minutos

```bash
# 1️⃣ Clonar repositorio
git clone <repo-url>
cd uclv_residencias

# 2️⃣ Crear entorno virtual con UV
uv venv .venv
source .venv/bin/activate  # Linux/Mac
# o en Windows:
# .venv\Scripts\activate

# 3️⃣ Instalar dependencias
uv pip install -r requirements/dev.txt

# 4️⃣ Configurar variables de entorno
cp .env.example .env
# Editar .env con credenciales locales (DB, SECRET_KEY, etc)

# 5️⃣ Aplicar migraciones y cargar seed
python manage.py migrate
python manage.py seed_database

# 6️⃣ Crear superusuario (admin)
python manage.py createsuperuser

# 7️⃣ Iniciar servidor
python manage.py runserver
```

### Validación rápida

```bash
# Ejecutar suite de tests (140 tests)
pytest -v

# Acceder a API
# Swagger UI: http://localhost:8000/api/v1/docs/
# API Base: http://localhost:8000/api/v1/
# Admin: http://localhost:8000/admin/
```

---

## 📁 Estructura del Proyecto

```
uclv_residencias/
├── README.md                          # Este archivo
├── Contexto.md                        # Contexto académico de la tesis
├── manage.py                          # CLI de Django
├── pytest.ini                         # Config de pytest
├── docker-compose.yml                 # Orquestación local
├── Dockerfile                         # Imagen Docker del APP
│
├── docs/                              # 📚 DOCUMENTACIÓN COMPLETA
│   ├── INDEX.md                       # Tabla de contenidos
│   ├── ARQUITECTURA.md                # Diseño de capas y patrones
│   ├── AUTENTICACION.md               # JWT, RBAC, permisos
│   ├── API_ENDPOINTS.md               # Catálogo completo de endpoints
│   ├── SISTEMA_FLUJO_COMPLETO.md      # Caso de uso operativo end-to-end
│   └── SEED_INSTALLATION.md           # Guía de seed database
│
├── requirements/                      # Dependencias por entorno
│   ├── base.txt                       # Comunes
│   ├── dev.txt                        # Desarrollo (test, debug)
│   └── prod.txt                       # Producción
│
├── config/                            # ⚙️ CONFIGURACIÓN DJANGO
│   ├── __init__.py
│   ├── wsgi.py                        # WSGI para producción
│   ├── urls.py                        # Rutas globales
│   └── settings/
│       ├── __init__.py
│       ├── base.py                    # Configuración común
│       ├── dev.py                     # Desarrollo (DEBUG=True)
│       ├── prod.py                    # Producción (DEBUG=False)
│       └── test.py                    # Testing (SQLite)
│
├── apps/                              # 🎯 DOMINIOS DE NEGOCIO
│   ├── __init__.py
│   ├── authentication/                # Autenticación JWT, roles, usuarios
│   │   ├── models.py                  # User, roles
│   │   ├── serializers.py             # LoginSerializer, ChangePasswordSerializer
│   │   ├── views.py                   # AuthViewSet (login, refresh, logout)
│   │   ├── permissions.py             # Clases RBAC (IsDirectivo, IsInstructor, etc)
│   │   ├── urls.py                    # Rutas /auth/
│   │   ├── management/
│   │   │   └── commands/
│   │   │       ├── create_roles.py    # Crear 9 roles del sistema
│   │   │       ├── assign_role.py     # Asignar rol a usuario
│   │   │       └── seed_database.py   # 🌱 CARGAR DATOS INICIALES
│   │   └── migrations/
│   │
│   ├── academic/                      # Estructura académica
│   │   ├── models.py                  # Faculty, Career, CareerYear, Group
│   │   ├── serializers.py
│   │   ├── views.py                   # CRUD endpoints
│   │   ├── permissions.py
│   │   ├── urls.py
│   │   └── migrations/
│   │
│   ├── actors/                        # Gestión de personas
│   │   ├── models.py                  # Student, Professor, subclases
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── permissions.py
│   │   ├── signals.py                 # Django signals para eventos
│   │   ├── urls.py
│   │   └── migrations/
│   │
│   ├── infrastructure/                # Infraestructura física
│   │   ├── models.py                  # Site, Building, Wing, Room
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── permissions.py
│   │   ├── urls.py
│   │   └── migrations/
│   │
│   └── operations/                    # Operaciones continuas
│       ├── models.py                  # Complaint, Evaluation, CleaningSchedule, Assignment, Information, Report
│       ├── serializers.py
│       ├── views.py                   # ViewSets con acciones personalizadas
│       ├── permissions.py
│       ├── signals.py                 # Actualización de ocupancia
│       ├── urls.py
│       └── migrations/
│
├── core/                              # 🔧 UTILIDADES COMPARTIDAS
│   ├── __init__.py
│   ├── exceptions.py                  # Excepciones personalizadas
│   ├── pagination.py                  # Paginación estándar
│   ├── permissions.py                 # Todas las clases RBAC centralizadas
│   └── permissions/
│
└── tests/                             # ✅ SUITE COMPLETA (140 tests)
    ├── __init__.py
    ├── conftest.py                    # Fixtures de pytest (roles, factories, clientes)
    ├── factories/                     # Factory Boy para datos de prueba
    ├── unit/                          # Pruebas unitarias (modelos, permisos)
    ├── integration/                   # Pruebas de integración (endpoints)
    └── __init__.py
```

---

## 🌱 Seed Database (Datos Iniciales)

El proyecto incluye un **script de población** que carga datos de prueba completos para simular el sistema real.

### Datos que carga

- ✅ 3 sedes
- ✅ 8 edificios
- ✅ 24 alas
- ✅ 120 cuartos
- ✅ 2 facultades
- ✅ 3 carreras
- ✅ 15 años académicos
- ✅ 45 grupos de estudiantes
- ✅ 50+ profesores con roles completos
- ✅ 150 estudiantes
- ✅ 80+ evaluaciones
- ✅ 50+ quejas
- ✅ 60+ cuartelerías
- ✅ 12 informaciones publicadas
- ✅ 8 reportes

**Año académico:** Septiembre 2025 — Julio 2026 (estándar cubano)

### Uso

```bash
# Ejecutar seed (carga todo de un golpe)
python manage.py seed_database

# Verificar en admin o API
http://localhost:8000/admin/
http://localhost:8000/api/v1/estudiantes/
```

📖 **Documentación detallada:** [docs/SEED_INSTALLATION.md](docs/SEED_INSTALLATION.md)

---

## 📚 Documentación Completa

| Documento | Descripción |
|-----------|-------------|
| [**docs/INDEX.md**](docs/INDEX.md) | 🗂️ Tabla de contenidos y navegación |
| [**docs/ARQUITECTURA.md**](docs/ARQUITECTURA.md) | 🏗️ Diseño de capas, modelo de datos, patrones SOLID |
| [**docs/AUTENTICACION.md**](docs/AUTENTICACION.md) | 🔐 JWT, RBAC (9 roles), permisos a nivel objeto |
| [**docs/API_ENDPOINTS.md**](docs/API_ENDPOINTS.md) | 📡 Catálogo de 70+ endpoints con ejemplos |
| [**docs/SISTEMA_FLUJO_COMPLETO.md**](docs/SISTEMA_FLUJO_COMPLETO.md) | 🔄 Caso de uso real: ciclo completo de un estudiante |
| [**docs/SEED_INSTALLATION.md**](docs/SEED_INSTALLATION.md) | 🌱 Guía de seed database y datos iniciales |
| [**Contexto.md**](Contexto.md) | 📜 Contexto académico de la tesis (problema, objetivos, stack) |

### Acceso rápido a Swagger

```
http://localhost:8000/api/v1/docs/    # Swagger UI (interactivo)
http://localhost:8000/api/v1/schema/  # OpenAPI 3.0 JSON
```

---

## ✅ Testing

### Suite completa

```bash
# Ejecutar todos los tests
pytest -v

# Con cobertura
pytest --cov=apps --cov-report=html
# Ver reporte: htmlcov/index.html

# Tests específicos
pytest tests/integration/test_assignments.py -v
pytest tests/unit/test_permissions.py::test_directivo_can_create_site -v
```

### Estadísticas actuales

- **Tests totales:** 140 ✅ PASSING
- **Cobertura:** >80% (módulos críticos)
- **Dominios cubiertos:** Autenticación, RBAC, CRUD, Permisos, Validaciones de negocio
- **Tiempo de ejecución:** ~2 segundos

---

## 🐳 Despliegue

### Desarrollo con Docker Compose

```bash
# Levantar stack completo (backend + PostgreSQL)
docker-compose -f docker-compose.yml up -d

# Ver logs
docker-compose logs -f backend

# Ejecutar migraciones dentro del contenedor
docker-compose exec backend python manage.py migrate

# Parar servicios
docker-compose down
```

### Producción

1. **Variables de entorno:** configurar `.env` con credenciales reales
2. **HTTPS obligatorio:** usar `SECURE_SSL_REDIRECT=True` en `config/settings/prod.py`
3. **Rate limiting:** activo automáticamente (5 intentos fallidos = bloqueo 15 min)
4. **Logging:** integración con ELK o Datadog recomendada
5. **Despliegue:** usar Dokploy, Heroku, AWS EC2 o similar

**Documentación:** [docs/DESPLIEGUE.md](docs/DESPLIEGUE.md) (próximamente)

---

## 🛠️ Desarrollo Local

### Variables de entorno (`.env`)

```bash
# Django
SECRET_KEY=una-clave-muy-secreta-minimo-50-caracteres
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Base de datos (PostgreSQL)
DB_NAME=uclv_residencias
DB_USER=postgres
DB_PASSWORD=tu-contraseña
DB_HOST=localhost
DB_PORT=5432

# CORS (frontend independiente)
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
```

### Comandos útiles

```bash
# Aplicar migraciones
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser

# Crear roles iniciales (admin, directivo, instructor, etc)
python manage.py create_roles

# Cargar datos de prueba
python manage.py seed_database

# Shell interactivo (Django REPL)
python manage.py shell

# Resetear BD completamente
python manage.py flush
```

---

## 🔒 Seguridad

### Implementado

✅ **Autenticación JWT** con refresh tokens (7 días)  
✅ **RBAC** con 9 roles y permisos granulares  
✅ **Permisos a nivel de objeto** (mitigación BOLA)  
✅ **Rate limiting** (django-axes: 5 intentos → 15 min bloqueo)  
✅ **SQL Injection protection** (ORM parametrizado)  
✅ **CSRF protection** (Django middleware)  
✅ **XSS protection** (escapado automático)  
✅ **HTTPS obligatorio** en producción  
✅ **Auditoría completa:** who, when, what (timestamps + user tracking)  

**Revisar:** [docs/AUTENTICACION.md](docs/AUTENTICACION.md) para detalles completos.

---

## 🤝 Contribuyendo

### Principios de desarrollo

1. **TDD:** Tests antes de código
2. **PEP 8:** Estilo Python estándar (enforced con `flake8` + `black`)
3. **Commits claros:** descripción en español o inglés
4. **Pull requests:** incluir tests + documentación

### Flujo de trabajo

```bash
# 1. Crear rama feature
git checkout -b feature/mi-funcionalidad

# 2. Hacer cambios + tests
echo "código" > apps/my_app/models.py
pytest  # ¡Debe pasar!

# 3. Commit
git commit -m "feat: nueva funcionalidad XYZ"

# 4. Push
git push origin feature/mi-funcionalidad

# 5. Pull Request a 'develop'
```

---

## 📞 Soporte

- **Documentación:** ver [docs/](docs/)
- **API Docs:** `http://localhost:8000/api/v1/docs/` (localmente)
- **Issues:** usar Git Issues
- **Email:** [mauricioavalo@protonmail.com]()

---

## 📄 Licencia

Este proyecto está bajo licencia **MIT**. Ver [LICENSE](LICENSE) para detalles.

---

## 🙋 Autor

**Mauricio Jesús Avalo Tamayo**  
Estudiante de Lic. en Ciencias de la Computación  
Universidad Central "Marta Abreu" de Las Villas (UCLV)  
**Año 2026**

**Tutor Académico:** MSc. Enrique Osvaldo Pérez Riverón  
**Tutor Consultante:** Lic. Juan Manuel Castellón Ruiz

---

## ✨ Stack Tecnológico Resumen

| Componente | Tecnología |
|-----------|-----------|
| **Backend** | Django 5.0 + DRF 3.15 |
| **BD** | PostgreSQL 15 |
| **Auth** | JWT (djangorestframework-simplejwt) |
| **Docs API** | OpenAPI 3.0 / Swagger (drf-spectacular) |
| **Testing** | pytest + pytest-django + factory-boy |
| **Container** | Docker + Docker Compose |
| **Package Manager** | UV 0.8+ |
| **Language** | Python 3.12+ |

---

**Última actualización:** 21 de mayo de 2026  
**Versión:** 1.0.0  
**Estado:** ✅ Producción-Ready
