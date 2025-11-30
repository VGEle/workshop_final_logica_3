# Unidad 1 – Hashing y Algoritmos Aleatorizados

## Qué hace y qué requisitos cumple
- **Tabla hash + hashing theory**: guarda documentos en un dict (chaining implícito) para inserción/lectura O(1) esperado, alineado con la teoría de hashing uniforme (clases 4–5).
- **Búsqueda y ordenamiento por relevancia**: índice invertido sobre título/contenido/tags; puntaje por frecuencia de palabras + bono de historial → resultados organizados por relevancia.
- **Algoritmo aleatorizado de recomendación**: `random.choices` ponderado por interacciones previas (concepto de algoritmos aleatorizados de clase 3).
- **Seguimiento de interacciones**: registra accesos por usuario y actualiza `lastAccessed` (formato del template); historial se usa para personalizar.
- **Generación de datos**: crea 2000 documentos con `_id`, `title`, `content`, `tags`, `lastAccessed` conforme al template JSON de la unidad.

## Archivos clave
- `w1/main.py`: clase `DocumentRecommender` y ejemplo de uso.
- `w1/data.json`: datos generados automáticamente (ignorados en git).

## Cómo correr
```bash
python3 w1/main.py
```

## Notas rápidas
- `record_interaction` actualiza `lastAccessed` en formato `YYYY-MM-ddThh:mm:ss +0000`.
- El índice invertido usa título, contenido y tags en minúsculas.

## Orden de ejecución (main)
- Archivo: `w1/main.py`, línea del bloque principal: 258.
- Secuencia: carga/genera documentos → instancia `DocumentRecommender` → búsqueda (`search`) → registra interacción (`record_interaction`) → sugerencias (`suggest`).
