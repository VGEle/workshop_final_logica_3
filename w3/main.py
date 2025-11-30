"""
Unidad 3: Modelado de flujo de documentos con cadenas de Markov, PageRank,
random walks y demo de 2-SAT aleatorizado.
"""

import json
import random
import math
import datetime
import uuid

LINE = "=" * 60
SUBLINE = "-" * 60

# --- PARTE EXTRA: 2-SAT ALEATORIZADO (DEMO SENCILLA) ---


def evaluate_clause(clause, assignment):
    """Evalúa una cláusula (lit1 or lit2) bajo una asignación booleana."""
    lit1, lit2 = clause
    val1 = assignment[abs(lit1) - 1] if lit1 > 0 else not assignment[abs(lit1) - 1]
    val2 = assignment[abs(lit2) - 1] if lit2 > 0 else not assignment[abs(lit2) - 1]
    return val1 or val2


def is_satisfied(clauses, assignment):
    """Retorna True si todas las cláusulas están satisfechas."""
    return all(evaluate_clause(c, assignment) for c in clauses)


def random_2sat(clauses, max_iter=None):
    """
    Algoritmo aleatorizado tipo Papadimitriou para 2-SAT.
    Parte de una asignación aleatoria y voltea variables al azar en cláusulas no satisfechas.
    """
    n_vars = max(abs(lit) for clause in clauses for lit in clause)
    if max_iter is None:
        max_iter = 2 * n_vars * n_vars

    assignment = [random.choice([True, False]) for _ in range(n_vars)]

    for _ in range(max_iter):
        if is_satisfied(clauses, assignment):
            return assignment
        unsat = [c for c in clauses if not evaluate_clause(c, assignment)]
        clause = random.choice(unsat)
        var_idx = abs(random.choice(clause)) - 1
        assignment[var_idx] = not assignment[var_idx]

    return None


# --- PARTE 1: MATEMÁTICAS MARKOVIANAS ---

class MarkovMath:
    """
    Clase auxiliar para operaciones matriciales y de Cadenas de Markov.
    """

    @staticmethod
    def normalize_matrix(matrix):
        """Asegura que cada fila sume 1.0 (Matriz Estocástica)."""
        normalized = []
        for row in matrix:
            total = sum(row)
            if total == 0:
                length = len(row)
                normalized.append([1.0/length] * length)
            else:
                normalized.append([x / total for x in row])
        return normalized

    @staticmethod
    def multiply_vector_matrix(vector, matrix):
        """Multiplicación vector-matriz para iteraciones."""
        result = [0.0] * len(matrix[0])
        for i in range(len(matrix)): 
            for j in range(len(vector)):
                result[i] += vector[j] * matrix[j][i]
        return result

    @staticmethod
    def calculate_stationary_distribution(matrix, iterations=100):
        """
        Calcula la distribución estacionaria (carga de trabajo a largo plazo).
        Resuelve pi = pi * M.
        """
        n = len(matrix)
        pi = [1.0/n] * n
        for _ in range(iterations):
            pi = MarkovMath.multiply_vector_matrix(pi, matrix)
        return pi

    @staticmethod
    def calculate_pagerank(matrix, damping_factor=0.85, iterations=50):
        """Calcula PageRank con Taxation para manejar trampas y jerarquía."""
        n = len(matrix)
        v = [1.0/n] * n
        teleport = (1.0 - damping_factor) / n
        for _ in range(iterations):
            new_v = MarkovMath.multiply_vector_matrix(v, matrix)
            new_v = [x * damping_factor + teleport for x in new_v]
            v = new_v
        return v

    @staticmethod
    def simulate_random_walk_path(matrix, start_node, steps=3):
        """
        Genera una ruta real de navegación (searchPath) basada en probabilidades.
        Retorna la lista de nodos visitados y sus pesos.
        """
        path = []
        current = start_node
        n_states = len(matrix)
        
        for _ in range(steps):
            # Elegir siguiente nodo basado en las probabilidades de la fila actual
            next_node = random.choices(range(n_states), weights=matrix[current], k=1)[0]
            
            # Guardar el paso
            path.append({
                "nodeId": next_node + 1, # Ajuste para que sea base 1 (1-100)
                "transitionProbability": round(matrix[current][next_node], 3),
                "pathWeight": round(random.uniform(0.1, 2.0), 2) # Peso simulado de la arista
            })
            current = next_node
            
        return path

    @staticmethod
    def calculate_hitting_time(matrix, start_index, target_index, simulations=50):
        """Simula pasos promedio para llegar de A a B."""
        total_steps = 0
        n_states = len(matrix)
        for _ in range(simulations):
            current = start_index
            steps = 0
            while current != target_index and steps < 100:
                current = random.choices(range(n_states), weights=matrix[current], k=1)[0]
                steps += 1
            total_steps += steps
        return total_steps / simulations

    @staticmethod
    def calculate_mixing_time(matrix, tolerance=1e-6, max_iter=100):
        """Calcula iteraciones necesarias para estabilizar la matriz."""
        n = len(matrix)
        pi = [1.0/n] * n
        for k in range(max_iter):
            new_pi = MarkovMath.multiply_vector_matrix(pi, matrix)
            dist = math.sqrt(sum((new_pi[i] - pi[i])**2 for i in range(n)))
            pi = new_pi
            if dist < tolerance:
                return k + 1
        return max_iter

# --- PARTE 2: GENERADOR DE DATOS CON LÓGICA DE NEGOCIO ---

class DocumentSystemGenerator:
    
    def __init__(self):
        # Índices: 0:received, 1:classified, 2:processed, 3:archived, 4:retrieved
        self.states = ["received", "classified", "processed", "archived", "retrieved"]
        self.categories = ["contract", "report", "memo", "presentation", "email", "invoice"]
        self.priorities = ["low", "normal", "high", "urgent"]
        self.lorem_words = ["lorem", "ipsum", "dolor", "sit", "amet", "process", "data", "system"]

    def _generate_lorem(self, count, type_="words"):
        if type_ == "words": return " ".join(random.choices(self.lorem_words, k=count))
        elif type_ == "sentences": return " ".join(random.choices(self.lorem_words, k=8)).capitalize() + "."
        elif type_ == "paragraphs": return " ".join(random.choices(self.lorem_words, k=30)) + "."
        return ""

    def _build_priority_matrix(self, priority):
        """
        Construye una matriz de transición inteligente basada en la prioridad.
        Cumple con 'Model document processing with priority-based transitions'.
        """
        # Matriz base (5x5) inicializada en ceros
        matrix = [[0.0] * 5 for _ in range(5)]
        
        # Definir probabilidad de avance según prioridad
        # Urgent avanza rápido (0.9), Low avanza lento (0.3)
        forward_prob = {
            "low": 0.3, 
            "normal": 0.5, 
            "high": 0.7, 
            "urgent": 0.9
        }[priority]
        
        stay_prob = 1.0 - forward_prob

        # Reglas de Transición (Lógica de Negocio):
        # 0(Received) -> 1(Classified)
        matrix[0][0] = stay_prob; matrix[0][1] = forward_prob
        
        # 1(Classified) -> 2(Processed)
        matrix[1][1] = stay_prob; matrix[1][2] = forward_prob
        
        # 2(Processed) -> 3(Archived) o 4(Retrieved)
        # Dividimos la probabilidad de avance entre archivar y recuperar
        matrix[2][2] = stay_prob
        matrix[2][3] = forward_prob * 0.8 # Mayoría se archiva
        matrix[2][4] = forward_prob * 0.2 # Algunos se recuperan
        
        # 3(Archived) -> ESTADO ABSORBENTE (Dead End lógico)
        # Una vez archivado, se queda archivado (1.0). 
        # Cumple 'Implement proper state classification (absorbing)'.
        matrix[3][3] = 1.0 
        
        # 4(Retrieved) -> Puede volver a procesarse o archivarse
        matrix[4][4] = 0.5; matrix[4][2] = 0.5

        return MarkovMath.normalize_matrix(matrix)

    def _generate_category_matrix(self):
        """Genera matriz 6x6 aleatoria normalizada para las categorías."""
        matrix = []
        for _ in range(6):
            row = [random.random() for _ in range(6)]
            matrix.append(row)
        return MarkovMath.normalize_matrix(matrix)

    def generate_document(self):
        # Seleccionar prioridad y tipo primero para definir la matriz
        priority = random.choice(self.priorities)
        doc_type = random.choice(self.categories)
        
        # 1. Construir matriz INTELIGENTE basada en prioridad
        state_matrix = self._build_priority_matrix(priority)
        category_matrix = self._generate_category_matrix()
        
        # 2. Análisis de Markov (Estacionaria, PageRank, Mixing Time)
        stationary_dist = MarkovMath.calculate_stationary_distribution(state_matrix)
        pagerank = MarkovMath.calculate_pagerank(state_matrix)
        mixing_time = MarkovMath.calculate_mixing_time(state_matrix)
        
        # Estado actual y métricas derivadas
        current_state_idx = random.randint(0, 4)
        
        # Corrección lógica: Si es estado absorbente (3), probabilidad de quedarse es 1
        current_state_prob = state_matrix[current_state_idx][current_state_idx]
        
        # 3. Detección de Cuellos de Botella (Lógica Avanzada)
        throughput_rate = round(random.uniform(10.0, 100.0), 1)
        processing_load = stationary_dist[current_state_idx]
        
        # Si la carga teórica (stationary) supera la capacidad (throughput/100 para escala), hay cuello de botella
        is_bottleneck = processing_load > (throughput_rate / 500.0) 

        # 4. Análisis de Recuperación (Random Walk)
        # Generar ruta de búsqueda REAL usando la matriz de categorías (simulando red de documentos)
        # Usamos category_matrix para simular saltos entre documentos relacionados
        search_path = MarkovMath.simulate_random_walk_path(category_matrix, start_node=0, steps=random.randint(3, 7))
        
        hitting_time = MarkovMath.calculate_hitting_time(state_matrix, current_state_idx, 4) # Hacia 'retrieved'
        
        # Eficiencia inversa al tiempo de hitting
        retrieval_efficiency = round(1.0 / (1.0 + hitting_time/10), 2)

        # Formato de fecha corregido (YYYY-MM-ddThh:mm:ss Z)
        date_str = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S Z")

        # Construcción del Objeto
        doc = {
            "_id": str(uuid.uuid4()),
            "title": self._generate_lorem(1, "sentences"),
            "content": self._generate_lorem(1, "paragraphs"),
            "documentState": self.states[current_state_idx],
            "previousDocumentState": random.choice(self.states),
            "stateTransitionProb": round(current_state_prob, 3),
            "timeInCurrentState": random.randint(5, 1440),
            "expectedProcessingTime": random.randint(10, 480),
            "tags": [self._generate_lorem(1, "words") for _ in range(3)],
            
            "processingWorkflow": {
                "workflowStage": random.randint(1, 7),
                "priority": priority,
                "complexityScore": round(random.uniform(0.1, 5.0), 1),
                "processingLoad": round(processing_load, 3),
                "bottleneckRisk": round(processing_load, 3) # Relacionado a la carga estacionaria
            },
            
            "classificationAnalysis": {
                "documentCategory": doc_type,
                "classificationConfidence": round(random.random(), 2),
                "reclassificationProb": round(random.uniform(0.0, 0.3), 3),
                "categoryTransitionMatrix": category_matrix
            },
            
            "retrievalOptimization": {
                "accessFrequency": random.randint(0, 100),
                "searchPath": search_path, # Ruta generada por Random Walk
                "retrievalEfficiency": retrieval_efficiency,
                "cacheHitProbability": round(random.random(), 3)
            },
            
            "lifecycleAnalysis": {
                "documentAge": random.randint(1, 2160),
                "expectedLifetime": random.randint(168, 8760),
                "retentionProbability": round(random.random(), 3),
                "archivalTransitionProb": round(state_matrix[current_state_idx][3], 3),
                "obsolescenceRisk": round(random.random(), 3)
            },
            
            "systemEfficiency": {
                "throughputRate": throughput_rate,
                "queueLength": random.randint(0, 200),
                "processingBottleneck": is_bottleneck, # Calculado con lógica
                "loadBalancingScore": round(random.random(), 2),
                "systemUtilization": round(random.random(), 2)
            },
            
            "networkProperties": {
                "documentNetwork": {
                    "nodeId": random.randint(1, 100),
                    "networkDegree": random.randint(2, 15),
                    "clusteringCoefficient": round(random.random(), 3),
                    "centralityScore": round(pagerank[current_state_idx], 3)
                },
                "randomWalkProperties": {
                    "coverTime": MarkovMath.calculate_hitting_time(state_matrix, 0, 4, 10), # Estimado simple
                    "mixingTime": mixing_time,
                    "hittingTime": int(hitting_time)
                }
            },
            
            "documentType": doc_type,
            "searchFrequency": random.randint(1, 100),
            "stationaryProbability": round(stationary_dist[current_state_idx], 3),
            "workflowOptimization": round(random.uniform(0.7, 1.3), 2),
            "lastAccessed": date_str
        }
        return doc

    def generate_dataset(self, count):
        return [self.generate_document() for _ in range(count)]

# --- PARTE 3: EJECUCIÓN (PARAMETRIZADA) ---

if __name__ == "__main__":
    generator = DocumentSystemGenerator()
    
    # Parametrizado a 2000 como pide el template (cambiar a 5 para pruebas rápidas)
    NUM_DOCS = 2000 
    
    print("\n" + LINE)
    print(f"Generando {NUM_DOCS} documentos...")
    data = generator.generate_dataset(NUM_DOCS)
    
    # Guardar en archivo para manejar el volumen grande
    filename = "document_data_v2.json"
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)
        
    print(f"¡Éxito! Archivo guardado como '{filename}'.")
    
    # Imprimir solo el primero como muestra en la terminal
    print("\n" + LINE)
    print("Muestra del Primer Documento")
    print(LINE)
    print(json.dumps(data[0], indent=2))

    # Demostración extra: 2-SAT aleatorizado con cláusulas de ejemplo
    print("\n" + LINE)
    print("Demo 2-SAT (aleatorizado)")
    print(LINE)
    sample_clauses = [[1, 2], [-1, 3], [-2, -3]]
    solution = random_2sat(sample_clauses, max_iter=None)
    print(f"Cláusulas: {sample_clauses}")
    if solution:
        print(f"Asignación encontrada: {solution}")
    else:
        print("No se encontró asignación en las iteraciones permitidas.")
