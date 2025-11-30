import random
import time
from collections import defaultdict
import multiprocessing  # Librería para paralelismo real

# ==========================================
# PARTE 0: GENERADOR DE DATOS (MOCK DATA)
# ==========================================
def generar_datos_simulados():
    print("--- Generando 1,000 registros simulados... ---")
    
    usuarios = []
    departamentos = ["IT", "HR", "Sales", "Finance", "Legal"]
    for i in range(1, 51):
        usuarios.append({
            "user_id": f"user_{i:03d}",
            "name": f"Empleado {i}",
            "department": random.choice(departamentos)
        })

    documentos = []
    tipos = ["PDF", "Word", "Excel", "PowerPoint"]
    
    for i in range(1, 1001):
        doc_type = random.choice(tipos)
        dept = random.choice(departamentos)
        
        doc = {
            "document_id": f"doc_{i:04d}",
            "document_type": doc_type,
            "department": dept,
            "file_size_mb": random.uniform(0.5, 50.0),
            "author_id": f"user_{random.randint(1, 50):03d}",
            "mapReducePartition": random.randint(1, 25),
            "processingNode": f"node_{random.randint(1, 12)}",
            "batchId": f"batch_{random.randint(1000, 9999)}",
            "aggregationKey": f"{doc_type}_{dept}"
        }
        documentos.append(doc)
        
    return documentos, usuarios

# ==========================================
# EL MOTOR MAP-REDUCE (VERSIÓN PARALELA REAL)
# ==========================================

# Esta función auxiliar es necesaria para que multiprocessing funcione bien
# Simplemente desempaqueta los argumentos para la función map
def _worker_map_wrapper(args):
    funcion, dato = args
    return funcion(dato)

def motor_map_reduce_paralelo(datos_entrada, funcion_map, funcion_reduce):
    """
    Motor que usa TODOS los núcleos de la CPU para la fase MAP.
    """
    print(f"    Iniciando motor paralelo con {multiprocessing.cpu_count()} núcleos de CPU...")
    inicio = time.time()

    # --- PASO 1: FASE MAP PARALELA ---
    # Preparamos los argumentos para enviarlos a los procesadores
    # Es como preparar las cajas para cada pintor
    tareas_map = [(funcion_map, dato) for dato in datos_entrada]

    # Creamos una 'piscina' (Pool) de procesos obreros
    # Python detecta automáticamente cuántos núcleos tiene tu PC
    with multiprocessing.Pool() as pool:
        # pool.map reparte las tareas entre los núcleos disponibles
        resultados_crudos = pool.map(_worker_map_wrapper, tareas_map)

    # Filtramos resultados vacíos (si los hubo)
    pares_intermedios = [r for r in resultados_crudos if r is not None]

    # --- PASO 2: FASE SHUFFLE (Agrupación) ---
    # Esto usualmente lo hace el nodo maestro (tu proceso principal)
    grupos = defaultdict(list)
    for clave, valor in pares_intermedios:
        grupos[clave].append(valor)
    
    # --- PASO 3: FASE REDUCE ---
    # Procesamos los resultados consolidados
    resultados_finales = {}
    for clave, lista_de_valores in grupos.items():
        resultados_finales[clave] = funcion_reduce(clave, lista_de_valores)
        
    fin = time.time()
    print(f"    Tiempo de ejecución: {fin - inicio:.4f} segundos")
    return resultados_finales

# ==========================================
# FUNCIONES MAP Y REDUCE (LÓGICA DEL NEGOCIO)
# ==========================================

# --- ALGORITMO 1: CONTADOR ---
def map_1_contador(documento):
    # Simulamos un pequeño retraso para que se note la diferencia de velocidad
    # en el paralelismo (sino es demasiado rápido)
    time.sleep(0.001) 
    return (documento['document_type'], 1)

def reduce_1_contador(clave, lista_de_unos):
    return sum(lista_de_unos)

# --- ALGORITMO 2: PROMEDIO ---
def map_2_promedio(documento):
    return (documento['department'], documento['file_size_mb'])

def reduce_2_promedio(clave, lista_tamanos):
    if not lista_tamanos: return 0
    return round(sum(lista_tamanos) / len(lista_tamanos), 2)

# --- ALGORITMO 3: JOIN ---
def algoritmo_3_join_setup(documentos, usuarios):
    todos_los_datos = []
    for d in documentos: todos_los_datos.append( ('DATA', d) ) 
    for u in usuarios: todos_los_datos.append( ('USER', u) )
    return todos_los_datos

def map_join(registro_bruto):
    tipo_origen, data = registro_bruto
    if tipo_origen == 'DATA':
        return (data['author_id'], ('DOC', data['document_id'], data['document_type']))
    elif tipo_origen == 'USER':
        return (data['user_id'], ('USER_INFO', data['name']))

def reduce_join(user_id, lista_valores):
    nombre_usuario = "Desconocido"
    docs_del_usuario = []
    for val in lista_valores:
        if val[0] == 'USER_INFO': nombre_usuario = val[1]
        elif val[0] == 'DOC': docs_del_usuario.append(val[1])
    return f"Usuario: {nombre_usuario} | Total Docs: {len(docs_del_usuario)}"

# ==========================================
# ALGORITMOS DE ANÁLISIS (4 y 5)
# ==========================================
def algoritmo_4_costos(documentos):
    print("\n--- Algoritmo 4: Costos ---")
    total_gb = sum(d['file_size_mb'] for d in documentos) / 1024
    print(f"Total Almacenado: {total_gb:.2f} GB | Costo Est. Petabyte: ${1_000_000 * 0.023:,.2f}")

def algoritmo_5_performance():
    print("\n--- Algoritmo 5: Análisis de Performance (Simulado) ---")
    print("Nodos | Speedup Teórico")
    for n in [1, 2, 4, 8]:
        print(f"{n:<5} | {n:<5}x (Ideal)")

# ==========================================
# MAIN
# ==========================================
if __name__ == "__main__":
    # IMPORTANTE: En Windows, multiprocessing necesita estar protegido por este if
    
    docs, users = generar_datos_simulados()
    
    print("\n" + "="*50)
    print("INICIANDO DEMOSTRACIÓN DE PARALELISMO REAL")
    print("="*50)

    # --- DEMO ALGORITMO 1 (PARALELO) ---
    print("\n1) Ejecutando Algoritmo 1 (Conteo) en PARALELO...")
    res1 = motor_map_reduce_paralelo(docs, map_1_contador, reduce_1_contador)
    print(f"   Resultado parcial: PDF -> {res1.get('PDF', 0)}")

    # --- DEMO ALGORITMO 3 (JOIN PARALELO) ---
    print("\n3) Ejecutando Algoritmo 3 (Join) en PARALELO...")
    datos_join = algoritmo_3_join_setup(docs, users)
    # Usamos la misma función map_join definida arriba
    res3 = motor_map_reduce_paralelo(datos_join, map_join, reduce_join)
    print("   Ejemplo de reporte generado:")
    print(f"   {list(res3.values())[0]}")

    algoritmo_4_costos(docs)
    algoritmo_5_performance()
    
    print("\nDemostración completada usando MÚLTIPLES NÚCLEOS.")
