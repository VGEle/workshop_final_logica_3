# Unidad 2 – Stream Processing (Bloom, Sampling, DGIM)

## Qué hace y qué requisitos cumple
- **Bloom Filter con recencia**: dos hashes sobre firma de tipo+bucket de frecuencia; marca bits y detecta si se vio en los últimos pasos (teoría de filtros de Bloom en streams).
- **Behavior-based Sampling**: hash consistente y umbral dinámico para aceptar usuarios; asigna ruta prioritaria/normal, optimizando la ruta de recuperación de forma simple.
- **Distinct Counting exacto**: set de tipos por usuario + contador exacto de documentos accedidos (no aproximado).
- **Frequency Moment F1**: suma total de `searchFrequency` del stream (momento 1 en análisis de streams).
- **DGIM**: ventana de 32, cubetas potencias de 2, fusión de 3 cubetas iguales; cuenta eventos (bit=1 por llegada) en la ventana deslizante.

## Archivos clave
- `w2/main.py`: simulación completa de 10 eventos de stream.

## Cómo correr
```bash
python3 w2/main.py
```

## Notas rápidas
- El Bloom usa dos hashes simples sobre la firma del tipo.
- El muestreo reduce el umbral si la muestra crece más que el límite.
- DGIM usa ventana de 32 pasos; se imprime el estado de cubetas tras cada 1.

## Orden de ejecución (stream)
- Archivo: `w2/main.py`.
- Secuencia por cada evento (bucle en línea 220): Bloom (`procesar_bloom`) → Sampling (`procesar_muestreo`) → Conteo exacto (`procesar_conteo_exacto`) → Momento 1 (`procesar_momento_uno`) → DGIM (`procesar_dgim`). Se repite 10 veces.
