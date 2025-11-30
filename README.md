# Workshop Final Lógica 3

Guía rápida para clonar el proyecto, crear el entorno virtual y ejecutar los ejemplos de manejo, recomendación y análisis de documentos.

## Requisitos
- Python 3.9+ (se usa solo librería estándar).

## Clonar y preparar el entorno
1. Clona el repo y entra a la carpeta:
   ```bash
   git clone <URL_DEL_REPO>
   cd workshop_final_logica_3
   ```
2. Crea el entorno virtual en la raíz:
   ```bash
   python3 -m venv .venv
   ```
3. Activa el entorno virtual:
   - macOS/Linux:
     ```bash
     source .venv/bin/activate
     ```
   - Windows (PowerShell):
     ```powershell
     .\.venv\Scripts\Activate.ps1
     ```
4. (Opcional) Actualiza `pip` dentro del entorno virtual:
   ```bash
   pip install --upgrade pip
   ```

## Ejecución de ejemplos
- `w1/main.py`: gestor integrado (hash + recomendaciones + generación de datos). Genera `data.json` con 2000 documentos y muestra búsqueda/sugerencias.
  ```bash
  python3 w1/main.py
  ```

- `w1_v2/main.py`: versión conceptual que muestra tabla hash, búsqueda y recomendaciones aleatorias.
  ```bash
  python3 w1_v2/main.py
  ```

- `w2/main.py`: simulación de stream con Bloom Filter, sampling, conteo exacto, momentos de frecuencia y DGIM.
  ```bash
  python3 w2/main.py
  ```

- `w3/main.py`: generación avanzada de documentos con matrices de Markov, PageRank, tiempos de mezcla y prueba de 2-SAT.
  ```bash
  python3 w3/main.py
  ```

- `w4/main.py`: demostración de MapReduce paralelo usando multiprocessing (conteo, promedio, join y análisis de costos/performance).
  ```bash
  python3 w4/main.py
  ```

## Notas
- El archivo de datos generado (`data.json`) está listado en `.gitignore` para evitar subirlo al repo.
- Mantén activado el entorno virtual cuando ejecutes los scripts. Si cierras la terminal, vuelve a activarlo antes de correrlos. 
