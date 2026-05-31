# 📊 REPORTE DE PRUEBAS DE CARGA - Endpoint `/api/v1/estudiantes/`

**Fecha:** 31 de mayo de 2026  
**Proyecto:** UCLV Residencias Backend  
**Servidor:** Waitress @ localhost:8000  
**Base de datos:** SQLite Dev

---

## ✅ RESUMEN EJECUTIVO

Se ejecutaron dos pruebas de carga contra el endpoint `/api/v1/estudiantes/`:

| Métrica | Prueba 1 (50 VUs) | Prueba 2 (100 VUs) |
|---|---:|---:|
| Escenario | Flujo Completo (auth + query) | Solo Consulta (token compartido) |
| Usuarios concurrentes | 50 | 100 |
| Iteraciones | 100 | 100 |
| Requests totales | 200 | 101 |
| Checks exitosos | 100.00% (200/200) | 97.05% (99/102) |
| Fallos HTTP | 0.00% | 2.97% (timeouts) |
| Duración total | ~37.1s | ~61.9s |

---

## 📈 RESULTADOS DETALLADOS

### Prueba 1: 50 VUs - Flujo completo (autenticación + consulta)

**Objetivo:** simular usuarios reales que hacen login y luego consultan estudiantes.

#### Latencia HTTP

| Percentil | Valor | Evaluación |
|---|---:|---|
| Mín | 1.84 s | ⚠️ Rápido |
| Mediana | 8.16 s | ⚠️ Moderado |
| Media | 8.25 s | ⚠️ Moderado |
| P90 | 12.53 s | ⚠️ Lento |
| P95 | 14.09 s | ❌ Muy lento |
| P99 | 15.50 s | ❌ Muy lento |
| Máx | 15.50 s | ❌ Inaceptable |

#### Throughput y recursos

- Requests/segundo: 5.40 RPS
- Iteraciones/segundo: 2.70 IPS
- Datos recibidos: 576 kB (16 kB/s)
- Datos enviados: 67 kB (1.8 kB/s)

#### Análisis

**Positivo:**
- 100% de éxito en autenticación y consultas.
- Cero errores HTTP.

**Preocupación:**
- La latencia p95 es muy alta para un endpoint de consulta.
- Las respuestas se mantienen entre 1.8 y 15.5 segundos.

---

### Prueba 2: 100 VUs - Solo consulta (token compartido)

**Objetivo:** simular picos de tráfico con usuarios ya autenticados.

#### Latencia HTTP

| Percentil | Valor | Evaluación |
|---|---:|---|
| Mín | 517.95 ms | ✅ Aceptable |
| Mediana | 3.27 s | ⚠️ Aceptable |
| Media | 4.95 s | ⚠️ Lento |
| P90 | 5.93 s | ⚠️ Lento |
| P95 | 6.09 s | ❌ Muy lento |
| P99 | 60.00 s | ❌ Timeout |
| Máx | 60.00 s | ❌ Timeout |

#### Errores y confiabilidad

| Métrica | Valor | Estado |
|---|---:|---|
| Checks exitosos | 97.05% (99/102) | ⚠️ Aceptable |
| Fallos HTTP | 2.97% (3/101) | ⚠️ Preocupante |
| Tipo de fallo | request timeout | Timeout del servidor |

#### Throughput y recursos

- Requests/segundo: 1.63 RPS
- Iteraciones/segundo: 1.62 IPS
- Datos recibidos: 446 kB (7.2 kB/s)
- Datos enviados: 48 kB (774 B/s)

#### Análisis

**Positivo:**
- El servidor soporta 100 VUs sin caerse.
- La mediana sigue siendo mejor que en la prueba de flujo completo.

**Crítico:**
- Hubo 3 requests que llegaron al timeout de 60s.
- El throughput cae de forma marcada respecto a la prueba 1.

---

## 🔍 ANÁLISIS COMPARATIVO

```text
50 VUs  → 5.40 RPS, 8.25s latencia (100% éxito)
100 VUs → 1.63 RPS, 4.95s latencia (97% éxito, 3 timeouts)

Degradación: -70% en throughput, +2.97% en tasa de error
```

### Factor de degradación

- Throughput: 5.40 → 1.63 RPS = 3.3x más lento.
- Concurrencia: 50 → 100 VUs = 2x más usuarios.
- Conclusión: la escalabilidad no es lineal.

---

## 🎯 CUELLOS DE BOTELLA IDENTIFICADOS

1. **Endpoint `/api/v1/estudiantes/` lento**
   - La consulta tarda varios segundos incluso con 50 VUs.
   - Posibles causas: N+1 queries, falta de índices, paginación ineficiente o serialización costosa.

2. **Sin caché**
   - Cada VU ejecuta el mismo query contra la base de datos.

3. **Capacidad limitada del servidor**
   - Waitress en este entorno soporta la carga, pero con degradación visible.

4. **SQLite en desarrollo**
   - Adecuado para dev, pero no para escenarios de alta concurrencia.

---

## 💡 RECOMENDACIONES

### Críticas

1. Optimizar el queryset de `/api/v1/estudiantes/`.
2. Agregar índices a la base de datos.
3. Implementar paginación eficiente.

### Altas

4. Incorporar caché con Redis.
5. Migrar a PostgreSQL en entornos de prueba/producción.
6. Evaluar Gunicorn en producción.

### Medianas

7. Monitoreo con InfluxDB y Grafana.
8. Escalado horizontal detrás de Nginx.

---

## 📋 MATRIZ DE CAPACIDAD

| Objetivo de carga | Mínimo | Actual | Recomendado |
|---|---:|---:|---:|
| P50 latencia | < 200 ms | 8.16 s | < 300 ms |
| P95 latencia | < 500 ms | 14.09 s | < 1 s |
| RPS | > 20 | 5.40 | > 50 |
| Disponibilidad | > 99% | 100% | > 99.9% |

---

## 🎬 Próximos pasos

1. Revisar el queryset del endpoint `/api/v1/estudiantes/`.
2. Añadir índices a la base de datos.
3. Implementar caché si el acceso es repetitivo.
4. Migrar a PostgreSQL cuando sea posible.

---

## 📚 Archivos generados

- `resultados_estudiantes_fullflow.json` — datos brutos Prueba 1
- `resultados_estudiantes_queryonly.json` — datos brutos Prueba 2
- `analizar_resultados.py` — script de análisis

---

## 🔗 Referencias

- https://k6.io/docs/
- https://docs.djangoproject.com/en/stable/topics/db/optimization/
- https://gunicorn.org/
