# 📊 REPORTE DE PRUEBAS DE CARGA - Endpoint `/api/v1/estudiantes/`

**Fecha:** 31 de mayo de 2026  
**Proyecto:** UCLV Residencias Backend  
**Base de datos:** SQLite Dev  
**Usuario de prueba:** `admin_bd`

---

## 📝 HISTORIALES DE PRUEBAS

### 🔄 Experimento 1: 2 Workers (Servidor local)

**Servidor:** Uvicorn ASGI @ `127.0.0.1:8001`  
**Workers:** 2  

---

### 🚀 Experimento 2: 4 Workers (Servidor local - ACTUAL)

**Servidor:** Uvicorn ASGI @ `127.0.0.1:8002`  
**Workers:** 4  

Este es el experimento actual que refleja la prueba con mayor paralelismo.

---

## ✅ RESUMEN COMPARATIVO DE EXPERIMENTOS

| Métrica | 2W - 50VU | 2W - 100VU | 4W - 50VU | 4W - 100VU |
|---|---:|---:|---:|---:|
| Escenario | Login + consulta | Login + consulta | Login + consulta | Login + consulta |
| Usuarios concurrentes | 50 | 100 | 50 | 100 |
| Workers | 2 | 2 | 4 | 4 |
| Iteraciones completadas | 100 | 100 | 100 | 100 |
| Requests totales | 200 | 200 | 200 | 200 |
| Checks exitosos | 100.00% | 100.00% | 100.00% | 100.00% |
| Fallos HTTP | 0.00% | 0.00% | 0.00% | 0.00% |
| Latencia promedio | 6.54 s | 13.51 s | 6.34 s | 12.45 s |
| Latencia P95 | 13.67 s | 26.45 s | 13.29 s | 25.01 s |
| RPS | 6.54 | 7.01 | 6.20 | 7.50 |
| Duración total | ~30.6 s | ~28.5 s | ~32.2 s | ~26.7 s |

---

## 📈 RESULTADOS DETALLADOS

### Prueba 1: 50 VUs - Uvicorn con 2 workers

**Objetivo:** medir el comportamiento del stack local con workers async bajo carga moderada.

#### Latencia HTTP

| Percentil | Valor | Evaluación |
|---|---:|---|
| Mín | 155.16 ms | ✅ Muy rápido |
| Mediana | 6.07 s | ⚠️ Alta |
| Media | 6.54 s | ⚠️ Alta |
| P90 | 13.57 s | ❌ Muy alta |
| P95 | 13.67 s | ❌ Muy alta |
| Máx | 13.93 s | ❌ Muy alta |

#### Throughput y recursos

- Requests/segundo: 6.54 RPS
- Iteraciones/segundo: 3.27 IPS
- Datos recibidos: 574 kB
- Datos enviados: 67 kB

#### Observaciones

- El login funcionó correctamente en todas las iteraciones.
- No hubo timeouts ni errores HTTP.
- La latencia sigue siendo alta, pero la estabilidad mejoró respecto a ejecuciones fallidas por autenticación.

---

### Prueba 2: 100 VUs - Uvicorn con 2 workers

**Objetivo:** estresar la concurrencia del servidor local con el mismo flujo real de login + consulta.

#### Latencia HTTP

| Percentil | Valor | Evaluación |
|---|---:|---|
| Mín | 331.82 ms | ✅ Aceptable |
| Mediana | 12.67 s | ❌ Alta |
| Media | 13.51 s | ❌ Alta |
| P90 | 26.41 s | ❌ Muy alta |
| P95 | 26.45 s | ❌ Muy alta |
| Máx | 26.48 s | ❌ Muy alta |

#### Errores y confiabilidad

| Métrica | Valor | Estado |
|---|---:|---|
| Checks exitosos | 100.00% (200/200) | ✅ Correcto |
| Fallos HTTP | 0.00% | ✅ Correcto |
| Tipo de fallo | Ninguno | — |

#### Throughput y recursos

- Requests/segundo: 7.01 RPS
- Iteraciones/segundo: 3.51 IPS
- Datos recibidos: 574 kB
- Datos enviados: 67 kB

#### Observaciones

- El servidor sostuvo la carga sin errores.
- La latencia creció de forma importante al duplicar la concurrencia.
- Aunque la estabilidad es buena, el rendimiento no escala de forma lineal.

---

### Prueba 3: 50 VUs - Uvicorn con 4 workers

**Objetivo:** medir la mejora con el doble de workers async en la misma carga moderada.

#### Latencia HTTP

| Percentil | Valor | Comparación vs 2W |
|---|---:|---|
| Mín | 22.66 ms | 👍 Mejor |
| Mediana | 4.55 s | 👍 25% mejor |
| Media | 6.34 s | 👍 3% mejor |
| P90 | 13.24 s | 👍 Similar |
| P95 | 13.29 s | 👍 Similar |
| Máx | 13.35 s | 👍 Similar |

#### Errores y confiabilidad

| Métrica | Valor | Estado |
|---|---:|---|
| Checks exitosos | 100.00% (200/200) | ✅ Correcto |
| Fallos HTTP | 0.00% | ✅ Correcto |
| Tipo de fallo | Ninguno | — |

#### Throughput y recursos

- Requests/segundo: 6.20 RPS
- Iteraciones/segundo: 3.10 IPS
- Datos recibidos: 574 kB
- Datos enviados: 67 kB

#### Observaciones

- La latencia mediana mejoró un ~25% respecto a 2 workers.
- El máximo se mantuvo en valores similares (~13.3s).
- El throughput fue ligeramente inferior pero sin degradación en confiabilidad.

---

### Prueba 4: 100 VUs - Uvicorn con 4 workers (ACTUAL)

**Objetivo:** validar la mejora de 4 workers bajo máxima carga.

#### Latencia HTTP

| Percentil | Valor | Comparación vs 2W @ 100VU |
|---|---:|---|
| Mín | 19.34 ms | 👍 Mejor |
| Mediana | 11.15 s | 👍 12% mejor |
| Media | 12.45 s | 👍 8% mejor |
| P90 | 24.98 s | 👍 5% mejor |
| P95 | 25.01 s | 👍 5% mejor |
| Máx | 25.04 s | 👍 5% mejor |

#### Errores y confiabilidad

| Métrica | Valor | Estado |
|---|---:|---|
| Checks exitosos | 100.00% (200/200) | ✅ Correcto |
| Fallos HTTP | 0.00% | ✅ Correcto |
| Tipo de fallo | Ninguno | — |

#### Throughput y recursos

- Requests/segundo: 7.50 RPS
- Iteraciones/segundo: 3.75 IPS
- Duración total: 26.7s
- Datos recibidos: 574 kB
- Datos enviados: 67 kB

#### Observaciones

- **Mejora notable:** con 4 workers, la latencia mediana bajó de 12.67s a 11.15s (+12%).
- **P95 más estable:** 25.01s vs 26.45s (5% de mejora).
- **Throughput máximo:** 7.50 RPS es el más alto en todas las pruebas.
- **Confiabilidad:** 100% de checks exitosos sin excepciones.
- **Escalabilidad:** el servidor responde mejor al aumentar workers; la concurrencia se distribuye más efectivamente.

---

## 🔍 ANÁLISIS COMPARATIVO

```text
Escenario: 50 VUs
───────────────────────────────────
2 Workers → 6.54 RPS, 6.07s p50, 13.67s p95, 100% éxito
4 Workers → 6.20 RPS, 4.55s p50, 13.29s p95, 100% éxito
         ↓
Beneficio: -5% RPS pero -25% latencia mediana

───────────────────────────────────
Escenario: 100 VUs (CARGA MÁXIMA)
───────────────────────────────────
2 Workers → 7.01 RPS, 12.67s p50, 26.45s p95, 100% éxito
4 Workers → 7.50 RPS, 11.15s p50, 25.01s p95, 100% éxito
         ↓
Beneficio: +7% RPS, -12% latencia mediana, -5% P95
```

### Lecturas clave

1. **Más workers ayudan:** los 4 workers muestran mejora en latencia bajo carga alta (100 VUs).
2. **Escalabilidad limitada:** la BD SQLite y la natura del endpoint son el cuello de botella principal.
3. **Confiabilidad 100%:** en todos los escenarios, cero fallos y cero errores HTTP.
4. **Throughput máximo:** ~7.5 RPS es la capacidad práctica con SQLite local.

---

## 🎯 CUELLOS DE BOTELLA IDENTIFICADOS

1. **Consulta pesada en `/api/v1/estudiantes/`**
   - Incluso con mejor concurrencia, la latencia sigue superando los 11s en mediana.

2. **Base de datos SQLite en desarrollo**
   - Sirve para desarrollo, pero no refleja una base optimizada para carga concurrente.
   - SQLite con múltiples conexiones simultáneas sufre contención.

3. **Coste de autenticación por iteración**
   - El flujo completo incluye login en cada vuelta, lo que añade presión innecesaria al backend.

4. **Posibles consultas no indexadas o serialización costosa**
   - Hay evidencia previa de consultas con ordenaciones y joins que pueden beneficiarse de índices.

---

## 💡 RECOMENDACIONES

### Críticas

1. ✅ **Mantener Uvicorn/Gunicorn con 4 workers async** en despliegue local y producción.
2. 📊 **Migrar pruebas a PostgreSQL** para obtener resultados representativos de producción.
3. 🔄 **Separar autenticación** de la ruta de consulta en el script k6.

### Altas

4. 📇 **Añadir índices** sobre columnas de ordenación (`full_name`, `carnet`) y filtros.
5. 🚀 **Revisar el queryset y serialización** del listado de estudiantes; considerar pagination más agresiva.
6. 💾 **Usar cache distribuido** en producción si el acceso es repetitivo.

### Medianas

7. 🔧 **Escalar workers según CPU** disponible en el ambiente objetivo.
8. 📈 **Medir nuevamente con BD de staging/producción**.
9. 📝 **Documentar configuración de despliegue** Uvicorn/Gunicorn en README y docs.

---

## 📋 MATRIZ DE CAPACIDAD

| Objetivo de carga | 50 VUs (2W) | 50 VUs (4W) | 100 VUs (2W) | 100 VUs (4W) | Referencia deseada |
|---|---:|---:|---:|---:|---:|
| P50 latencia | 6.07 s | 4.55 s | 12.67 s | 11.15 s | < 300 ms |
| P95 latencia | 13.67 s | 13.29 s | 26.45 s | 25.01 s | < 1 s |
| RPS | 6.54 | 6.20 | 7.01 | 7.50 | > 20 |
| Disponibilidad | 100% | 100% | 100% | 100% | > 99.9% |
| Duración prueba | ~30.6s | ~32.2s | ~28.5s | ~26.7s | — |

---

## 🔗 Referencias

- https://k6.io/docs/
- https://docs.djangoproject.com/en/stable/howto/deployment/asgi/
- https://docs.djangoproject.com/en/stable/topics/db/optimization/
