import hashlib #se importa la librería hashlib para poder calcular el hash de los registros

def calcular_hash(texto):
    return hashlib.sha256(texto.encode('utf-8')).hexdigest()   #define la función calcular_hash que toma un texto como entrada y devuelve su hash SHA-256 en formato hexadecimal.

class ArbolMerkle: #se construye la clase ArbolMerkle que representa un árbol de Merkle. Esta clase tiene métodos para construir el árbol, generar pruebas de inclusión y verificar dichas pruebas.
    def __init__(self, registros): #constructor de la clase que inicializa el árbol con una lista de registros
        self.registros = registros # se almacena la lista de registros
        self.niveles = [] # se inicializa una lista vacía para almacenar los niveles del árbol
        nivel = [calcular_hash(r) for r in registros] # se calcula el hash de cada registro y se almacena en la lista nivel
        self.niveles.append(nivel) # se agrega el nivel inicial a la lista de niveles
        while len(nivel) > 1: # mientras haya más de un hash en el nivel actual, se calcula el siguiente nivel del árbol
            if len(nivel) % 2 != 0: # si el número de hashes en el nivel actual es impar, se duplica el último hash para que haya un número par de hashes
                nivel = nivel + [nivel[-1]] # se duplica el último hash del nivel actual
            nivel = [calcular_hash(nivel[i] + nivel[i+1]) for i in range(0, len(nivel), 2)] # se calcula el hash de cada par de hashes adyacentes en el nivel actual y se almacena en la lista nivel
            self.niveles.append(nivel) # se agrega el nuevo nivel a la lista de niveles

    @property # se define una propiedad llamada raiz que devuelve el hash de la raíz del árbol, que es el primer elemento del último nivel de la lista de niveles
    def raiz(self): # define el método raiz que devuelve el hash de la raíz del árbol
        return self.niveles[-1][0] # devuelve el primer elemento del último nivel de la lista de niveles, que es el hash de la raíz del árbol

    def generar_prueba(self, indice): # define el método generar_prueba que toma un índice como entrada y devuelve una lista de tuplas que representan la prueba de inclusión para el registro en ese índice
        prueba = [] # se inicializa una lista vacía para almacenar la prueba de inclusión
        for nivel in self.niveles[:-1]: # se itera sobre todos los niveles del árbol excepto el último
            lvl = nivel + [nivel[-1]] if len(nivel) % 2 != 0 else nivel # si el número de hashes en el nivel actual es impar, se duplica el último hash para que haya un número par de hashes
            if indice % 2 == 0: # si el índice es par, se agrega el hash del hermano derecho a la prueba de inclusión
                prueba.append((lvl[indice + 1], "DERECHA")) # si el índice es impar, se agrega el hash del hermano izquierdo a la prueba de inclusión
            else:
                prueba.append((lvl[indice - 1], "IZQUIERDA")) # se divide el índice entre 2 para pasar al siguiente nivel del árbol
            indice //= 2  # se devuelve la lista de tuplas que representan la prueba de inclusión
        return prueba 

    @staticmethod  # define un método estático llamado verificar_prueba que toma un dato, una prueba de inclusión y la raíz esperada del árbol como entrada y devuelve un valor booleano que indica si la prueba es válida o no
    def verificar_prueba(dato, prueba, raiz_esperada): #  define el método verificar_prueba que toma un dato, una prueba de inclusión y la raíz esperada del árbol como entrada y devuelve un valor booleano que indica si la prueba es válida o no
        h = calcular_hash(dato) #   calcula el hash del dato y lo almacena en la variable h
        for hermano, posicion in prueba: # itera sobre cada tupla en la prueba de inclusión, que contiene el hash del hermano y la posición (izquierda o derecha) del hermano con respecto al nodo actual
            h = calcular_hash(hermano + h if posicion == "IZQUIERDA" else h + hermano) # calcula el hash del nodo actual y su hermano, dependiendo de la posición del hermano, y lo almacena en la variable h
        return h == raiz_esperada   # devuelve un valor booleano que indica si el hash calculado a partir del dato y la prueba de inclusión coincide con la raíz esperada del árbol


if __name__ == "__main__":       # bloque principal del programa que se ejecuta cuando se ejecuta el script directamente
    registros = [           # lista de registros que se utilizarán para construir el árbol de Merkle
        "ORD-001: Laptop Dell XPS  | Qty:3  | $3.600 | Bodega-A",
        "ORD-002: Monitor Samsung  | Qty:5  | $2.500 | Bodega-B",
        "ORD-003: Teclado Logitech | Qty:10 |   $800 | Bodega-A",
        "ORD-004: Mouse Razer      | Qty:8  |   $400 | Bodega-C",
        "ORD-005: Webcam Logitech  | Qty:6  |   $720 | Bodega-B",
    ]

    arbol = ArbolMerkle(registros) # se crea una instancia de la clase ArbolMerkle con la lista de registros y se almacena en la variable arbol
    raiz_original = arbol.raiz # se obtiene la raíz del árbol de Merkle y se almacena en la variable raiz_original

    # 1. Construcción del árbol
    print(">>> 1. MERKLE ROOT ORIGINAL") # se imprime un mensaje indicando que se está mostrando la raíz original del árbol de Merkle
    print(f"Raíz: {raiz_original}\n")   # se imprime la raíz original del árbol de Merkle

    # 2. Modificar un registro → la raíz cambia
    modificados = registros.copy() # se crea una copia de la lista de registros y se almacena en la variable modificados
    modificados[2] = "ORD-003: Teclado Logitech | Qty:99 | $9.999 | Bodega-A" # se modifica el registro en el índice 2 de la lista modificados
    raiz_modificada = ArbolMerkle(modificados).raiz # se crea una nueva instancia de la clase ArbolMerkle con la lista modificada y se obtiene la raíz del árbol modificado, que se almacena en la variable raiz_modificada

    print(">>> 2. MODIFICACIÓN (Efecto Avalancha)") #   se imprime un mensaje indicando que se está mostrando la raíz modificada del árbol de Merkle después de modificar un registro
    print(f"Raíz original : {raiz_original}") # se imprime la raíz original del árbol de Merkle
    print(f"Raíz modificada: {raiz_modificada}") # se imprime la raíz modificada del árbol de Merkle
    print(f"¿Son iguales?: {raiz_original == raiz_modificada}\n") # se imprime un mensaje indicando si la raíz original y la raíz modificada son iguales o no

    # 3. Prueba de inclusión válida para ORD-003 (índice 2)
    prueba = arbol.generar_prueba(2) # se genera una prueba de inclusión para el registro en el índice 2 de la lista de registros y se almacena en la variable prueba
    valido = ArbolMerkle.verificar_prueba(registros[2], prueba, raiz_original) # se verifica la prueba de inclusión para el registro en el índice 2 de la lista de registros utilizando la prueba generada y la raíz original del árbol, y se almacena el resultado en la variable valido

    print(">>> 3. PRUEBA DE INCLUSIÓN VÁLIDA (índice 2)")   # se imprime un mensaje indicando que se está mostrando la prueba de inclusión válida para el registro en el índice 2 de la lista de registros
    print(f"Verificando: '{registros[2]}'") #   se imprime el registro que se está verificando
    print(f"Resultado: {valido} →  Funciona\n") # se imprime el resultado de la verificación de la prueba de inclusión, que debe ser True si la prueba es válida

    # 4. Dato incorrecto → debe fallar
    falso = ArbolMerkle.verificar_prueba("ORD-003: Teclado Logitech | Qty:99 | $9.999 | Bodega-A", prueba, raiz_original) # se verifica la prueba de inclusión para un dato incorrecto utilizando la prueba generada y la raíz original del árbol, y se almacena el resultado en la variable falso

    print(">>> 4. DATO INCORRECTO (debe fallar)") # se imprime un mensaje indicando que se está mostrando la verificación de un dato incorrecto, que debe fallar
    print(f"Resultado: {falso} →  Fallo esperado") #   se imprime el resultado de la verificación de la prueba de inclusión para el dato incorrecto, que debe ser False si la prueba falla como se espera