# 📚 Índice de Documentación

**Bienvenido a la documentación completa del Sistema de Gestión de Residencias Estudiantiles UCLV.**

Aquí encontrarás todo lo necesario para entender, configurar, usar y contribuir al proyecto.

---

## 🗺️ Navegación por Temas

### 🚀 Para Empezar Rápido

1. **[README.md](../README.md)** — Descripción general, instalación en 5 minutos, estructura del proyecto
2. **[SEED_INSTALLATION.md](SEED_INSTALLATION.md)** — Cómo cargar datos de prueba en la BD
3. **[DESPLIEGUE.md](DESPLIEGUE.md)** — Guía completa de despliegue (local, Docker, producción)

### 🏗️ Entender el Diseño

4. **[ARQUITECTURA.md](ARQUITECTURA.md)** — Modelo de datos, capas, patrones SOLID, decisiones técnicas
5. **[AUTENTICACION.md](AUTENTICACION.md)** — JWT, RBAC con 9 roles, permisos a nivel de objeto, seguridad

### 📡 Usar la API

6. **[API_ENDPOINTS.md](API_ENDPOINTS.md)** — Catálogo completo de 70+ endpoints con ejemplos HTTP
7. **[SISTEMA_FLUJO_COMPLETO.md](SISTEMA_FLUJO_COMPLETO.md)** — Caso de uso real: ciclo de vida de un estudiante
8. **[K6_GRAFANA.md](K6_GRAFANA.md)** — Pruebas de carga con k6 y visualización en Grafana

### 📜 Contexto Académico

9. **[Contexto.md](../Contexto.md)** — Tesis: problema, objetivos, justificación tecnológica, requisitos funcionales

---

## 📖 Documentos Detallados

### [ARQUITECTURA.md](ARQUITECTURA.md)

**Objetivo:** Entender cómo está construido el sistema.

**Contiene:**
- Patrón MVC (Django)
- Capas: modelos, serializadores, views, URLs
- Modelo de datos relacional (tablas, FK, constraints)
- Principios SOLID aplicados  
- Ventajas de arquitectura desacoplada
- Optimizaciones (select_related, queries N+1)
- Herencia multi-tabla (User → Student/Professor)

**Para quién:** Desarrolladores, arquitectos, integradores con otros sistemas.

---

### [DESPLIEGUE.md](DESPLIEGUE.md)

**Objetivo:** Desplegar y operar el sistema en diferentes ambientes.

**Contiene:**
- Arquitectura ASGI (Uvicorn + Gunicorn)
- Despliegue local con Uvicorn (con/sin workers)
- Despliegue con Docker Compose
- Despliegue en producción (Linux, PostgreSQL, Nginx, SSL)
- Configuración supervisor y systemd
- Nginx como reverse proxy
- SSL/HTTPS con Let's Encrypt
- PostgreSQL setup y optimizaciones
- Backups automatizados
- Monitoreo y logs
- Troubleshooting de errores comunes

**Variables de entorno críticas:**
- `DEBUG`, `SECRET_KEY`, `ALLOWED_HOSTS`
- `DATABASE_URL` (SQLite dev / PostgreSQL prod)
- `SECURE_SSL_REDIRECT`, `SESSION_COOKIE_SECURE`

**Comando rápido (local con 4 workers):**
```bash
uv run uvicorn config.asgi:application --host 0.0.0.0 --port 8000 --workers 4
```

**Comando producción (Gunicorn + Supervisor):**
```bash
gunicorn config.asgi:application \
    --worker-class uvicorn.workers.UvicornWorker \
    --workers 8 \
    --bind 0.0.0.0:8000
```

**Para quién:** DevOps, SRE, administradores de sistemas, desarrolladores de backend.

---

### [AUTENTICACION.md](AUTENTICACION.md)

**Objetivo:** Entender cómo se autentica y autoriza a usuarios.

**Contiene:**
- Flujo JWT: login → tokens → refresh → logout
- 9 roles del sistema con matriz de permisos
- Permisos a nivel de objeto (BOLA mitigation)
- Rate limiting (django-axes)
- Medidas de seguridad OWASP Top 10
- Ejemplos de solicitudes HTTP

**Para quién:** Desarrolladores frontend, especialistas en seguridad, integradores.

---

### [API_ENDPOINTS.md](API_ENDPOINTS.md)

**Objetivo:** Referencia exhaustiva de todos los endpoints.

**Contiene:**
- Listado de 70+ endpoints HTTP organizados por dominio
- Métodos (GET, POST, PATCH, DELETE)
- Parámetros de entrada y respuestas esperadas
- Códigos HTTP (200, 201, 400, 403, 409, etc)
- Ejemplos de curl y JSON
- Filtrado, búsqueda, paginación

**Para quién:** Desarrolladores frontend, testers, integradores terceros.

**Acceso rápido:** http://localhost:8000/api/v1/docs/ (Swagger UI)

---

### [SISTEMA_FLUJO_COMPLETO.md](SISTEMA_FLUJO_COMPLETO.md)

**Objetivo:** Ver cómo funciona el sistema en la práctica.

**Contiene:**
- Descripción de 9 fases del ciclo académico (sep-jul)
- Caso de uso real completo
- Flujos de: infraestructura, ingreso de estudiantes, asignación, evaluación, quejas, cuartelerías, comunicaciones, liberación, reportería
- Ejemplos paso a paso de requests/responses
- Validaciones de negocio
- Señales automáticas (DB triggers)

**Para quién:** Directivos, users finales, product managers, testers de aceptación.

---

### [SEED_INSTALLATION.md](SEED_INSTALLATION.md)

**Objetivo:** Cargar datos de prueba realistas en la BD.

**Contiene:**
- Qué datos carga el seed
- Cómo ejecutar el script
- Datos de login para users creados
- Verificación de que se cargó correctamente
- Casos de uso incluidos

**Para quién:** Desarrolladores locales, QA, demostración del sistema.

---

### [K6_GRAFANA.md](K6_GRAFANA.md)

**Objetivo:** Ejecutar pruebas de carga con k6 y ver métricas en Grafana.

**Contiene:**
- Script base de carga para autenticación y endpoint protegido
- docker-compose con InfluxDB + Grafana
- Datasource provisionado automáticamente
- Pasos exactos para correr la prueba en Windows

**Para quién:** QA, performance testing, validación de escalabilidad.

---

## 🎯 Flujos de Lectura Recomendados

### 👨‍💻 Soy desarrollador backend

1. [README.md](../README.md) — Instalación rápida
2. [ARQUITECTURA.md](ARQUITECTURA.md) — Entender el diseño
3. [AUTENTICACION.md](AUTENTICACION.md) — Seguridad y permisos
4. [API_ENDPOINTS.md](API_ENDPOINTS.md) — Endpoints disponibles
5. [SISTEMA_FLUJO_COMPLETO.md](SISTEMA_FLUJO_COMPLETO.md) — Caso de uso

### 👱‍♀️ Soy desarrollador frontend

1. [README.md](../README.md) — Setup general
2. [AUTENTICACION.md](AUTENTICACION.md) — JWT y login
3. [API_ENDPOINTS.md](API_ENDPOINTS.md) — Endpoints a consumir
4. `http://localhost:8000/api/v1/docs/` — Swagger UI interactivo (mejor referencia)

### 🔍 Soy testeador/QA

1. [README.md](../README.md) — Instalación
2. [SEED_INSTALLATION.md](SEED_INSTALLATION.md) — Cargar datos de prueba
3. [K6_GRAFANA.md](K6_GRAFANA.md) — Pruebas de carga
4. [SISTEMA_FLUJO_COMPLETO.md](SISTEMA_FLUJO_COMPLETO.md) — Casos de uso
5. [API_ENDPOINTS.md](API_ENDPOINTS.md) — Referencia de endpoints

### 🎓 Soy estudiante/investigador

1. [Contexto.md](../Contexto.md) — Marco académico
2. [README.md](../README.md) — Visión general
3. [ARQUITECTURA.md](ARQUITECTURA.md) — Diseño técnico
4. [AUTENTICACION.md](AUTENTICACION.md) — Seguridad implementada

### 👔 Soy director/stakeholder

1. [README.md](../README.md) — Resumen ejecutivo
2. [SISTEMA_FLUJO_COMPLETO.md](SISTEMA_FLUJO_COMPLETO.md) — Caso de uso operativo
3. [Contexto.md](../Contexto.md) — Contexto institucional y problemas resueltos

---

## 🔗 Enlaces Externos Útiles

### Stack Tecnológico
- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [PostgreSQL Docs](https://www.postgresql.org/docs/)
- [JWT RFC 7519](https://datatracker.ietf.org/doc/html/rfc7519)

### Seguridad
- [OWASP API Security Top 10](https://owasp.org/www-project-api-security/)
- [OWASP Django Security](https://owasp.org/www-project-top-10/)

### Estándares
- [REST API Best Practices](https://restfulapi.net/)
- [OpenAPI 3.0 Specification](https://spec.openapis.org/oas/v3.0.3)
- [HTTP Status Codes](https://httpwg.org/specs/rfc7231.html#status.codes)

---

## 📝 Ruta de Aprendizaje Progresiva

```
PRINCIPIANTE
    ↓
[README.md] — ¿Qué es esto?
    ↓
[SEED_INSTALLATION.md] — Instalar y probar localmente
    ↓
http://localhost:8000/api/v1/docs/ — Explorar endpoints interactivamente
    ↓
[SISTEMA_FLUJO_COMPLETO.md] — Ver caso de uso real
    ↓
INTERMEDIO
    ↓
[AUTENTICACION.md] — Entender JWT y RBAC
    ↓
[API_ENDPOINTS.md] — Referencia exhaustiva
    ↓
[ARQUITECTURA.md] — Entender el diseño interno
    ↓
AVANZADO / CONTRIBUIDOR
    ↓
[Contexto.md] — Marco académico completo
    ↓
Código fuente (apps/) — Implementación
    ↓
Tests (tests/) — Validación de cambios
```

---

## 🆘 Solución de Problemas Rápida

| Problema | Solución |
|----------|----------|
| No sé por dónde empezar | → [README.md](../README.md) |
| No me funciona el seed | → [SEED_INSTALLATION.md](SEED_INSTALLATION.md) |
| ¿Cómo despliego la app? | → [DESPLIEGUE.md](DESPLIEGUE.md) |
| ¿Qué endpoints hay? | → [API_ENDPOINTS.md](API_ENDPOINTS.md) o http://localhost:8000/api/v1/docs/ |
| ¿Por qué rechazo mi request? | → [AUTENTICACION.md](AUTENTICACION.md) (permisos/roles) |
| ¿Cómo integro el frontend? | → [AUTENTICACION.md](AUTENTICACION.md) + [API_ENDPOINTS.md](API_ENDPOINTS.md) |
| Quiero entender el diseño | → [ARQUITECTURA.md](ARQUITECTURA.md) |
| ¿Cuál es el caso de uso real? | → [SISTEMA_FLUJO_COMPLETO.md](SISTEMA_FLUJO_COMPLETO.md) |
| Quiero probar carga y ver métricas | → [K6_GRAFANA.md](K6_GRAFANA.md) |
| ¿Cuál es el rendimiento actual? | → [performance/k6/REPORTE_RENDIMIENTO.md](../performance/k6/REPORTE_RENDIMIENTO.md) |

---

## 📊 Estadísticas del Proyecto

- **Endpoints REST:** 70+
- **Tests:** 140+ (todos ✅ PASSING)
- **Cobertura:** >80%
- **Modelos:** 18
- **Serializadores:** 20+
- **ViewSets:** 12
- **Throughput máximo:** 7.50 RPS (100 VUs, 4 workers)
- **Latencia P95 (prod):** ~25 s (100 VUs) — límite por SQLite dev
- **Disponibilidad:** 100% en todas las pruebas de carga

- **Roles:** 9
- **Permisos:** 14 clases
- **Migraciones:** 4 iniciales + actualizaciones

---

## 🎓 Glosario de Términos

| Término | Definición |
|---------|-----------|
| **API REST** | Interfaz para que aplicaciones se comuniquen via HTTP |
| **JWT** | Token seguro que contiene identidad del usuario |
| **RBAC** | Control de acceso basado en roles (student, instructor, admin, etc) |
| **Endpoint** | URL específica del API (ej: `/api/v1/estudiantes/`) |
| **Serializer** | Convierte modelos Django ↔ JSON |
| **ViewSet** | Genera automáticamente CRUD endpoints para un modelo |
| **BOLA** | Broken Object Level Authorization — vuln. cuando usuario accede recursos de otros |
| **Seed** | Cargar datos iniciales en BD para testing |
| **Migrate** | Aplicar cambios de BD (crear tablas, etc) |
| **Signal** | Disparo automático cuando algo acontece en la BD |

---

## ✅ Checklist de Onboarding

- [ ] Leo [README.md](../README.md)
- [ ] Instalo localmente con [SEED_INSTALLATION.md](SEED_INSTALLATION.md)
- [ ] Acceso a http://localhost:8000/api/v1/docs/
- [ ] Hago login y exploro endpoints en Swagger
- [ ] Leo [SISTEMA_FLUJO_COMPLETO.md](SISTEMA_FLUJO_COMPLETO.md) para entender caso de uso
- [ ] Leo [AUTENTICACION.md](AUTENTICACION.md) si voy a desarrollar
- [ ] Leo [ARQUITECTURA.md](ARQUITECTURA.md) si voy a contribuir código


---

**Última actualización:** 21 de mayo de 2026  
**Versión del doc:** 1.0.0
