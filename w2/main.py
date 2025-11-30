"""
Unidad 2: Procesamiento de streams con Bloom Filter, Sampling, Conteo exacto,
Momento 1 (F1) y DGIM sobre eventos de documentos.
"""

import random
import math

LINE = "=" * 70
SUB = "-" * 70

class SistemaProcesamiento:
    def __init__(self):
        # ---------------------------------------------------------
        # 1. BLOOM FILTER (Filtro de Bloom)
        # Teoría: Array de N bits inicializados en 0.
        # ---------------------------------------------------------
        self.bloom_size = 20  # Tamaño pequeño para ver efectos en la demo
        self.bloom_array = [0] * self.bloom_size
        # Recencia por firma simple de contenido
        self.bloom_last_seen = {}
        self.recency_window = 5  # pasos recientes que consideramos
        
        # ---------------------------------------------------------
        # 2. BEHAVIOR SAMPLING (Muestreo) - Algoritmo 3
        # Teoría: Hash consistente y umbral dinámico.
        # ---------------------------------------------------------
        self.sample_buckets = 10     # 'b' en la teoría
        self.sample_size_limit = 3   # 'm' (tamaño máximo de muestra)
        self.threshold = self.sample_buckets - 1 # Empieza permisivo
        self.sample = {}             # Aquí guardamos los usuarios elegidos
        
        # Constantes para la función hash (a * user + c)
        self.hash_a = 3
        self.hash_c = 7

        # ---------------------------------------------------------
        # 3. DISTINCT COUNTING (Conteo Exacto)
        # Teoría: Estructura exacta (mapa/set) por usuario.
        # ---------------------------------------------------------
        self.user_distinct_docs = {}
        self.user_doc_count = {}  # Conteo exacto de documentos por usuario

        # ---------------------------------------------------------
        # 4. FREQUENCY MOMENTS (Momento 1)
        # Teoría: F1 = Suma total de las frecuencias (longitud del stream).
        # ---------------------------------------------------------
        self.F1_total = 0

        # ---------------------------------------------------------
        # 5. DGIM ALGORITHM
        # Teoría: Ventana deslizante, buckets potencias de 2.
        # ---------------------------------------------------------
        self.current_timestamp = 0
        self.window_size = 32
        # Lista de buckets. Cada bucket es: [tamaño, tiempo_final]
        self.dgim_buckets = []
        # Ruta preferida para usuarios muestreados
        self.routing_choice = {}

    # ==============================================================================
    # 1. LÓGICA BLOOM FILTER
    # ==============================================================================
    def procesar_bloom(self, document_type, step, search_freq=None):
        """
        Verifica si un documento similar fue visto recientemente.
        Usa una firma simple (tipo + bucket de frecuencia) y recencia.
        """
        freq_bucket = search_freq // 10 if search_freq is not None else None
        signature = f"{document_type.lower()}_{freq_bucket}" if freq_bucket is not None else document_type.lower()

        # Hash 1: Suma de ASCII ponderada
        val_ascii = sum(ord(c) for c in signature)
        pos1 = (val_ascii * 7) % self.bloom_size

        # Hash 2: Posiciones con desplazamiento
        pos2 = (val_ascii * 13 + 5) % self.bloom_size

        # Hash 3: hash nativo de Python
        pos3 = (hash(signature) * 11 + 17) % self.bloom_size

        positions = (pos1, pos2, pos3)

        # Verificamos recencia: todos los bits en 1 y visto en ventana reciente
        seen = all(self.bloom_array[p] == 1 for p in positions)
        recent = signature in self.bloom_last_seen and (step - self.bloom_last_seen[signature]) <= self.recency_window

        if seen and recent:
            print(f"[Bloom] El tipo '{document_type}' posiblemente fue visto en los últimos {self.recency_window} pasos.")
        else:
            print(f"[Bloom] El tipo '{document_type}' no estaba reciente. Marcando bits {pos1} y {pos2}.")
        
        # Marcamos los bits a 1 (Inserción) y guardamos recencia
        for pos in positions:
            self.bloom_array[pos] = 1
        self.bloom_last_seen[signature] = step

    # ==============================================================================
    # 2. LÓGICA SAMPLING (Basado ESTRICTAMENTE en tu Algoritmo 3)
    # ==============================================================================
    def procesar_muestreo(self, user_id, data):
        """
        Decide si guardamos a este usuario basándonos en su Hash y el Umbral.
        Define una ruta preferente simple para la recuperación.
        """
        # Fórmula teórica: h(user) = (a * user + c) mod buckets
        h_user = (self.hash_a * user_id + self.hash_c) % self.sample_buckets
        
        print(f"[Sampling] Usuario {user_id} (Hash: {h_user}) | Umbral actual: {self.threshold}")

        # Condición del algoritmo: if h(user) <= threshold (ajustado a <= para incluir el borde)
        if h_user <= self.threshold:
            # Agregar a la muestra
            if user_id not in self.sample:
                self.sample[user_id] = []
            self.sample[user_id].append(data)
            self.routing_choice[user_id] = "ruta_prioritaria"
            print("   -> Usuario aceptado en la muestra. Ruta: prioritaria.")
        else:
            self.routing_choice[user_id] = "ruta_normal"
            print(f"   -> Usuario descartado.")

        # Manejo de desbordamiento (Overflow)
        # Teoría: while (users in sample > sample_size)
        while len(self.sample) > self.sample_size_limit:
            print(f"   [!] Muestra llena. Reduciendo umbral de {self.threshold} a {self.threshold - 1}")
            
            # 1. Eliminar elementos con h(user) == threshold
            usuarios_a_eliminar = []
            for uid in self.sample:
                h_uid = (self.hash_a * uid + self.hash_c) % self.sample_buckets
                if h_uid == self.threshold:
                    usuarios_a_eliminar.append(uid)
            
            for uid in usuarios_a_eliminar:
                del self.sample[uid]
                print(f"   [!] Usuario {uid} eliminado por cambio de umbral.")

            # 2. Reducir el umbral
            self.threshold -= 1

    # ==============================================================================
    # 3. LÓGICA DISTINCT COUNTING (Exacto)
    # ==============================================================================
    def procesar_conteo_exacto(self, user_id, doc_type):
        """
        Cuenta exactamente cuántos documentos ha visto un usuario y cuántos tipos distintos.
        """
        if user_id not in self.user_distinct_docs:
            self.user_distinct_docs[user_id] = set() # 'set' guarda solo elementos únicos

        self.user_distinct_docs[user_id].add(doc_type)

        # Conteo exacto de documentos (no solo tipos)
        self.user_doc_count[user_id] = self.user_doc_count.get(user_id, 0) + 1

    # ==============================================================================
    # 4. FREQUENCY MOMENTS (F1)
    # ==============================================================================
    def procesar_momento_uno(self, search_freq):
        """
        F1 es simplemente la suma de las frecuencias de los elementos.
        """
        self.F1_total += search_freq
        print(f"[Momentos] F1 (Suma Total Frecuencias): {self.F1_total}")

    # ==============================================================================
    # 5. LÓGICA DGIM (Simplificado)
    # ==============================================================================
    def procesar_dgim(self, bit):
        """
        Recibe un bit (1 o 0). Si es 1, crea un bucket y fusiona si es necesario.
        """
        self.current_timestamp += 1
        
        # Paso A: Eliminar buckets viejos (fuera de la ventana)
        # Si el tiempo actual es 100 y ventana es 20, borramos todo lo anterior a 80
        while len(self.dgim_buckets) > 0:
            ultimo_bucket = self.dgim_buckets[-1]  # El más viejo está al final
            if ultimo_bucket[1] <= self.current_timestamp - self.window_size:
                self.dgim_buckets.pop()  # Borrar
            else:
                break

        # Paso B: Si el bit es 0, no hacemos nada (según DGIM básico para contar 1s)
        if bit == 0:
            return

        # Paso C: Si bit es 1, crear nuevo bucket de tamaño 1
        # Insertamos al inicio (índice 0 es lo más reciente)
        new_bucket = [1, self.current_timestamp] 
        self.dgim_buckets.insert(0, new_bucket)

        # Paso D: Fusión (Merge) - La parte clave de la teoría
        # "Si hay 3 buckets del mismo tamaño, fusionar los 2 más viejos"
        idx = 0
        while idx < len(self.dgim_buckets) - 2:
            # Revisamos 3 buckets consecutivos: actual, siguiente, subsiguiente
            b1 = self.dgim_buckets[idx]
            b2 = self.dgim_buckets[idx+1]
            b3 = self.dgim_buckets[idx+2]

            if b1[0] == b2[0] and b2[0] == b3[0]:
                # ¡Tenemos tres del mismo tamaño!
                # Fusionamos b2 y b3 (los más viejos de ese tamaño)
                # Nuevo tamaño = b2.size + b3.size (ej. 1+1=2, 2+2=4)
                # Nos quedamos con el timestamp del más reciente de los dos fusionados (b2)
                merged_bucket = [b2[0] + b3[0], b2[1]]
                
                # Eliminamos b2 y b3, insertamos el fusionado
                self.dgim_buckets.pop(idx+1)
                self.dgim_buckets.pop(idx+1)
                self.dgim_buckets.insert(idx+1, merged_bucket)
                
                # Seguimos revisando desde la misma posición por si generó cascada
            else:
                idx += 1
        
        print(f"[DGIM] Estado Buckets (Tamaño, TiempoFinal): {self.dgim_buckets}")

# ==============================================================================
# SIMULACIÓN DEL FLUJO (STREAM)
# ==============================================================================

# 1. Crear el sistema
sistema = SistemaProcesamiento()

# 2. Generar datos aleatorios (Como pide el ejercicio)
tipos_docs = ["report", "memo", "presentation", "email"]

print("--- INICIANDO STREAM DE DATOS ---\n")

for i in range(10): # Simularemos 10 llegadas de datos
    print("\n" + SUB)
    print(f"T (Tiempo): {i+1}")
    print(SUB)
    
    # Generar JSON simulado
    doc_type = random.choice(tipos_docs)
    freq = random.randint(1, 100)
    
    # Como el JSON no trae usuario, simulamos uno al azar (ID entre 1 y 15)
    # Esto es necesario para el Sampling y el Distinct Counting
    user_id = random.randint(1, 15)
    
    dato_json = {
        "documentType": doc_type,
        "searchFrequency": freq,
        "simulatedUserID": user_id
    }
    
    print(f"Llegó dato: {dato_json}")

    # --- EJECUTAR LOS 5 ALGORITMOS ---
    
    # 1. Bloom Filter
    sistema.procesar_bloom(doc_type, step=i+1, search_freq=freq)
    
    # 2. Behavior Sampling
    sistema.procesar_muestreo(user_id, dato_json)
    
    # 3. Distinct Counting (Exacto)
    sistema.procesar_conteo_exacto(user_id, doc_type)
    
    # 4. Moment 1
    sistema.procesar_momento_uno(freq)
    
    # 5. DGIM
    # Para DGIM contamos cada búsqueda en la ventana (bit=1 en cada llegada).
    print(f"[DGIM] Entrada al stream de bits: 1")
    sistema.procesar_dgim(1)

print("\n--- FIN DE LA SIMULACIÓN ---")
print(LINE)
print("RESUMEN FINAL")
print(LINE)
print(f"Muestra (usuarios): {list(sistema.sample.keys())}")
print(f"Conteo exacto de documentos por usuario: {sistema.user_doc_count}")
print(f"Rutas asignadas por muestreo: {sistema.routing_choice}")
