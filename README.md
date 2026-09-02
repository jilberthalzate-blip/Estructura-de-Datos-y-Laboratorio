# Estructura de Datos y Laboratorio

Repositorio de laboratorios de la asignatura Estructura de Datos.

## Laboratorio 1 — Visor de matriz gigante (100,000 × 100,000)

Visualizador interactivo de una matriz de 100,000 × 100,000 celdas (10,000 millones de valores) que **nunca carga los datos completos en RAM**.

### Idea central

Una matriz de ese tamaño no cabe en memoria (~10-80 GB según el tipo de dato). La solución aplica el mismo principio que la **paginación de memoria virtual** de un sistema operativo, pero a nivel de aplicación:

- Los datos se guardan en disco divididos en **bloques (chunks) de 500×500**, usando la librería [`zarr`](https://zarr.dev/), en vez de en un único archivo plano.
- Cada vez que el usuario navega o hace zoom, solo se leen y descomprimen los 1-4 bloques que intersectan la vista actual — nunca la matriz completa.
- El proceso de Python usa unos pocos cientos de MB de RAM sin importar que la matriz "lógica" pese varios GB en disco.

### Evolución del enfoque de datos

La primera versión de este laboratorio generaba la matriz con **valores aleatorios uniformes** (0-9), solo para probar que el sistema de bloques/paginación funcionara sin cargar todo en RAM. El problema fue que con ruido aleatorio no se podía comprobar visualmente que el paneo y el zoom estuvieran mostrando la región correcta de la matriz — cualquier zona se veía igual de aleatoria que otra.

Por eso se tomó la decisión de reemplazar los datos aleatorios por los de una **foto real**, para poder visualizar gráficamente y confirmar a simple vista que la navegación por bloques funciona correctamente sobre datos con estructura reconocible, no solo ruido.

### Origen de los datos

Los valores de la matriz (enteros 0-9) salen de una foto (`20241015_192425.jpg`), convertida a escala de grises por luminancia y cuantizada en 10 bandas de brillo. La foto se repite en mosaico hasta cubrir las 100,000×100,000 celdas.

### Rendimiento: RAM vs. disco duro

El objetivo del ejercicio era que la matriz completa **nunca se cargara por completo en RAM**. Resultados medidos:

**Disco duro (almacenamiento persistente):**

| Versión de los datos | Tamaño sin comprimir | Tamaño real en disco |
|---|---|---|
| Aleatoria uniforme (primera versión) | ~10 GB (`uint8`) | ~4.54 GB (Zstd apenas comprime ruido puro) |
| Foto real en mosaico (versión final) | ~10 GB (`uint8`) | ~1.08 GB (Zstd comprime bien porque hay zonas uniformes y gradientes) |

**RAM (memoria durante la ejecución):**

- El proceso mide un *working set* de solo **~114 MB**, sin importar que la matriz pese varios GB en disco.
- Ese uso de RAM es prácticamente constante: no crece con el tamaño de la matriz, porque en cada vista solo se leen y descomprimen los 1-4 bloques de `500×500` que intersectan la ventana visible — el resto se queda en disco.
- Comparación: cargar la matriz completa con `np.load()` habría requerido tener los ~10 GB completos en RAM de una sola vez, algo inviable en un equipo con 16 GB.

### Controles

- **Sliders** (`← →`, `↑ ↓`): desplazan la ventana visible por la matriz (pan).
- **Rueda del mouse**: hace zoom in/out, centrado en el punto donde estabas viendo.

### Formato de los archivos de datos

Dentro de `matriz_100k_foto_mosaico.zarr/` hay dos tipos de archivo:

- **`zarr.json`** — el único archivo de texto plano (JSON), con los metadatos: tamaño de la matriz, tipo de dato, tamaño de bloque.
- **Los archivos dentro de `c/.../...`** (ej. `c/199/199`) — **binarios comprimidos con Zstandard**, no texto. Cada uno guarda un bloque de 500×500 valores enteros (0-9).

Si abres uno de esos archivos de bloque en un editor de texto (Notepad, VS Code, etc.), vas a ver símbolos ilegibles (`Ð`, `Ë`, `œ`...) — eso es normal y esperado: cada símbolo raro es solo cómo el editor intenta mostrar como "letra" un byte comprimido que no corresponde a ningún carácter imprimible. No es un archivo corrupto ni un error.

No hace falta leer esos archivos manualmente — `zarr` los descomprime automáticamente cuando el script pide `matriz[fila, columna]`. Para comprobarlo, esto imprime los valores reales (números 0-9) de un bloque:

```python
import zarr
z = zarr.open(r"%LOCALAPPDATA%\matriz_100k_foto_mosaico.zarr", mode="r")
print(z[0:5, 0:10])
```

### Cómo correrlo

```bash
pip install numpy zarr matplotlib pillow
python matriz.py
```

La primera ejecución genera los datos en disco (`%LOCALAPPDATA%\matriz_100k_foto_mosaico.zarr`, ~1 GB) — puede tardar unos minutos. Las ejecuciones siguientes reutilizan esos datos y abren el visor de inmediato.

### Estructura de la carpeta

```
Laboratorio 1/
├── matriz.py                          # script principal
├── 20241015_192425.jpg                # foto fuente (no se sube al repo)
├── Matriz representacion en disco duro/   # capturas: tamaño y estructura en disco
└── Matriz representacion Grafica/         # captura: visualización final
```
