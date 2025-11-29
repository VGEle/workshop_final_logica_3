import random
import math

class SistemaProcesamiento:
    def __init__(self):
        # ---------------------------------------------------------
        # 1. BLOOM FILTER (Filtro de Bloom)
        # Teoría: Array de N bits inicializados en 0.
        # ---------------------------------------------------------
        self.bloom_size = 20  # Tamaño pequeño para ver efectos en la demo
        self.bloom_array = [0] * self.bloom_size
        
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

        # ---------------------------------------------------------
        # 4. FREQUENCY MOMENTS (Momento 1)
        # Teoría: F1 = Suma total de las frecuencias (longitud del stream).
        # ---------------------------------------------------------
        self.F1_total = 0

        # ---------------------------------------------------------
        # 5. DGIM ALGORITHM
        # Teoría: Ventana deslizante, cubetas potencias de 2.
        # ---------------------------------------------------------
        self.current_timestamp = 0
        self.window_size = 32
        # Lista de cubetas. Cada cubeta es: [tamaño, tiempo_final]
        self.dgim_buckets = [] 

    # ==============================================================================
    # 1. LÓGICA BLOOM FILTER
    # ==============================================================================
    def procesar_bloom(self, document_type):
        """
        Verifica si un tipo de documento ya fue visto. Si no, lo marca.
        Usamos dos funciones hash simples simuladas.
        """
        # Simulamos Hash 1: Suma de valores ASCII % tamaño
        val_ascii = sum(ord(c) for c in document_type)
        pos1 = (val_ascii * 7) % self.bloom_size
        
        # Simulamos Hash 2: Otra operación matemática
        pos2 = (val_ascii * 13 + 5) % self.bloom_size

        # Verificamos si ambos bits están en 1 (Teoría: "Posiblemente ya existe")
        existe = False
        if self.bloom_array[pos1] == 1 and self.bloom_array[pos2] == 1:
            existe = True
            print(f"[Bloom] El tipo '{document_type}' POSIBLEMENTE ya fue procesado.")
        else:
            print(f"[Bloom] El tipo '{document_type}' NO estaba. Marcando bits {pos1} y {pos2}.")
        
        # Marcamos los bits a 1 (Inserción)
        self.bloom_array[pos1] = 1
        self.bloom_array[pos2] = 1

    # ==============================================================================
    # 2. LÓGICA SAMPLING (Basado ESTRICTAMENTE en tu Algoritmo 3)
    # ==============================================================================
    def procesar_muestreo(self, user_id, data):
        """
        Decide si guardamos a este usuario basándonos en su Hash y el Umbral.
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
            print(f"   -> ¡Usuario aceptado en la muestra!")
        else:
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
        Cuenta exactamente cuántos tipos de documentos distintos ha visto un usuario.
        """
        if user_id not in self.user_distinct_docs:
            self.user_distinct_docs[user_id] = set() # 'set' guarda solo elementos únicos
        
        self.user_distinct_docs[user_id].add(doc_type)
        count = len(self.user_distinct_docs[user_id])
        # Solo imprimimos para ver qué pasa
        # print(f"[Conteo] Usuario {user_id} ha visto {count} tipos de documentos únicos.")

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
        Recibe un bit (1 o 0). Si es 1, crea una cubeta y fusiona si es necesario.
        """
        self.current_timestamp += 1
        
        # Paso A: Eliminar cubetas viejas (fuera de la ventana)
        # Si el tiempo actual es 100 y ventana es 20, borramos todo lo anterior a 80
        while len(self.dgim_buckets) > 0:
            ultimo_bucket = self.dgim_buckets[-1] # El más viejo está al final
            if ultimo_bucket[1] <= self.current_timestamp - self.window_size:
                self.dgim_buckets.pop() # Borrar
            else:
                break

        # Paso B: Si el bit es 0, no hacemos nada (según DGIM básico para contar 1s)
        if bit == 0:
            return

        # Paso C: Si bit es 1, crear nueva cubeta de tamaño 1
        # Insertamos al inicio (índice 0 es lo más reciente)
        new_bucket = [1, self.current_timestamp] 
        self.dgim_buckets.insert(0, new_bucket)

        # Paso D: Fusión (Merge) - La parte clave de la teoría
        # "Si hay 3 cubetas del mismo tamaño, fusionar las 2 más viejas"
        idx = 0
        while idx < len(self.dgim_buckets) - 2:
            # Revisamos 3 cubetas consecutivas: actual, siguiente, subsiguiente
            b1 = self.dgim_buckets[idx]
            b2 = self.dgim_buckets[idx+1]
            b3 = self.dgim_buckets[idx+2]

            if b1[0] == b2[0] and b2[0] == b3[0]:
                # ¡Tenemos tres del mismo tamaño!
                # Fusionamos b2 y b3 (las más viejas de ese tamaño)
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
        
        print(f"[DGIM] Estado Cubetas (Tamaño, TiempoFinal): {self.dgim_buckets}")

# ==============================================================================
# SIMULACIÓN DEL FLUJO (STREAM)
# ==============================================================================

# 1. Crear el sistema
sistema = SistemaProcesamiento()

# 2. Generar datos aleatorios (Como pide el ejercicio)
tipos_docs = ["report", "memo", "presentation", "email"]

print("--- INICIANDO STREAM DE DATOS ---\n")

for i in range(10): # Simularemos 10 llegadas de datos
    print(f"\n--- T (Tiempo): {i+1} ---")
    
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
    sistema.procesar_bloom(doc_type)
    
    # 2. Behavior Sampling
    sistema.procesar_muestreo(user_id, dato_json)
    
    # 3. Distinct Counting (Exacto)
    sistema.procesar_conteo_exacto(user_id, doc_type)
    
    # 4. Moment 1
    sistema.procesar_momento_uno(freq)
    
    # 5. DGIM
    # Para DGIM necesitamos un BIT (1 o 0).
    # Regla simple: Si la frecuencia es alta (>50), es un "Evento Importante" (1), sino (0).
    bit_dgim = 1 if freq > 50 else 0
    print(f"[DGIM] Entrada al stream de bits: {bit_dgim}")
    sistema.procesar_dgim(bit_dgim)

print("\n--- FIN DE LA SIMULACIÓN ---")
print("Contenidos Finales de Muestras (Sampling):")
print(sistema.sample.keys()) # Ver qué usuarios sobrevivieron en la muestra