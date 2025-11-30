# Unidad 1 – Hashing y Algoritmos Aleatorizados

## Contexto del problema
Exercise 12: Automated Document Sorting and Retrieval System. Queremos almacenar y recuperar documentos rápido, ordenarlos por relevancia y sugerir contenidos de forma personalizada. Estrategia: usar hashing (O(1) esperado), índice invertido para búsquedas por palabra, y algoritmos aleatorizados para ordenar y recomendar según historial.

## Teoría clave
- Hashing con chaining para inserción/lectura O(1) esperado (Hashing Theory, clases 4–5).
- Índice invertido: palabra → documentos; reduce la búsqueda a O(1)+O(k).
- Algoritmos aleatorizados: pivote aleatorio en quicksort y muestreo ponderado para recomendaciones (clase 3).
- Tracking: `access_count` y `lastAccessed` para personalizar resultados y sugerencias.

## Componentes del algoritmo
- `Document`: metadatos, acceso, score de relevancia.
- `HashTable`: almacenamiento por `_id` con chaining.
- `InvertedIndex`: tokens de título/contenido/tags para búsqueda rápida.
- `DocumentSystem`: generación de 2000 docs, búsqueda por relevancia, comparación índice vs lineal, recomendaciones, estadísticas.

## Flujo de ejecución (demo)
1) Generar 2000 documentos (`generate_dummy_data`).
2) Recuperar por ID (O(1)).
3) Buscar keyword: calcular score (título/tags/contenido + popularidad), ordenar (quicksort aleatorio), comparar índice invertido vs búsqueda lineal.
4) Simular interacciones (búsquedas adicionales, accesos).
5) Recomendaciones: historial reciente + popularidad + muestreo aleatorio ponderado.
6) Estadísticas: búsquedas totales, keywords únicas, documentos accedidos, más accedidos.

## Requerimientos cubiertos
- “Store/manage in hash table”: `HashTable` para O(1) esperado.
- “Search by keywords, organized results”: índice invertido + score de relevancia.
- “Randomized recommendations”: muestreo ponderado con historial.
- “Track interactions”: `access_count`, `lastAccessed`, historial y estadísticas.
- Generación de datos conforme al template: `_id`, `title`, `content`, `tags`, `lastAccessed`.

## Archivos clave
- `w1/main.py`: implementación y demo.
- `w1/data.json`: datos generados automáticamente (ignorados en git).

## Cómo correr
```bash
python3 w1/main.py
```

## Notas rápidas
- `lastAccessed` formateado como `YYYY-MM-ddThh:mm:ss +0000`.
- Índice invertido usa título, contenido y tags en minúsculas.

## Sugerencias para la exposición
- Muestra breve de salida: generación de docs, recuperación por ID, comparación índice vs lineal, top 5 resultados, recomendaciones y estadísticas.
- Simplificaciones: relevancia por pesos fijos y popularidad; recomendaciones con muestreo simple; sin persistencia de búsquedas más allá de la sesión.
