"""
Unidad 5: Búsqueda de vecinos cercanos (KNN) para similitud de documentos,
categorías, patrones de usuario, efectividad y agrupación.
"""

import json
import math
import random
from pathlib import Path

# ==========================================
# PASO 0: CARGA O GENERACIÓN DE DATOS
# ==========================================
def load_or_generate_documents(count=1000):
    """
    Carga documentos de la unidad anterior (w3/document_data_v2.json) si existen.
    Si no, genera datos simples. En ambos casos añade el bloque documentSimilarity.
    """
    base_path = Path("w3/document_data_v2.json")
    types = ["report", "manual", "policy", "training"]
    departments = ["HR", "Finance", "Engineering", "Marketing"]

    if base_path.exists():
        with base_path.open() as f:
            data = json.load(f)[:count]
    else:
        data = []
        for i in range(count):
            data.append(
                {
                    "_id": f"doc_{i:04d}",
                    "title": f"Document {i}",
                    "content": "Contenido simulado",
                    "documentType": random.choice(types),
                    "department": random.choice(departments),
                    "fileSizeMB": random.uniform(0.5, 50.0),
                }
            )

    enriched = []
    for idx, doc in enumerate(data):
        sim_block = doc.get("documentSimilarity", {})
        # Valores base o aleatorios
        doc_type = sim_block.get("documentType") or doc.get("documentType") or random.choice(types)
        dept = sim_block.get("department") or doc.get("department") or random.choice(departments)
        document_size = sim_block.get("documentSize") or doc.get("documentSize") or random.randint(10, 500)
        access_metrics = sim_block.get("accessMetrics") or [random.randint(1, 50) for _ in range(4)]
        relevance = sim_block.get("relevanceScore") or round(random.uniform(0.3, 1.0), 2)
        user_pattern = sim_block.get("userAccessPattern") or round(random.uniform(0.1, 1.0), 2)

        # Asegurar identificador y nombre amigable
        doc_id = doc.get("_id") or doc.get("id") or f"doc_{idx:04d}"
        doc_name = doc.get("title") or doc.get("name") or f"Document_{idx}"

        doc["id"] = idx
        doc["_id"] = doc_id
        doc["name"] = doc_name
        doc["documentType"] = doc_type
        doc["department"] = dept
        doc["documentSimilarity"] = {
            "accessMetrics": access_metrics,
            "documentType": doc_type,
            "department": dept,
            "documentSize": document_size,
            "relevanceScore": relevance,
            "userAccessPattern": user_pattern,
        }
        enriched.append(doc)

    return enriched

# ==========================================
# HERRAMIENTAS MATEMÁTICAS (TEORÍA)
# ==========================================

def calculate_euclidean_distance(vector1, vector2):
    """
    Calcula la Distancia Euclidiana (L2-Norm) entre dos listas de números.
    Teoría: Raíz cuadrada de la suma de las diferencias al cuadrado.
    Fórmula: sqrt(sum((x_i - y_i)^2))
    """
    # Validamos que los vectores tengan la misma longitud
    if len(vector1) != len(vector2):
        raise ValueError("Los vectores deben tener la misma longitud")
    
    squared_diff_sum = 0
    for i in range(len(vector1)):
        diff = vector1[i] - vector2[i]
        squared_diff_sum += diff ** 2
        
    return math.sqrt(squared_diff_sum)

# ==========================================
# ALGORITMO 1: SIMILITUD BÁSICA (SIMPLE KNN)
# ==========================================
# Requisito: Buscar documentos con frecuencia de acceso y características básicas similares.
# Métrica: Distancia Euclidiana sobre 'accessMetrics' y 'documentSize'.

def algorithm_1_basic_similarity(target_doc, all_docs, k=3):
    print(f"\n--- Ejecutando Algoritmo 1: Similitud Básica (K={k}) ---")
    print(f"Documento Objetivo: {target_doc['name']} (Size: {target_doc['documentSimilarity']['documentSize']})")
    
    distances = []
    
    # Preparamos el vector del documento objetivo
    # Vector = [metric1, metric2, metric3, metric4, size]
    target_vector = target_doc['documentSimilarity']['accessMetrics'] + [target_doc['documentSimilarity']['documentSize']]

    for doc in all_docs:
        # No nos comparamos con nosotros mismos (distancia sería 0)
        if doc['id'] == target_doc['id']:
            continue
            
        # Preparamos el vector del documento candidato
        candidate_vector = doc['documentSimilarity']['accessMetrics'] + [doc['documentSimilarity']['documentSize']]
        
        # Calculamos distancia euclidiana
        dist = calculate_euclidean_distance(target_vector, candidate_vector)
        
        # Guardamos el resultado: (distancia, documento)
        distances.append((dist, doc))
    
    # Ordenamos por distancia (menor es más similar) y tomamos los K primeros
    distances.sort(key=lambda x: x[0])
    neighbors = distances[:k]
    
    for dist, doc in neighbors:
        print(f"Vecino encontrado: {doc['name']} - Distancia: {dist:.4f}")
    
    return neighbors

# ==========================================
# ALGORITMO 2: EMPAREJAMIENTO POR TIPO (CATEGORY KNN)
# ==========================================
# Requisito: Encontrar documentos dentro de tipos y departamentos similares.
# Enfoque: Primero filtrar (agrupar) por categoría, luego comparar uso.

def algorithm_2_category_matching(target_doc, all_docs, k=3):
    print(f"\n--- Ejecutando Algoritmo 2: Emparejamiento por Categoría ---")
    target_type = target_doc['documentSimilarity']['documentType']
    target_dept = target_doc['documentSimilarity']['department']
    print(f"Objetivo: {target_doc['name']} - Tipo: {target_type}, Dept: {target_dept}")
    
    # Paso 1: Filtrado estricto (Categorical Feature)
    # Solo consideramos documentos que coincidan en Tipo Y Departamento
    filtered_docs = []
    for doc in all_docs:
        if doc['id'] == target_doc['id']:
            continue
            
        sim_data = doc['documentSimilarity']
        if sim_data['documentType'] == target_type and sim_data['department'] == target_dept:
            filtered_docs.append(doc)
            
    print(f"Documentos encontrados en la misma categoría: {len(filtered_docs)}")
    
    if not filtered_docs:
        print("No se encontraron vecinos en la misma categoría exacta.")
        return []

    # Paso 2: KNN sobre los filtrados usando accessMetrics
    distances = []
    target_metrics = target_doc['documentSimilarity']['accessMetrics']
    
    for doc in filtered_docs:
        candidate_metrics = doc['documentSimilarity']['accessMetrics']
        dist = calculate_euclidean_distance(target_metrics, candidate_metrics)
        distances.append((dist, doc))
        
    distances.sort(key=lambda x: x[0])
    neighbors = distances[:k]
    
    for dist, doc in neighbors:
        print(f"Vecino de misma categoría: {doc['name']} - Distancia de Uso: {dist:.4f}")
        
    return neighbors

# ==========================================
# ALGORITMO 3: PATRÓN DE ACCESO DE USUARIO (USAGE KNN)
# ==========================================
# Requisito: Buscar documentos con patrones de acceso de usuario similares.
# Métrica: Distancia simple (valor absoluto) sobre 'userAccessPattern'.

def algorithm_3_user_pattern(target_doc, all_docs, k=3):
    print(f"\n--- Ejecutando Algoritmo 3: Patrón de Usuario ---")
    target_pattern = target_doc['documentSimilarity']['userAccessPattern']
    print(f"Objetivo: {target_doc['name']} - Patrón Usuario: {target_pattern}")
    
    distances = []
    
    for doc in all_docs:
        if doc['id'] == target_doc['id']:
            continue
            
        candidate_pattern = doc['documentSimilarity']['userAccessPattern']
        
        # Calculamos la diferencia absoluta (distancia euclidiana 1D)
        dist = abs(target_pattern - candidate_pattern)
        distances.append((dist, doc))
        
    distances.sort(key=lambda x: x[0])
    neighbors = distances[:k]
    
    for dist, doc in neighbors:
        patt = doc['documentSimilarity']['userAccessPattern']
        print(f"Vecino: {doc['name']} - Patrón: {patt} - Diferencia: {dist:.4f}")

    return neighbors

# ==========================================
# ALGORITMO 4: EFECTIVIDAD DEL KNN
# ==========================================
# Requisito: Comparar la calidad de las coincidencias.
# Meta: Verificar si los vecinos encontrados comparten el mismo 'documentType' que el objetivo.

def algorithm_4_effectiveness_test(target_doc, all_docs, k=5):
    print(f"\n--- Ejecutando Algoritmo 4: Prueba de Efectividad ---")
    
    # Filtramos primero por tipo para exigir coherencia categórica
    target_type = target_doc['documentSimilarity']['documentType']
    filtered = [doc for doc in all_docs if doc['id'] != target_doc['id'] and doc['documentSimilarity']['documentType'] == target_type]
    
    if not filtered:
        print("No hay vecinos del mismo tipo para evaluar.")
        return 0.0

    # Usamos Algoritmo 1 (euclidiana sobre métricas numéricas) sobre el subconjunto
    neighbors = algorithm_1_basic_similarity(target_doc, filtered, k)
    
    matches = 0
    
    print(f"Evaluando consistencia de tipo. Tipo esperado: {target_type}")
    
    for dist, doc in neighbors:
        neighbor_type = doc['documentSimilarity']['documentType']
        is_match = (neighbor_type == target_type)
        match_str = "SI" if is_match else "NO"
        
        print(f"  Vecino {doc['name']} tiene tipo '{neighbor_type}'? {match_str}")
        
        if is_match:
            matches += 1
            
    accuracy = (matches / k) * 100
    print(f"Precisión del KNN (coincidencia de tipo): {accuracy}%")
    return accuracy

# ==========================================
# ALGORITMO 5: AGRUPACIÓN DE ORGANIZACIÓN (GROUPING)
# ==========================================
# Requisito: Agrupar documentos usando resultados de KNN.
# Enfoque: Asignar un documento a un 'Cluster' basado en el departamento mayoritario de sus vecinos.

def algorithm_5_organization_grouping(all_docs, k=3):
    print(f"\n--- Ejecutando Algoritmo 5: Agrupación Organizacional ---")
    print("Clasificando documentos basado en sus vecinos más cercanos (Métricas de acceso)...")
    
    for i, doc in enumerate(all_docs[:5]): # Limitamos a 5 para no saturar la terminal
        # Obtenemos vecinos usando Algoritmo 1 (basado en uso/tamaño)
        # Nota: Aquí reutilizamos la lógica de distancia, no la función de impresión para mantenerlo limpio
        
        target_vector = doc['documentSimilarity']['accessMetrics'] + [doc['documentSimilarity']['documentSize']]
        distances = []
        
        for candidate in all_docs:
            if candidate['id'] == doc['id']: continue
            cand_vector = candidate['documentSimilarity']['accessMetrics'] + [candidate['documentSimilarity']['documentSize']]
            dist = calculate_euclidean_distance(target_vector, cand_vector)
            distances.append((dist, candidate))
            
        distances.sort(key=lambda x: x[0])
        neighbors = distances[:k]
        
        # Votación (Voting) para determinar el grupo
        dept_votes = {}
        for _, neighbor in neighbors:
            dept = neighbor['documentSimilarity']['department']
            dept_votes[dept] = dept_votes.get(dept, 0) + 1
            
        # Obtener el departamento más común entre los vecinos
        predicted_group = max(dept_votes, key=dept_votes.get)
        actual_dept = doc['documentSimilarity']['department']
        
        print(f"Doc {doc['name']} ({actual_dept}) -> Asignado al Grupo sugerido: {predicted_group}")

# ==========================================
# BLOQUE PRINCIPAL DE EJECUCIÓN
# ==========================================

def main():
    # Fijamos semilla para reproducibilidad en la demo
    random.seed(42)

    # 1. Cargar o generar datos (1000 docs por requisito; puedes bajar doc_count para menos salida)
    doc_count = 1000
    my_docs = load_or_generate_documents(doc_count)
    
    # Seleccionamos el primer documento como nuestro "Query" o "Target"
    target_document = my_docs[0]
    
    line = "=" * 60
    print("\n" + line)
    print("Algoritmo 1: Similitud Básica (KNN)")
    print(line)
    algorithm_1_basic_similarity(target_document, my_docs, k=3)
    
    print("\n" + line)
    print("Algoritmo 2: Emparejamiento por Categoría")
    print(line)
    algorithm_2_category_matching(target_document, my_docs, k=3)
    
    print("\n" + line)
    print("Algoritmo 3: Patrón de Usuario")
    print(line)
    algorithm_3_user_pattern(target_document, my_docs, k=3)
    
    print("\n" + line)
    print("Algoritmo 4: Prueba de Efectividad")
    print(line)
    algorithm_4_effectiveness_test(target_document, my_docs, k=5)
    
    print("\n" + line)
    print("Algoritmo 5: Agrupación Organizacional")
    print(line)
    algorithm_5_organization_grouping(my_docs, k=4)

if __name__ == "__main__":
    main()
