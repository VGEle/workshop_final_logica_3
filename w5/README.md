# Unidad 5 – Búsqueda de Vecinos Cercanos (KNN)

## Qué hace y qué requisitos cumple
- **Algoritmo 1 (similitud básica)**: KNN con distancia euclidiana sobre `accessMetrics`+`documentSize` (frecuencia/tamaño).
- **Algoritmo 2 (por categoría)**: filtra por `documentType` y `department` y aplica distancia sobre `accessMetrics` (categorical KNN).
- **Algoritmo 3 (patrón de usuario)**: KNN por `userAccessPattern` usando diferencia absoluta.
- **Algoritmo 4 (efectividad)**: evalúa coincidencia de tipo tras filtrar por `documentType` (precisión simple).
- **Algoritmo 5 (agrupación)**: asigna grupo por voto del departamento de los vecinos cercanos (clustering sencillo).

## Datos
- Carga documentos de `w3/document_data_v2.json` si existe; si no, genera datos de ejemplo.
- Añade bloque `documentSimilarity` con métricas y categorías para los algoritmos KNN.
- Usa `random.seed(42)` y 1000 documentos por defecto para reproducibilidad; puedes ajustar `doc_count` si quieres menos salida.

## Cómo correr
```bash
python3 w5/main.py
```

## Notas rápidas
- Cambia `doc_count` o quita la semilla si necesitas más aleatoriedad.
- Los vecinos y agrupaciones dependen de las métricas generadas; los resultados son deterministas con la semilla actual.

## Orden de ejecución (main)
- Archivo: `w5/main.py`, bloque principal en línea 311.
- Secuencia: fija semilla → carga/genera docs (`load_or_generate_documents`) → Algoritmo 1 (similitud básica) → Algoritmo 2 (categoría) → Algoritmo 3 (patrón usuario) → Algoritmo 4 (efectividad) → Algoritmo 5 (agrupación).
