# k6 + Grafana para pruebas de carga

Guía rápida para ejecutar pruebas de carga contra este backend y ver métricas en Grafana.

## Resumen rápido

- Modo liviano: solo `k6`, guardas resultados en JSON o ves la consola.
- Modo completo: `k6` + InfluxDB + Grafana (requiere Docker).

## Importante si estás usando datos móviles

Si quieres gastar lo mínimo posible, usa el **modo liviano**:

- instalar solo `k6`
- no levantar Grafana
- no levantar InfluxDB
- guardar el resumen en archivo o ver el resultado en consola

La opción con Grafana requiere descargar imágenes Docker grandes, así que **no es la mejor idea si tienes datos limitados**.

## Qué se creó

- `performance/k6/k6-per-vu.js` — flujo realista (cada VU hace login).
- `performance/k6/k6-loadtest.js` — alta concurrencia (setup único, VUs reutilizan token).
- `performance/k6/docker-compose.yml` — InfluxDB + Grafana (opcional).
- `performance/k6/grafana/provisioning/datasources/datasource.yml` — datasource automático.

## Requisitos

- Backend levantado en http://localhost:8000
- `k6` instalado en Windows
- Docker Desktop (solo si vas a usar Grafana + InfluxDB)

## Comprobar servidor

```powershell
curl http://localhost:8000/api/v1/auth/login/
```

## Levantar el backend (Windows — Waitress recomendado para pruebas)

1. Activar el virtualenv:

```powershell
& .\.venv\Scripts\Activate.ps1
```

2. (Opcional) Instalar `waitress` si no está presente:

```powershell
pip install waitress
```

3. Aplicar migraciones (si es necesario):

```powershell
python manage.py migrate
```

4. Ejecutar Waitress en primer plano (útil para ver logs):

```powershell
waitress-serve --port=8000 config.wsgi:application
```

5. Ejecutar Waitress en segundo plano (PowerShell):

```powershell
Start-Process -NoNewWindow -FilePath "waitress-serve" -ArgumentList "--port=8000 config.wsgi:application"

# o como job en segundo plano
Start-Job -ScriptBlock { & waitress-serve --port=8000 config.wsgi:application }
```

Alternativa (desarrollo): usar el servidor de desarrollo de Django (no recomendado para carga real):

```powershell
python manage.py runserver 0.0.0.0:8000
```

Alternativa ASGI (si tu proyecto usa ASGI en vez de WSGI):

```powershell
pip install uvicorn
uvicorn config.asgi:application --host 0.0.0.0 --port 8000
```

Con el backend en http://localhost:8000 puedes ejecutar los comandos k6 indicados abajo.

## Modo liviano (recomendado para pruebas rápidas)

Desde la raíz del proyecto:

```powershell
cd performance/k6
# Test rápido: 10 VUs por 1 minuto
k6 run --env USERNAME=admin_bd --env PASSWORD=Password123! --vus 10 --duration 1m performance/k6/k6-per-vu.js
```

Guardar resultados en JSON:

```powershell
k6 run --out json=performance/k6/resultados.json --env USERNAME=admin_bd --env PASSWORD=Password123! --vus 10 --duration 1m performance/k6/k6-per-vu.js
```

## Modo completo (Grafana + InfluxDB)

1. Levantar InfluxDB + Grafana (desde `performance/k6`):

```powershell
cd performance/k6
docker compose up -d
Start-Sleep -Seconds 15  # espera a que inicie InfluxDB/Grafana
```

2. Ejecutar k6 enviando datos a InfluxDB:

```powershell
k6 run --out influxdb=http://localhost:8086/k6 --env USERNAME=admin_bd --env PASSWORD=Password123! --vus 50 --iterations 100 performance/k6/k6-per-vu.js
```

3. Abrir Grafana en http://localhost:3000 (usuario `admin` / `admin`) y usar **Explore** para consultar métricas.

Métricas útiles: `http_req_duration`, `http_reqs`, `http_req_failed`, `vus`.

## Comandos de ejemplo listos para copiar

- Prueba realista (50 VUs, 100 iteraciones):

```powershell
k6 run --env USERNAME=admin_bd --env PASSWORD=Password123! --vus 50 --iterations 100 performance/k6/k6-per-vu.js
```

- Prueba alta concurrencia (100 VUs, 100 iteraciones):

```powershell
k6 run --env USERNAME=admin_bd --env PASSWORD=Password123! --vus 100 --iterations 100 performance/k6/k6-loadtest.js
```

- Guardar resultados en JSON (ejemplo personalizado):

```powershell
k6 run --env USERNAME=admin_bd --env PASSWORD=Password123! --vus 25 --duration 2m --out json=performance/k6/resultados_custom.json performance/k6/k6-per-vu.js
$env:DURATION = '2m'
$env:TARGET_PATH = '/api/v1/estudiantes/'
```


## Interpretación básica de métricas

- `http_req_duration`: latencia por request (ms)
- `http_reqs`: requests por segundo (RPS)
- `http_req_failed`: % de requests fallidos
- `iterations`: ciclos completados
- `vus`: usuarios virtuales activos

Reglas rápidas:

- p95 latencia < 500 ms — bueno
- RPS > 10 — throughput aceptable
- Error rate < 1% — confiable

## Solución de problemas rápida

| Error | Causa | Solución |
|---|---|---|
| `Connection refused` | Backend no está corriendo | Levantar Django/Waitress: `waitress-serve config.wsgi:application` |
| `401 Unauthorized` | Credenciales incorrectas | Usa `admin_bd` / `Password123!` en los env vars |
| `InfluxDB connection failed` | Docker no está activo | `docker compose up -d` en `performance/k6` |
| `Timeout 60s` | Servidor sobrecargado | Reduce `--vus` o incrementa `--duration` |
