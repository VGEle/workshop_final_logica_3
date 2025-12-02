# Unidad 3 – Markov y Optimización de Flujo

## Contexto del problema
Exercise 12: Automated Document Sorting and Retrieval System (flujo). Objetivo: modelar estados de procesamiento con cadenas de Markov, optimizar rutas de recuperación con random walks y detectar cuellos de botella en el workflow.

## Teoría clave
- Cadenas de Markov: matriz de transición estocástica, estados absorbentes/transientes.
- Distribución estacionaria y mixing time (iteración de potencia).
- PageRank (Google matrix con damping).
- Random walks: rutas probables, hitting/cover time.
- Algoritmos aleatorizados: demo de 2-SAT como extra.

## Qué hace y qué requisitos cumple
- **Cadena de Markov de estados**: 5 estados (received, classified, processed, archived absorbente, retrieved) con matriz 5x5 dependiente de prioridad (transiciones basadas en parámetro).
- **Distribución estacionaria y mixing**: power iteration para carga a largo plazo y tiempo de mezcla simple.
- **PageRank**: cálculo con damping sobre la matriz de estados (Google matrix).
- **Random walks y rutas**: genera `searchPath` con random walk sobre matriz de categorías y calcula hitting/cover para eficiencia de recuperación.
- **Detección de cuellos de botella**: compara carga estacionaria vs throughput simulado para marcar `processingBottleneck`.
- **JSON enriquecido**: 2000 docs por defecto con todos los campos del template; mantiene `lastAccessed` en formato `YYYY-MM-ddThh:mm:ss Z`; incluye prueba 2-SAT como extra de algoritmos aleatorizados.

## Archivos clave
- `w3/main.py`: generador de documentos con análisis de Markov y ejemplo 2-SAT.
- `w3/document_data_v2.json`: salida con 2000 documentos (generado al correr).

## Cómo correr
```bash
python3 w3/main.py
```

## Notas rápidas
- Estados: received, classified, processed, archived (absorbente), retrieved.
- Prioridad ajusta probabilidad de avance (low a urgent).
- `searchPath` se genera con random walk sobre la matriz de categorías.
- `lastAccessed` se formatea como `YYYY-MM-ddThh:mm:ss Z`.

## Orden de ejecución (main)
- Archivo: `w3/main.py`, bloque principal en línea 295.
- Secuencia: instancia generador → define `NUM_DOCS` (=2000) → genera dataset (`generate_dataset`) → guarda JSON → imprime muestra del primer documento → ejecuta prueba 2-SAT.


