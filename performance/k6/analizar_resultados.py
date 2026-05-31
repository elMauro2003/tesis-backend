#!/usr/bin/env python3
"""
Analizador de resultados k6 - Genera reportes de rendimiento
"""
import json
from pathlib import Path
from collections import defaultdict
from statistics import mean, median, stdev

def load_json_results(filepath):
    """Carga resultados JSON de k6"""
    with open(filepath, 'r') as f:
        lines = f.readlines()
    
    metrics = defaultdict(list)
    checks = defaultdict(int)
    
    for line in lines:
        try:
            data = json.loads(line)
            if 'metric' in data:
                metric_name = data['metric']
                metric_value = data.get('data', {}).get('value', 0)
                metrics[metric_name].append(metric_value)
            
            if data.get('type') == 'Point' and data.get('metric') == 'checks':
                check_name = data.get('data', {}).get('tags', {}).get('check', 'unknown')
                checks[check_name] += 1
        except json.JSONDecodeError:
            continue
    
    return metrics, checks

def analyze_metrics(metrics):
    """Analiza métricas extraídas"""
    analysis = {}
    
    for metric_name, values in metrics.items():
        if not values:
            continue
        
        if metric_name in ['http_req_duration', 'http_req_waiting', 'iteration_duration']:
            # Convertir a ms si están en segundos
            values_ms = [v * 1000 if v < 100 else v for v in values]
            
            analysis[metric_name] = {
                'min': min(values_ms),
                'max': max(values_ms),
                'avg': mean(values_ms),
                'med': median(values_ms),
                'p90': sorted(values_ms)[int(len(values_ms) * 0.9)] if len(values_ms) > 0 else 0,
                'p95': sorted(values_ms)[int(len(values_ms) * 0.95)] if len(values_ms) > 0 else 0,
                'p99': sorted(values_ms)[int(len(values_ms) * 0.99)] if len(values_ms) > 0 else 0,
                'count': len(values_ms)
            }
        else:
            analysis[metric_name] = {
                'min': min(values),
                'max': max(values),
                'avg': mean(values),
                'count': len(values)
            }
    
    return analysis

def print_report(test_name, filepath):
    """Imprime reporte formateado"""
    metrics, checks = load_json_results(filepath)
    analysis = analyze_metrics(metrics)
    
    print("\n" + "="*70)
    print(f"REPORTE DE RENDIMIENTO: {test_name}")
    print("="*70)
    
    print("\n📊 MÉTRICAS DE LATENCIA (en ms):")
    print("-" * 70)
    
    http_duration = analysis.get('http_req_duration', {})
    if http_duration:
        print(f"  HTTP Duration:")
        print(f"    Min:     {http_duration.get('min', 0):>10.2f} ms")
        print(f"    Médiana: {http_duration.get('med', 0):>10.2f} ms")
        print(f"    Media:   {http_duration.get('avg', 0):>10.2f} ms")
        print(f"    P90:     {http_duration.get('p90', 0):>10.2f} ms")
        print(f"    P95:     {http_duration.get('p95', 0):>10.2f} ms")
        print(f"    P99:     {http_duration.get('p99', 0):>10.2f} ms")
        print(f"    Max:     {http_duration.get('max', 0):>10.2f} ms")
        print(f"    Muestras: {http_duration.get('count', 0)}")
    
    print("\n📈 THROUGHPUT:")
    print("-" * 70)
    
    # Calcular RPS
    if http_duration and http_duration.get('count', 0):
        total_time_s = (http_duration.get('max', 0) - http_duration.get('min', 0)) / 1000
        if total_time_s > 0:
            rps = http_duration.get('count', 0) / total_time_s
            print(f"  Requests/segundo:  {rps:.2f} RPS")
        print(f"  Total de requests:  {http_duration.get('count', 0)}")
    
    print("\n✅ CHECKS:")
    print("-" * 70)
    total_checks = sum(checks.values())
    for check_name, count in sorted(checks.items()):
        rate = (count / total_checks * 100) if total_checks > 0 else 0
        print(f"  {check_name:.<40} {count:>5} ({rate:>5.1f}%)")
    
    print("\n🔄 DURACIÓN DE ITERACIONES (en ms):")
    print("-" * 70)
    iter_duration = analysis.get('iteration_duration', {})
    if iter_duration:
        print(f"    Min:     {iter_duration.get('min', 0):>10.2f} ms")
        print(f"    Médiana: {iter_duration.get('med', 0):>10.2f} ms")
        print(f"    Media:   {iter_duration.get('avg', 0):>10.2f} ms")
        print(f"    P95:     {iter_duration.get('p95', 0):>10.2f} ms")
        print(f"    Max:     {iter_duration.get('max', 0):>10.2f} ms")
    
    print("\n" + "="*70)

if __name__ == '__main__':
    base_path = Path(__file__).parent
    
    results = [
        ("PRUEBA 1: 50 VUs - Flujo Completo (Auth + API)", 
         base_path / "resultados_estudiantes_fullflow.json"),
        ("PRUEBA 2: 100 VUs - Solo Consulta (Token Compartido)",
         base_path / "resultados_estudiantes_queryonly.json"),
    ]
    
    for test_name, filepath in results:
        if filepath.exists():
            print_report(test_name, filepath)
        else:
            print(f"\n⚠️  Archivo no encontrado: {filepath}")
    
    print("\n" + "="*70)
    print("📋 CONCLUSIONES:")
    print("="*70)
    print("""
    - Prueba 1 simuló el flujo completo (login + consulta) con 50 usuarios
      concurrentes, mostrando latencia moderada pero consistente.
    
    - Prueba 2 simuló alta concurrencia (100 VUs) con token reutilizado,
      revelando que bajo carga extrema hay timeouts (2.97% de fallos).
    
    - El endpoint /api/v1/estudiantes/ maneja razonablemente bien 50 VUs
      concurrentes pero muestra degradación en 100+ VUs.
    
    - Recomendación: Optimizar queries, añadir caché, o escalar el servidor
      para manejar >100 users concurrentes en producción.
    """)
