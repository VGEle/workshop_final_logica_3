import json
import random
import math
import datetime
import uuid

# --- PARTE 1: CLASES DE UTILIDAD MATEMATICA (MARKOV, PAGERANK & 2-SAT) ---

class MarkovMath:
    """
    Clase auxiliar para realizar operaciones matriciales y analisis de cadenas de Markov.
    """

    @staticmethod
    def normalize_matrix(matrix):
        """
        Asegura que cada fila de la matriz de transicion sume exactamente 1.0.
        Teoria: Requisito fundamental para una Matriz Estocastica (Clase 13).
        """
        normalized = []
        for row in matrix:
            total = sum(row)
            if total == 0:
                # Si una fila es todo ceros (Dead End), se distribuye uniforme
                length = len(row)
                normalized.append([1.0/length] * length)
            else:
                normalized.append([x / total for x in row])
        return normalized

    @staticmethod
    def multiply_vector_matrix(vector, matrix):
        """Multiplica un vector fila por una matriz (Iteracion de Potencia)."""
        result = [0.0] * len(matrix[0])
        for i in range(len(matrix)): 
            for j in range(len(vector)):
                result[i] += vector[j] * matrix[j][i]
        return result

    @staticmethod
    def calculate_stationary_distribution_and_mixing_time(matrix, tolerance=1e-6, max_iterations=100):
        """
        Calcula la distribucion estacionaria (pi) y el Mixing Time.
        Teoria: Clase 14 (Estacionaria) y Clase 16 (Mixing Time).
        Mixing Time aqui se aproxima como el numero de iteraciones para converger.
        """
        n = len(matrix)
        pi = [1.0/n] * n
        mixing_time = max_iterations
        
        for k in range(max_iterations):
            new_pi = MarkovMath.multiply_vector_matrix(pi, matrix)
            
            # Chequear convergencia (distancia euclidiana entre iteraciones)
            dist = math.sqrt(sum((new_pi[i] - pi[i])**2 for i in range(n)))
            pi = new_pi
            
            if dist < tolerance:
                mixing_time = k + 1
                break
                
        return pi, mixing_time

    @staticmethod
    def calculate_pagerank(matrix, damping_factor=0.85, iterations=50):
        """
        Calcula el PageRank usando el metodo de Taxation (Teleportacion).
        Teoria: Clase 15. Formula: v = beta * M * v + (1-beta) * e/n
        """
        n = len(matrix)
        v = [1.0/n] * n
        teleport_prob = (1.0 - damping_factor) / n
        
        for _ in range(iterations):
            new_v = MarkovMath.multiply_vector_matrix(v, matrix)
            new_v = [x * damping_factor for x in new_v]
            new_v = [x + teleport_prob for x in new_v]
            v = new_v
            
        return v

    @staticmethod
    def simulate_random_walk(matrix, start_index, target_index, max_steps=100):
        """Simula una caminata aleatoria para encontrar tiempos de llegada."""
        current = start_index
        steps = 0
        n_states = len(matrix)
        
        while current != target_index and steps < max_steps:
            current = random.choices(range(n_states), weights=matrix[current], k=1)[0]
            steps += 1
        return steps

    @staticmethod
    def calculate_hitting_time(matrix, start_index, target_index, simulations=50):
        """Calcula el Hitting Time (h_ij) promedio. Teoria: Clase 16."""
        total_steps = 0
        for _ in range(simulations):
            total_steps += MarkovMath.simulate_random_walk(matrix, start_index, target_index)
        return total_steps / simulations

    @staticmethod
    def calculate_cover_time(matrix, start_index, simulations=20):
        """Calcula el Cover Time (tiempo para visitar todos los nodos). Teoria: Clase 16."""
        total_steps = 0
        n_states = len(matrix)
        for _ in range(simulations):
            visited = set()
            visited.add(start_index)
            current = start_index
            steps = 0
            while len(visited) < n_states and steps < 500: 
                current = random.choices(range(n_states), weights=matrix[current], k=1)[0]
                visited.add(current)
                steps += 1
            total_steps += steps
        return int(total_steps / simulations)


class TwoSATSolver:
    """
    Implementacion del algoritmo aleatorio para 2-SAT.
    Teoria: Clase 17. Requerido en 'Deliverables'.
    """
    @staticmethod
    def solve(clauses, num_vars, max_iterations=None):
        if max_iterations is None:
            max_iterations = 2 * (num_vars ** 2)
        assignment = [random.choice([True, False]) for _ in range(num_vars)]
        for i in range(max_iterations):
            unsatisfied_clauses = []
            for clause in clauses:
                lit1, lit2 = clause
                val1 = assignment[abs(lit1)-1] if lit1 > 0 else not assignment[abs(lit1)-1]
                val2 = assignment[abs(lit2)-1] if lit2 > 0 else not assignment[abs(lit2)-1]
                if not (val1 or val2): unsatisfied_clauses.append(clause)
            if not unsatisfied_clauses: return {"success": True, "assignment": assignment, "steps": i}
            target_clause = random.choice(unsatisfied_clauses)
            var_idx = abs(random.choice(target_clause)) - 1
            assignment[var_idx] = not assignment[var_idx]
        return {"success": False, "steps": max_iterations}

# --- PARTE 2: GENERADOR DE DATOS DEL SISTEMA ---

class DocumentSystemGenerator:
    """
    Clase principal que genera los documentos siguiendo el template JSON.
    """
    
    def __init__(self):
        self.states = ["received", "classified", "processed", "archived", "retrieved"]
        self.categories = ["contract", "report", "memo", "presentation", "email", "invoice"]
        self.priorities = ["low", "normal", "high", "urgent"]
        self.lorem_words = ["lorem", "ipsum", "dolor", "sit", "amet", "consectetur", "process", "data"]

    def _generate_lorem(self, count, type_="words"):
        if type_ == "words": return " ".join(random.choices(self.lorem_words, k=count))
        elif type_ == "sentences": return " ".join(random.choices(self.lorem_words, k=8)).capitalize() + "."
        elif type_ == "paragraphs": return " ".join(random.choices(self.lorem_words, k=30)) + "."
        return ""

    def _generate_transition_matrix(self, size):
        """Genera una matriz estocastica de tamano size x size."""
        matrix = []
        for _ in range(size):
            row = [random.random() for _ in range(size)]
            matrix.append(row)
        return MarkovMath.normalize_matrix(matrix)

    def generate_document(self):
        # 1. Matriz de ESTADOS (5x5 para el flujo del documento)
        state_matrix = self._generate_transition_matrix(len(self.states))
        
        # 2. Matriz de CATEGORIAS (6x6 para la clasificacion)
        category_matrix = self._generate_transition_matrix(len(self.categories))
        
        # 3. Analisis Estacionario y Mixing Time (Usando la matriz de estados)
        stationary_dist, mixing_time = MarkovMath.calculate_stationary_distribution_and_mixing_time(state_matrix)
        
        # 4. Calculo de PageRank
        pagerank_dist = MarkovMath.calculate_pagerank(state_matrix)
        
        current_state_idx = random.randint(0, len(self.states) - 1)
        current_state_name = self.states[current_state_idx]
        bottleneck_risk = stationary_dist[current_state_idx]
        
        # 5. Analisis de Random Walk
        target_idx = 4 # retrieved
        hitting_time = MarkovMath.calculate_hitting_time(state_matrix, current_state_idx, target_idx)
        cover_time = MarkovMath.calculate_cover_time(state_matrix, current_state_idx)
        
        # Eficiencia basada en Hitting Time
        retrieval_efficiency = 1.0 / (1.0 + (hitting_time / 10.0))
        retrieval_efficiency = round(min(retrieval_efficiency, 1.0), 2)

        # Construccion del JSON
        doc = {
            "_id": str(uuid.uuid4()),
            "title": self._generate_lorem(1, "sentences"),
            "content": self._generate_lorem(1, "paragraphs"),
            "documentState": current_state_name,
            "previousDocumentState": random.choice(self.states[:-1]),
            "stateTransitionProb": round(state_matrix[current_state_idx][current_state_idx], 3),
            "timeInCurrentState": random.randint(5, 1440),
            "expectedProcessingTime": random.randint(10, 480),
            "tags": [self._generate_lorem(1, "words") for _ in range(3)],
            "processingWorkflow": {
                "workflowStage": random.randint(1, 7),
                "priority": random.choice(self.priorities),
                "complexityScore": round(random.uniform(0.1, 5.0), 1),
                "processingLoad": round(stationary_dist[current_state_idx], 2),
                "bottleneckRisk": round(bottleneck_risk, 3)
            },
            "classificationAnalysis": {
                "documentCategory": random.choice(self.categories),
                "classificationConfidence": round(random.random(), 2),
                "reclassificationProb": round(random.uniform(0.0, 0.3), 3),
                "categoryTransitionMatrix": category_matrix # Ahora es 6x6
            },
            "retrievalOptimization": {
                "accessFrequency": random.randint(0, 100),
                "searchPath": [], 
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
                "throughputRate": round(random.uniform(1.0, 100.0), 1),
                "queueLength": random.randint(0, 200),
                "processingBottleneck": bottleneck_risk > 0.3,
                "loadBalancingScore": round(random.random(), 2),
                "systemUtilization": round(random.random(), 2)
            },
            "networkProperties": {
                "documentNetwork": {
                    "nodeId": random.randint(1, 100),
                    "networkDegree": random.randint(2, 15),
                    "clusteringCoefficient": round(random.random(), 3),
                    "centralityScore": round(pagerank_dist[current_state_idx], 3)
                },
                "randomWalkProperties": {
                    "coverTime": cover_time,
                    "mixingTime": mixing_time, # Ahora calculado
                    "hittingTime": int(hitting_time)
                }
            },
            "documentType": random.choice(self.categories),
            "searchFrequency": random.randint(1, 100),
            "stationaryProbability": round(stationary_dist[current_state_idx], 3),
            "workflowOptimization": round(random.uniform(0.7, 1.3), 2),
            "lastAccessed": datetime.datetime.now().isoformat()
        }
        
        for _ in range(3):
            next_node = random.randint(1, 50)
            doc["retrievalOptimization"]["searchPath"].append({
                "nodeId": next_node,
                "transitionProbability": round(random.random(), 3),
                "pathWeight": round(random.uniform(0.1, 2.0), 2)
            })
        return doc

    def generate_dataset(self, count=5):
        return [self.generate_document() for _ in range(count)]

# --- PARTE 3: EJECUCION ---

if __name__ == "__main__":
    generator = DocumentSystemGenerator()
    data = generator.generate_dataset(count=5)
    print(json.dumps(data, indent=2))
    
    print("\n--- TEST DE ALGORITMO 2-SAT (Deliverable extra) ---")
    example_clauses = [[1, 2], [-1, 3], [-2, -3]]
    result_2sat = TwoSATSolver.solve(example_clauses, num_vars=3)
    print(f"Clausulas: {example_clauses}")
    print(f"Resultado: {result_2sat}")