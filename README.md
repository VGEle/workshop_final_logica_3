# Workshop Final Lógica 3

Guía rápida para clonar el proyecto, crear el entorno virtual y ejecutar los ejemplos de manejo, recomendación y análisis de documentos.

## Requisitos
- Python 3.9+ (se usa solo librería estándar).
- Dependencias opcionales: `faker` si deseas ejecutar `w1/data_generation.py`.

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
4. Instala dependencias opcionales solo si usarás `w1/data_generation.py`:
   ```bash
   pip install faker
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

- `w1/data_generation.py` (opcional, requiere `faker`): genera `w1/documents_data.json` con 2000 documentos ficticios.
  ```bash
  python3 w1/data_generation.py
  ```

- `w2/main.py`: simulación de stream con Bloom Filter, sampling, conteo exacto, momentos de frecuencia y DGIM.
  ```bash
  python3 w2/main.py
  ```

- `w3/main.py`: generación avanzada de documentos con matrices de Markov, PageRank, tiempos de mezcla y prueba de 2-SAT.
  ```bash
  python3 w3/main.py
  ```

## Notas
- Los archivos de datos (`data.json`, `documents_data.json`) están listados en `.gitignore` para evitar subirlos al repo.
- Mantén activado el entorno virtual cuando ejecutes los scripts. Si cierras la terminal, vuelve a activarlo antes de correrlos. 
