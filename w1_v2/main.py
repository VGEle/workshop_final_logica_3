import json
import random
import string
import datetime

# ---------------------------------------------------------
# CLASE 1: Estructura del Documento
# Representa el objeto de datos basico.
# ---------------------------------------------------------
class Document:
    """
    Representa un documento individual con sus metadatos.
    """
    def __init__(self, doc_id, title, content, tags):
        self.doc_id = doc_id
        self.title = title
        self.content = content
        self.tags = tags
        self.last_accessed = datetime.datetime.now().isoformat()
        self.access_count = 0  # Para rastrear interacciones del usuario

    def __repr__(self):
        return f"[ID: {self.doc_id}] {self.title}"

# ---------------------------------------------------------
# CLASE 2: Tabla Hash (Hash Table)
# Implementacion conceptual basada en la teoria de la Unidad 1.
# Usa 'Buckets' (listas) para manejar colisiones (Chaining).
# Referencia: Hashing in Practice, diapositiva sobre Chain Hashing.
# ---------------------------------------------------------
class HashTable:
    """
    Estructura de datos que asocia llaves (Keys) con valores (Documentos)
    usando una funcion hash para calcular el indice.
    """
    def __init__(self, size=1000):
        # El tamaño (size) define el numero de 'buckets' o cubetas disponibles.
        self.size = size
        # Inicializamos los buckets como listas vacias para manejar colisiones (chaining).
        self.buckets = [[] for _ in range(self.size)]

    def _hash_function(self, key):
        """
        Calcula el indice basado en la llave.
        Teoria: h(x) maps keys into B = {0, ..., n-1}.
        """
        # Usamos la funcion hash() nativa de Python y el operador modulo (%).
        # Esto asegura que el indice siempre este entre 0 y self.size - 1.
        return hash(key) % self.size

    def insert(self, key, document):
        """
        Inserta un documento en la tabla hash.
        Costo esperado: O(1).
        """
        index = self._hash_function(key)
        bucket = self.buckets[index]
        
        # Verificamos si ya existe para actualizarlo, si no, lo agregamos.
        for i, (k, doc) in enumerate(bucket):
            if k == key:
                bucket[i] = (key, document) # Actualizar
                return
        
        # Si no existe, se agrega al final de la lista del bucket (colision manejada).
        bucket.append((key, document))

    def get(self, key):
        """
        Recupera un documento usando su llave.
        Costo esperado: O(1).
        """
        index = self._hash_function(key)
        bucket = self.buckets[index]
        
        for k, doc in bucket:
            if k == key:
                return doc
        return None # No encontrado

    def get_all_documents(self):
        """
        Metodo auxiliar para recolectar todos los documentos de todos los buckets.
        Util para las funciones de busqueda lineal y sugerencias.
        """
        all_docs = []
        for bucket in self.buckets:
            for k, doc in bucket:
                all_docs.append(doc)
        return all_docs

# ---------------------------------------------------------
# CLASE 3: Sistema de Gestion de Documentos
# Integra la Tabla Hash y los Algoritmos Aleatorizados.
# ---------------------------------------------------------
class DocumentSystem:
    """
    Clase principal que gestiona la generacion de datos, almacenamiento,
    recuperacion y ordenamiento.
    """
    def __init__(self):
        # Usamos un numero primo o cercano para el tamaño para reducir colisiones (Teoria).
        self.storage = HashTable(size=2003) 
        self.user_search_history = [] # Historial simple

    def generate_dummy_data(self, num_records=2000):
        """
        Genera datos aleatorios siguiendo el template JSON solicitado.
        Simula la variedad y volumen de Big Data.
        """
        print(f"Generando {num_records} documentos de prueba...")
        
        lorem_words = ["lorem", "ipsum", "dolor", "sit", "amet", "data", "big", "hash", "code", "random", "search", "engine", "sorting", "retrieval", "system"]
        
        for i in range(num_records):
            # Generacion de ID aleatorio
            doc_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=24))
            
            # Generacion de titulo y contenido aleatorio
            title = ' '.join(random.choices(lorem_words, k=5)).capitalize()
            content = ' '.join(random.choices(lorem_words, k=20)).capitalize()
            tags = random.sample(lorem_words, k=3)
            
            # Creacion del objeto documento
            new_doc = Document(doc_id, title, content, tags)
            
            # Almacenamiento en la Tabla Hash usando el ID como llave
            self.storage.insert(doc_id, new_doc)
            
        print("Datos generados y almacenados en la Tabla Hash.")

    def _quicksort(self, docs_list):
        """
        Implementacion simple de Randomized Quicksort para ordenar resultados.
        Referencia: Logica y Representacion III - Clase 03.
        Ordena alfabeticamente por titulo.
        """
        if len(docs_list) <= 1:
            return docs_list
        
        # Seleccion aleatoria del pivote (Randomized approach)
        pivot = random.choice(docs_list)
        
        left = []
        middle = []
        right = []
        
        for doc in docs_list:
            # Comparamos por titulo
            if doc.title < pivot.title:
                left.append(doc)
            elif doc.title == pivot.title:
                middle.append(doc)
            else:
                right.append(doc)
                
        # Llamada recursiva (Divide and Conquer)
        return self._quicksort(left) + middle + self._quicksort(right)

    def search_by_keyword(self, keyword):
        """
        Busca documentos que contengan una palabra clave en el titulo.
        Retorna los resultados ORDENADOS usando Quicksort.
        """
        keyword = keyword.lower()
        results = []
        all_docs = self.storage.get_all_documents()
        
        for doc in all_docs:
            if keyword in doc.title.lower() or keyword in doc.tags:
                results.append(doc)
        
        # Guardamos la interaccion
        self.user_search_history.append(keyword)
        
        # Aqui aplicamos el Sorting requerido en el titulo del proyecto
        return self._quicksort(results)

    def retrieve_document(self, doc_id):
        """
        Recupera un documento especifico por su ID.
        Usa la eficiencia O(1) de la Tabla Hash.
        """
        doc = self.storage.get(doc_id)
        if doc:
            doc.access_count += 1 # Rastrear interaccion
            doc.last_accessed = datetime.datetime.now().isoformat()
        return doc

    def randomized_recommendation(self, num_suggestions=3):
        """
        Algoritmo Aleatorizado (Randomized Algorithm).
        Sugerencias basadas en muestreo aleatorio (Sampling).
        """
        all_docs = self.storage.get_all_documents()
        
        if not all_docs:
            return []
            
        # Si el usuario tiene historial, intentamos filtrar un subconjunto relevante
        relevant_pool = []
        if self.user_search_history:
            last_search = self.user_search_history[-1]
            relevant_pool = [d for d in all_docs if last_search in d.tags]
        
        # Si no hay pool relevante, usamos todo el conjunto
        if len(relevant_pool) < num_suggestions:
            pool_to_sample = all_docs
        else:
            pool_to_sample = relevant_pool

        # Seleccion aleatoria (Sampling)
        suggestions = random.sample(pool_to_sample, min(num_suggestions, len(pool_to_sample)))
        
        return suggestions

# ---------------------------------------------------------
# BLOQUE PRINCIPAL (Ejecucion)
# ---------------------------------------------------------
if __name__ == "__main__":
    # 1. Instanciar el sistema
    system = DocumentSystem()

    # 2. Generar la data
    system.generate_dummy_data(2000)

    # 3. Simular recuperacion por ID (Hashing)
    all_docs = system.storage.get_all_documents()
    sample_id = all_docs[0].doc_id
    
    print(f"\n--- Prueba 1: Recuperacion eficiente por Hash (ID: {sample_id}) ---")
    retrieved_doc = system.retrieve_document(sample_id)
    print(f"Documento recuperado: {retrieved_doc}")

    # 4. Simular busqueda por palabra clave con ORDENAMIENTO (Quicksort)
    print("\n--- Prueba 2: Busqueda ordenada por palabra clave 'data' ---")
    search_results = system.search_by_keyword("data")
    print(f"Encontrados {len(search_results)} documentos.")
    print("Primeros 3 resultados ordenados alfabeticamente:")
    for doc in search_results[:3]:
        print(f" - {doc.title}")

    # 5. Recomendaciones Aleatorizadas
    print("\n--- Prueba 3: Recomendaciones personalizadas (Aleatorias) ---")
    suggestions = system.randomized_recommendation(3)
    for i, doc in enumerate(suggestions, 1):
        print(f"Sugerencia {i}: {doc.title}")