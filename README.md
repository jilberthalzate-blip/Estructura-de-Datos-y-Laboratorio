# Estructura de Datos y Laboratorio

Repositorio de laboratorios de la asignatura Estructura de Datos.

## Laboratorio 1 — Visor de matriz gigante (100,000 × 100,000)

Visualizador interactivo de una matriz de 100,000 × 100,000 celdas (10,000 millones de valores) que **nunca carga los datos completos en RAM**.

### Idea central

Una matriz de ese tamaño no cabe en memoria (~10-80 GB según el tipo de dato). La solución aplica el mismo principio que la **paginación de memoria virtual** de un sistema operativo, pero a nivel de aplicación:

- Los datos se guardan en disco divididos en **bloques (chunks) de 500×500**, usando la librería [`zarr`](https://zarr.dev/), en vez de en un único archivo plano.
- Cada vez que el usuario navega o hace zoom, solo se leen y descomprimen los 1-4 bloques que intersectan la vista actual — nunca la matriz completa.
- El proceso de Python usa unos pocos cientos de MB de RAM sin importar que la matriz "lógica" pese varios GB en disco.

### Origen de los datos

Los valores de la matriz (enteros 0-9) salen de una foto (`20241015_192425.jpg`), convertida a escala de grises por luminancia y cuantizada en 10 bandas de brillo. La foto se repite en mosaico hasta cubrir las 100,000×100,000 celdas.

### Controles

- **Sliders** (`← →`, `↑ ↓`): desplazan la ventana visible por la matriz (pan).
- **Rueda del mouse**: hace zoom in/out, centrado en el punto donde estabas viendo.

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
