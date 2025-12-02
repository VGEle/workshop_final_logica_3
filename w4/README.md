# Unidad 4 – MapReduce (Conteo, Promedio, Join, Costos, Performance)

## Contexto del problema
Exercise 12: Automated Document Sorting and Retrieval System (MapReduce). Objetivo: procesar grandes volúmenes de documentos de forma distribuida para contar, agregar, unir metadatos, estimar costos y medir performance con paralelismo.

## Qué hace y qué requisitos cumple
- **Algoritmo 1 (contar tipos)**: map (documentType, 1), reduce suma → tipos más comunes.
- **Algoritmo 2 (promedio por departamento)**: map (department, fileSizeMB), reduce promedio → tamaños por área.
- **Algoritmo 3 (join básico)**: combina documentos con usuarios para reportes por autor/dep.
- **Algoritmo 4 (costos)**: calcula GB totales y costo estimado por PB; ilustración de análisis de costos.
- **Algoritmo 5 (performance)**: mide tiempo del conteo en subset vs dataset completo para mostrar efecto de volumen; usa multiprocessing para paralelizar la fase MAP.
- **Campos MapReduce**: añade `mapReducePartition`, `processingNode`, `batchId`, `aggregationKey` a los documentos (mantiene los campos de la U3 si existen).

## Archivos clave
- `w4/main.py`: generador (carga de w3 si existe) y ejecución de los 5 algoritmos.

## Cómo correr
```bash
python3 w4/main.py
```

## Notas rápidas
- Genera o carga 1000 documentos y agrega campos de MapReduce (`mapReducePartition`, `processingNode`, `batchId`, `aggregationKey`).
- El join combina `authorId` con `user_id` para armar reportes.
- La fase reduce agrupa con `defaultdict` y aplica la función reduce que corresponda.

## Orden de ejecución (main)
- Archivo: `w4/main.py`, bloque principal en línea 189.
- Secuencia: carga/genera docs → Algoritmo 1 (conteo) → Algoritmo 3 (join) → Algoritmo 4 (costos) → Algoritmo 5 (performance en subset y completo). Algoritmo 2 está definido pero no se llama en el flujo; puedes invocarlo si lo necesitas.
