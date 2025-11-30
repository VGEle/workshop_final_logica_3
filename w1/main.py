"""
Implementación sencilla de un gestor de documentos que usa una tabla hash para
almacenar, generar, buscar y sugerir resultados de forma rápida.
"""

import json
import random
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, Iterable, List, Optional


class DocumentRecommender:
    """
    Gestiona documentos en una tabla hash, permite generarlos y ofrece búsquedas
    y sugerencias personalizadas basadas en interacciones previas.
    """

    def __init__(self, documents: Optional[Iterable[Dict]] = None) -> None:
        """
        Inicializa la estructura con una lista opcional de documentos.
        Cada documento debe incluir _id, title, content, tags y lastAccessed.
        """
        self.documents: Dict[str, Dict] = {}
        self.inverted_index: Dict[str, set] = defaultdict(set)
        self.user_history: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))

        if documents:
            for doc in documents:
                self.add_document(doc)

    def add_document(self, document: Dict) -> None:
        """
        Agrega un documento a la tabla hash y lo indexa para búsquedas rápidas.
        """
        doc_id = document["_id"]
        self.documents[doc_id] = document
        self._index_document(document)

    def get_document(self, doc_id: str) -> Optional[Dict]:
        """
        Recupera un documento en tiempo constante; regresa None si no existe.
        """
        return self.documents.get(doc_id)

    def record_interaction(self, user_id: str, doc_id: str) -> None:
        """
        Registra una interacción de un usuario con un documento para
        personalizar futuras búsquedas y sugerencias.
        """
        if doc_id not in self.documents:
            return

        self.user_history[user_id][doc_id] += 1
        self.documents[doc_id]["lastAccessed"] = datetime.utcnow().isoformat()

    def search(self, keywords: List[str], user_id: Optional[str] = None, limit: int = 10) -> List[Dict]:
        """
        Busca documentos que contengan las palabras clave y los ordena por
        relevancia simple y afinidad con el usuario.
        """
        tokens = [kw.lower() for kw in keywords]
        candidate_ids = set()

        for token in tokens:
            candidate_ids.update(self.inverted_index.get(token, set()))

        scored_results = []
        user_scores = self.user_history.get(user_id, {}) if user_id else {}

        for doc_id in candidate_ids:
            doc = self.documents[doc_id]
            text = " ".join(
                [doc.get("title", ""), doc.get("content", ""), " ".join(doc.get("tags", []))]
            ).lower()

            text_score = sum(text.count(tok) for tok in tokens)
            personalization_bonus = user_scores.get(doc_id, 0)
            scored_results.append((text_score + personalization_bonus, doc))

        scored_results.sort(key=lambda item: item[0], reverse=True)
        return [doc for _, doc in scored_results[:limit]]

    def suggest(self, user_id: str, query: Optional[List[str]] = None, sample_size: int = 5) -> List[Dict]:
        """
        Sugiere documentos usando aleatoriedad controlada, ponderando la
        relevancia de la consulta y el historial del usuario.
        """
        if query:
            candidates = self.search(query, user_id=user_id, limit=len(self.documents))
        else:
            candidates = list(self.documents.values())

        if not candidates:
            return []

        user_scores = self.user_history.get(user_id, {})
        weights = []

        for doc in candidates:
            base_weight = 1.0 + 0.5 * user_scores.get(doc["_id"], 0)
            weights.append(base_weight)

        suggestions = []
        chosen_ids = set()

        # Evita sugerir documentos repetidos en la misma llamada.
        while len(suggestions) < min(sample_size, len(candidates)):
            doc = random.choices(candidates, weights=weights, k=1)[0]
            if doc["_id"] in chosen_ids:
                continue
            suggestions.append(doc)
            chosen_ids.add(doc["_id"])

        return suggestions

    def _index_document(self, document: Dict) -> None:
        """
        Construye el índice invertido a partir del título, contenido y etiquetas.
        """
        tokens = self._tokenize(document.get("title", "")) | self._tokenize(document.get("content", ""))
        tokens.update(tag.lower() for tag in document.get("tags", []))

        for token in tokens:
            self.inverted_index[token].add(document["_id"])

    @staticmethod
    def _tokenize(text: str) -> set:
        """
        Normaliza y separa un texto en tokens básicos.
        """
        return {
            word.strip(".,;:!?()[]\"'").lower()
            for word in text.split()
            if word.strip(".,;:!?()[]\"'")
        }

    @staticmethod
    def generate_documents(total: int = 2000) -> List[Dict]:
        """
        Genera documentos de muestra
        """
        documents = []
        for _ in range(total):
            documents.append(
                {
                    "_id": DocumentRecommender._generate_object_id(),
                    "title": DocumentRecommender._generate_title(),
                    "content": DocumentRecommender._generate_content(),
                    "tags": DocumentRecommender._generate_tags(),
                    "lastAccessed": DocumentRecommender._generate_last_accessed(),
                }
            )
        return documents

    @staticmethod
    def save_documents(documents: List[Dict], path: str) -> None:
        """
        Guarda los documentos en un archivo JSON.
        """
        with open(path, "w", encoding="utf-8") as file:
            json.dump(documents, file, indent=2, ensure_ascii=False)

    @staticmethod
    def _generate_object_id() -> str:
        """
        Crea un identificador de 24 caracteres hexadecimales tipo ObjectId.
        """
        hex_chars = "0123456789abcdef"
        return "".join(random.choice(hex_chars) for _ in range(24))

    @staticmethod
    def _generate_title() -> str:
        """
        Crea un título aleatorio sin punto final.
        """
        words = DocumentRecommender._sample_words(random.randint(5, 10))
        sentence = " ".join(words)
        return sentence.capitalize()

    @staticmethod
    def _generate_content() -> str:
        """
        Crea un párrafo de contenido.
        """
        sentences = []
        for _ in range(random.randint(5, 10)):
            words = DocumentRecommender._sample_words(random.randint(8, 15))
            sentence = " ".join(words).capitalize() + "."
            sentences.append(sentence)
        return " ".join(sentences)

    @staticmethod
    def _generate_tags() -> List[str]:
        """
        Crea tres etiquetas para el documento.
        """
        return [random.choice(DocumentRecommender._WORD_BANK) for _ in range(3)]

    @staticmethod
    def _generate_last_accessed() -> str:
        """
        Genera una marca de tiempo con fecha aleatoria del último año.
        """
        now = datetime.now()
        random_days = random.randint(0, 365)
        random_date = now - timedelta(days=random_days)
        random_date = random_date.replace(
            hour=random.randint(0, 23),
            minute=random.randint(0, 59),
            second=random.randint(0, 59),
        )
        return random_date.strftime("%Y-%m-%dT%H:%M:%S +0000")

    @staticmethod
    def _sample_words(quantity: int) -> List[str]:
        """
        Devuelve una lista de palabras aleatorias del banco base.
        """
        return [random.choice(DocumentRecommender._WORD_BANK) for _ in range(quantity)]

    _WORD_BANK = [
        "system",
        "data",
        "analysis",
        "search",
        "engine",
        "hashing",
        "index",
        "retrieval",
        "storage",
        "cache",
        "ranking",
        "query",
        "document",
        "cluster",
        "vector",
        "token",
        "user",
        "session",
        "history",
        "learning",
        "metric",
        "relevance",
        "probability",
        "random",
        "cloud",
        "network",
        "log",
        "audit",
        "trace",
        "performance",
        "scalable",
        "distributed"
    ]


if __name__ == "__main__":
    # Generar y guardar documentos de muestra
    documents = DocumentRecommender.generate_documents(total=2000)
    DocumentRecommender.save_documents(documents, "data.json")
    print(f"Archivo creado: data.json")

    recommender = DocumentRecommender(documents)

    # Ejemplo básico de uso
    sample_user = "usuario_demo"
    query = ["system", "data"]

    resultados = recommender.search(query, user_id=sample_user, limit=3)
    print("Resultados de búsqueda:")
    for doc in resultados:
        print(f"- {doc['title']} (id: {doc['_id']})")

    if resultados:
        # Registrar interacción con el primer resultado para personalizar futuras sugerencias.
        recommender.record_interaction(sample_user, resultados[0]["_id"])

    sugerencias = recommender.suggest(sample_user, query=query, sample_size=3)
    print("\nSugerencias personalizadas:")
    for doc in sugerencias:
        print(f"- {doc['title']} (id: {doc['_id']})")
