"""
Unidad 1: Gestor de documentos con tabla hash, índice invertido y
recomendaciones aleatorizadas.
"""

import random
import string
import datetime
import time
from collections import defaultdict


# ---------------------------------------------------------
# CLASE 1: Documento
# ---------------------------------------------------------
class Document:
    """Representa un documento individual con sus metadatos."""

    def __init__(self, doc_id, title, content, tags):
        self.doc_id = doc_id
        self.title = title
        self.content = content
        self.tags = tags
        self.last_accessed = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S +0000")
        self.access_count = 0
        self.relevance_score = 0

    def __repr__(self):
        return f"[ID: {self.doc_id}] {self.title} (Score: {self.relevance_score})"


# ---------------------------------------------------------
# CLASE 2: Tabla Hash (Chain Hashing)
# ---------------------------------------------------------
class HashTable:
    """Tabla hash con chaining para almacenar documentos."""

    def __init__(self, size=2003):
        self.size = size
        self.buckets = [[] for _ in range(self.size)]

    def _hash_function(self, key):
        return hash(key) % self.size

    def insert(self, key, document):
        index = self._hash_function(key)
        bucket = self.buckets[index]
        for i, (k, doc) in enumerate(bucket):
            if k == key:
                bucket[i] = (key, document)
                return
        bucket.append((key, document))

    def get(self, key):
        index = self._hash_function(key)
        bucket = self.buckets[index]
        for k, doc in bucket:
            if k == key:
                return doc
        return None

    def get_all_documents(self):
        docs = []
        for bucket in self.buckets:
            for _, doc in bucket:
                docs.append(doc)
        return docs


# ---------------------------------------------------------
# CLASE 3: Índice Invertido
# ---------------------------------------------------------
class InvertedIndex:
    """Mapea palabra -> lista de documentos que la contienen."""

    def __init__(self):
        self.index = defaultdict(list)
        self.doc_store = {}

    def _tokenize(self, text):
        words = text.lower().split()
        cleaned = []
        for w in words:
            clean = w.strip('.,!?;:"()[]{}')
            if clean:
                cleaned.append(clean)
        return cleaned

    def add_document(self, document: Document):
        doc_id = document.doc_id
        self.doc_store[doc_id] = document

        for word in self._tokenize(document.title):
            if doc_id not in self.index[word]:
                self.index[word].append(doc_id)

        for word in self._tokenize(document.content):
            if doc_id not in self.index[word]:
                self.index[word].append(doc_id)

        for tag in document.tags:
            for word in self._tokenize(tag):
                if doc_id not in self.index[word]:
                    self.index[word].append(doc_id)

    def search(self, keyword):
        keyword = keyword.lower()
        return self.index.get(keyword, [])

    def get_document(self, doc_id):
        return self.doc_store.get(doc_id)

    def get_all_documents(self):
        return list(self.doc_store.values())


# ---------------------------------------------------------
# CLASE 4: Sistema de Gestión
# ---------------------------------------------------------
class DocumentSystem:
    """Gestiona generación, almacenamiento, búsqueda y recomendaciones."""

    def __init__(self):
        self.storage = HashTable(size=2003)
        self.inverted_index = InvertedIndex()
        self.user_search_history = []
        self.user_interactions = {}

    def generate_dummy_data(self, num_records=2000):
        """Genera documentos de prueba según el template básico."""
        print(f"Generando {num_records} documentos de prueba...")
        lorem_words = [
            'python', 'automatizado', 'java', 'lenguaje', 'programación', 'sistema', 'redes', 'seguridad', 
            'datos', 'análisis', 'desarrollo', 'aplicación', 'web', 'móvil', 'base', 'algoritmo', 'inteligencia', 
            'artificial', 'aprendizaje', 'máquina', 'nube', 'computación', 'software', 'hardware', 'infraestructura', 
            'tecnología', 'digital', 'información', 'procesamiento', 'visualización', 'automatización', 'robótica', 
            'sistema operativo', 'servidor', 'cliente', 'protocolo', 'criptografía', 'blockchain', 'iot', 
            'internet de las cosas', 'big data', 'análisis predictivo', 'minería de datos', 'redes neuronales', 
            'deep learning', 'framework', 'biblioteca', 'API', 'interfaz', 'usuario', 'experiencia', 'diseño', 
            'despliegue', 'contenerización', 'docker', 'kubernetes', 'virtualización', 'monitorización', 'rendimiento', 
            'optimización', 'seguridad informática', 'ciberseguridad', 'ataque', 'defensa', 'firewall', 'antivirus', 
            'malware', 'phishing', 'ingeniería social', 'criptomonedas', 'fintech', 'smart contracts', 'tokenización', 
            'economía digital', 'transformación digital', 'innovación', 'emprendimiento', 'startup', 'agilidad', 
            'scrum', 'kanban', 'devops', 'QA', 'control de calidad', 'documentación', 'versionado', 'git', 
            'github', 'gitlab', 'bitbucket', 'gestión de proyectos', 'planificación', 'análisis de requisitos', 
            'diseño de software', 'arquitectura de software', 'patrones de diseño'
        ]
        
        for _ in range(num_records):
            doc_id = "".join(random.choices(string.ascii_lowercase + string.digits, k=24))
            title = " ".join(random.choices(lorem_words, k=5)).capitalize()
            content = " ".join(random.choices(lorem_words, k=20)).capitalize()
            tags = random.sample(lorem_words, k=3)
            doc = Document(doc_id, title, content, tags)
            self.storage.insert(doc_id, doc)
            self.inverted_index.add_document(doc)
        print("Datos generados, tabla hash e índice invertido listos.")

    def _calculate_relevance_score(self, doc: Document, keyword: str):
        """Score por coincidencias en título/tags/contenido y popularidad."""
        keyword = keyword.lower()
        score = 0

        for word in doc.title.lower().split():
            if keyword in word:
                score += 3
        for tag in doc.tags:
            if keyword in tag.lower():
                score += 2
        for word in doc.content.lower().split():
            if keyword in word:
                score += 1
        score += doc.access_count * 0.5
        return score

    def _quicksort_by_relevance(self, docs_list):
        if len(docs_list) <= 1:
            return docs_list
        pivot = random.choice(docs_list)
        greater, equal, lesser = [], [], []
        for doc in docs_list:
            if doc.relevance_score > pivot.relevance_score:
                greater.append(doc)
            elif doc.relevance_score == pivot.relevance_score:
                equal.append(doc)
            else:
                lesser.append(doc)
        return self._quicksort_by_relevance(greater) + equal + self._quicksort_by_relevance(lesser)

    def search_by_keyword(self, keyword, use_inverted_index=True):
        """Búsqueda con índice invertido (rápido) o lineal (lento)."""
        keyword = keyword.lower()
        results = []

        if use_inverted_index:
            doc_ids = self.inverted_index.search(keyword)
            for doc_id in doc_ids:
                doc = self.inverted_index.get_document(doc_id)
                if doc:
                    score = self._calculate_relevance_score(doc, keyword)
                    if score > 0:
                        doc.relevance_score = score
                        results.append(doc)
        else:
            for doc in self.storage.get_all_documents():
                score = self._calculate_relevance_score(doc, keyword)
                if score > 0:
                    doc.relevance_score = score
                    results.append(doc)

        self.user_search_history.append(keyword)
        return self._quicksort_by_relevance(results)

    def retrieve_document(self, doc_id):
        """Recupera por ID (O(1)) y actualiza acceso y fecha."""
        doc = self.storage.get(doc_id)
        if doc:
            doc.access_count += 1
            doc.last_accessed = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S +0000")
            self.user_interactions[doc_id] = self.user_interactions.get(doc_id, 0) + 1
        return doc

    def randomized_recommendation(self, num_suggestions=3):
        """Recomendaciones ponderadas por búsquedas recientes y popularidad."""
        all_docs = self.inverted_index.get_all_documents()
        if not all_docs:
            return []

        candidates = []
        if self.user_search_history:
            recent = self.user_search_history[-3:]
            for doc in all_docs:
                relevance = sum(self._calculate_relevance_score(doc, term) for term in recent)
                if relevance > 0:
                    doc.relevance_score = relevance
                    candidates.append(doc)

        if len(candidates) < num_suggestions:
            popular = sorted(all_docs, key=lambda x: x.access_count, reverse=True)
            top_popular = popular[:max(10, len(popular) // 5)]
            existing = {d.doc_id for d in candidates}
            for doc in top_popular:
                if doc.doc_id not in existing:
                    candidates.append(doc)

        if len(candidates) < num_suggestions:
            candidates = all_docs

        k = min(num_suggestions, len(candidates))
        return random.sample(candidates, k)

    def get_user_stats(self):
        return {
            "total_searches": len(self.user_search_history),
            "unique_keywords": len(set(self.user_search_history)),
            "documents_accessed": len(self.user_interactions),
            "most_accessed_docs": sorted(self.user_interactions.items(), key=lambda x: x[1], reverse=True)[:5],
        }

    def compare_search_methods(self, keyword):
        """Compara índice invertido vs búsqueda lineal en tiempo y resultados."""
        print("\n" + "=" * 60)
        print(f"COMPARACIÓN DE MÉTODOS DE BÚSQUEDA: '{keyword}'")
        print("=" * 60)

        start = time.time()
        results_inverted = self.search_by_keyword(keyword, use_inverted_index=True)
        t_inv = time.time() - start

        start = time.time()
        results_linear = self.search_by_keyword(keyword, use_inverted_index=False)
        t_lin = time.time() - start

        print("\n1) ÍNDICE INVERTIDO")
        print(f"   Tiempo: {t_inv*1000:.2f} ms | Resultados: {len(results_inverted)}")
        print("\n2) BÚSQUEDA LINEAL")
        print(f"   Tiempo: {t_lin*1000:.2f} ms | Resultados: {len(results_linear)}")
        if t_inv > 0:
            speedup = t_lin / t_inv if t_inv > 0 else float('inf')
            print(f"\nMejora: {speedup:.1f}x más rápido con índice invertido")
        return results_inverted


if __name__ == "__main__":
    system = DocumentSystem()
    system.generate_dummy_data(2000)

    all_docs = system.storage.get_all_documents()
    sample_id = all_docs[0].doc_id

    print("\n" + "=" * 60)
    print(f"PRUEBA 1: Recuperación por Hash (ID: {sample_id[:12]}...)")
    print("=" * 60)
    retrieved = system.retrieve_document(sample_id)
    print(f"Documento: {retrieved.title}")
    print(f"Accesos: {retrieved.access_count}")

    print("\n" + "=" * 60)
    print("PRUEBA 2: Comparación de búsqueda con keyword 'data'")
    print("=" * 60)
    results = system.compare_search_methods("data")
    print("\nTop 5 más relevantes:")
    for i, doc in enumerate(results[:5], 1):
        print(f"  {i}. [{doc.relevance_score:.1f} pts] {doc.title}")

    print("\n" + "=" * 60)
    print("Simulando interacciones...")
    print("=" * 60)
    system.search_by_keyword("algorithm")
    system.search_by_keyword("python")
    if results:
        system.retrieve_document(results[0].doc_id)
        system.retrieve_document(results[0].doc_id)

    print("\n" + "=" * 60)
    print("PRUEBA 3: Recomendaciones")
    print("=" * 60)
    suggestions = system.randomized_recommendation(5)
    print(f"Historial: {system.user_search_history}")
    for i, doc in enumerate(suggestions, 1):
        print(f"  {i}. {doc.title} | Accesos: {doc.access_count} | Tags: {', '.join(doc.tags)}")

    print("\n" + "=" * 60)
    print("PRUEBA 4: Estadísticas de uso")
    print("=" * 60)
    stats = system.get_user_stats()
    print(f"Total de búsquedas: {stats['total_searches']}")
    print(f"Palabras clave únicas: {stats['unique_keywords']}")
    print(f"Documentos accedidos: {stats['documents_accessed']}")
    if stats["most_accessed_docs"]:
        print("Más accedidos:")
        for doc_id, count in stats["most_accessed_docs"]:
            doc = system.storage.get(doc_id)
            if doc:
                print(f"  - {doc.title[:40]}... ({count} accesos)")

    print("\n" + "=" * 60)
    print("Sistema funcionando correctamente")
    print("=" * 60)
