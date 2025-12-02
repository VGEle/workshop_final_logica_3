# Unidad 2 – Stream Processing (Bloom, Sampling, DGIM)

## Contexto del problema
Exercise 12: Automated Document Sorting and Retrieval System (stream). Objetivo: procesar eventos de búsqueda/recuperación en línea, detectar contenido visto recientemente, muestrear usuarios para optimizar rutas, contar accesos y estimar actividad en ventana temporal.

## Teoría clave
- Bloom Filter en streams: múltiples hashes + ventana de recencia.
- Behavior Sampling: hash consistente + umbral dinámico para seleccionar usuarios.
- Distinct Counting exacto: sets y contadores por usuario.
- Frequency Moments (F1): suma de frecuencias = longitud del stream.
- DGIM: buckets potencias de 2 en ventana deslizante.

## Qué hace y qué requisitos cumple
- **Bloom con recencia**: tres hashes sobre firma tipo+bucket de frecuencia; detecta si se vio en los últimos pasos.
- **Sampling**: hash/umbral para aceptar usuarios y asignar ruta prioritaria o normal; reduce umbral si la muestra crece.
- **Distinct Counting**: tipos únicos y contador exacto de documentos por usuario.
- **F1**: acumula `searchFrequency` de todos los eventos.
- **DGIM**: ventana 32, buckets con fusión de 3 iguales; bit=1 por llegada para estimar búsquedas recientes.

## Archivos clave
- `w2/main.py`: simulación de 10 eventos de stream.

## Cómo correr
```bash
python3 w2/main.py
```

## Orden de ejecución (stream)
- Secuencia por evento (bucle en línea ~220): Bloom → Sampling → Conteo exacto → F1 → DGIM. Se repite 10 veces.

