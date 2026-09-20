Árbol de Merkle en Python
Implementación desde cero de un Árbol de Merkle (Merkle Tree) en Python puro, aplicado a un caso de uso de integridad de órdenes de inventario.
¿Qué es un Árbol de Merkle?
Un Árbol de Merkle es una estructura de datos criptográfica en forma de árbol binario donde:
Cada hoja contiene el hash de un dato.
Cada nodo padre contiene el hash de la concatenación de sus dos hijos.
La raíz (Merkle Root) es un resumen criptográfico de todos los datos del árbol.
Cualquier modificación, por mínima que sea, en cualquier dato produce una raíz completamente diferente (efecto avalancha). Esto permite detectar manipulaciones de forma eficiente sin necesidad de comparar todos los datos.
Es la base de tecnologías como Bitcoin, Ethereum, Git y sistemas de bases de datos distribuidas.
Características
Construcción del árbol desde una lista arbitraria de registros.
Cálculo del Merkle Root con SHA-256.
Manejo automático de niveles con número impar de nodos (duplicación del último).
Generación de pruebas de inclusión (Merkle Proof).
Verificación de pruebas sin necesidad de conocer el resto del árbol.
Demostración del efecto avalancha ante modificaciones.
Estructura del proyecto
```
merkle-tree/
│
├── merkle.py       # Implementación principal
└── README.md       # Este archivo
```
Requisitos
Python 3.7 o superior
Sin dependencias externas (solo librería estándar `hashlib`)
Uso
```bash
python merkle.py
```
Salida esperada
```
>>> 1. MERKLE ROOT ORIGINAL
Raíz: e3b0c44298fc1c149afb...

>>> 2. MODIFICACIÓN (Efecto Avalancha)
Raíz original : e3b0c44298fc1c149afb...
Raíz modificada: a7f3d92bc1e04f87d3c9...
¿Son iguales?: False

>>> 3. PRUEBA DE INCLUSIÓN VÁLIDA (índice 2)
Verificando: 'ORD-003: Teclado Logitech | Qty:10 | $800 | Bodega-A'
Resultado: True →  ÉXITO

>>> 4. DATO INCORRECTO (debe fallar)
Resultado: False →  FALLO ESPERADO
```
Cómo funciona
1. Construcción del árbol
```
Registros (hojas):   [H0]  [H1]  [H2]  [H3]  [H4]
                       \   /      \   /      |
Nivel intermedio:    [H01]        [H23]    [H44]  ← H4 duplicado
                         \         /
Nivel intermedio:       [H0123]  [H4444]
                              \   /
Raíz (Merkle Root):         [H_RAIZ]
```
2. Prueba de inclusión
Para verificar que un dato pertenece al árbol no es necesario conocer todos los demás datos. Solo se necesita el camino de hashes "hermanos" desde la hoja hasta la raíz. Para un árbol de `n` hojas, la prueba tiene `log₂(n)` pasos.
3. Verificación
Se recalcula el camino hacia la raíz usando el dato y los hermanos de la prueba. Si el hash final coincide con la raíz conocida, el dato es auténtico.
API principal
```python
# Crear el árbol
arbol = ArbolMerkle(registros)

# Obtener la raíz
raiz = arbol.raiz

# Generar una prueba de inclusión para el elemento en el índice i
prueba = arbol.generar_prueba(i)

# Verificar si un dato pertenece al árbol
es_valido = ArbolMerkle.verificar_prueba(dato, prueba, raiz)
```
Caso de uso del ejemplo
El script demuestra la integridad de órdenes de inventario:
Orden	Producto	Cantidad	Precio	Bodega
ORD-001	Laptop Dell XPS	3	$3.600	Bodega-A
ORD-002	Monitor Samsung	5	$2.500	Bodega-B
ORD-003	Teclado Logitech	10	$800	Bodega-A
ORD-004	Mouse Razer	8	$400	Bodega-C
ORD-005	Webcam Logitech	6	$720	Bodega-B
Si alguien intenta modificar la cantidad o el precio de cualquier orden, la raíz cambia inmediatamente y la alteración queda detectada.
Conceptos clave
Término	Descripción
SHA-256	Función hash criptográfica que produce 256 bits (64 hex)
Merkle Root	Hash raíz que resume criptográficamente todos los datos
Efecto avalancha	Pequeño cambio en entrada → gran cambio en hash de salida
Merkle Proof	Conjunto mínimo de hashes para verificar un dato
Nodo hermano	Nodo con el que se combina para subir al padre
Aplicaciones reales
Bitcoin / Ethereum: verificar transacciones sin descargar toda la blockchain.
Git: detectar cambios en archivos del repositorio.
Sistemas de archivos distribuidos (IPFS, Cassandra): garantizar consistencia de datos.
Certificados de transparencia (Certificate Transparency): auditar CAs de forma pública.
