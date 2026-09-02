import os
import zarr
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider

# --- Matriz respaldada en disco, en bloques 2D (no cabe completa en RAM) ---
# Zarr guarda la matriz en "tiles" cuadrados en vez de fila por fila: cada
# vista solo necesita leer 1-4 bloques contiguos, no cientos de fragmentos
# dispersos por fila (que es lo que pasaba con np.memmap en un disco normal).
#
# OJO: se guarda FUERA de OneDrive a propósito. Si quedara dentro de la
# carpeta sincronizada, escribir decenas de miles de archivos de chunk
# dispara la sincronización de OneDrive en cada escritura (mucho más lento).
DIR_SCRIPT = os.path.dirname(os.path.abspath(__file__))
RUTA_FOTO = os.path.join(DIR_SCRIPT, "imagen .jpg")
RUTA_MATRIZ = os.path.join(os.environ.get("LOCALAPPDATA", "C:\\Temp"), "matriz_100k_foto_mosaico.zarr")
FORMA = (100_000, 100_000)
DTYPE = "uint8"  # valores enteros 0-9, 1 byte c/u
CHUNK = (500, 500)  # tamaño de bloque = tamaño de ventana inicial

# 10 niveles de brillo (0=oscuro, 9=claro) -> colormap secuencial "gray"
# (no "tab10": ese es cualitativo/sin orden, rompe la continuidad de la foto)
N_CATEGORIAS = 10
CMAP = "gray"


def cargar_foto_categorizada(ruta_foto, n_categorias):
    # "L" = escala de grises por luminancia (PIL usa la fórmula estándar
    # L = 0.299*R + 0.587*G + 0.114*B). Luego se reparte el rango 0-255
    # en n_categorias bandas iguales: 0 = más oscuro, n-1 = más claro.
    # rotate(-90, expand=True): la foto original quedó horizontal, se gira
    # a vertical (sentido horario) antes de usarla como tile del mosaico.
    img = Image.open(ruta_foto).convert("L").rotate(-90, expand=True)
    gris = np.asarray(img, dtype=np.uint16)
    return ((gris * n_categorias) // 256).astype(np.uint8)


def verificar_matriz(z, forma):
    completo = z.nchunks_initialized == z.nchunks
    estado = "OK" if completo else "INCOMPLETA"
    print(
        f"Verificación [{estado}]: {z.nchunks_initialized}/{z.nchunks} chunks escritos, "
        f"shape={z.shape} (esperado {forma}), {z.nbytes_stored() / 1e9:.2f} GB en disco."
    )
    return completo


def crear_matriz_si_no_existe(ruta, forma, dtype, chunk, foto_categorizada, banda_filas=2000):
    if os.path.exists(ruta):
        return
    print(f"Creando matriz {forma} en disco ({ruta}) a partir de la foto (mosaico)... esto puede tardar varios minutos.")
    z = zarr.open(ruta, mode="w", shape=forma, chunks=chunk, dtype=dtype)
    img_h, img_w = foto_categorizada.shape
    col_idx = np.arange(forma[1]) % img_w
    for inicio in range(0, forma[0], banda_filas):
        fin = min(inicio + banda_filas, forma[0])
        fila_idx = np.arange(inicio, fin) % img_h
        z[inicio:fin, :] = foto_categorizada[np.ix_(fila_idx, col_idx)]
        print(f"  {fin}/{forma[0]} filas generadas", end="\r")
    print("\nMatriz creada.")
    verificar_matriz(z, forma)


foto_categorizada = cargar_foto_categorizada(RUTA_FOTO, N_CATEGORIAS)
crear_matriz_si_no_existe(RUTA_MATRIZ, FORMA, DTYPE, CHUNK, foto_categorizada)
matriz = zarr.open(RUTA_MATRIZ, mode="r")
verificar_matriz(matriz, FORMA)

# Tamaño de la ventana visible (nivel de zoom)
ventana = 500
ventana_min = 50
# Tope de zoom-out: más allá de esto no aporta detalle visible y satura la RAM/render
ventana_max = 5_000

# Posición inicial
x0, y0 = 0, 0

fig, ax = plt.subplots(figsize=(8, 8))
plt.subplots_adjust(bottom=0.2)

# Mostrar trozo inicial
vista = matriz[y0:y0+ventana, x0:x0+ventana]
img = ax.imshow(vista, cmap=CMAP, vmin=0, vmax=N_CATEGORIAS - 1)
ax.set_title("Sliders para moverte, rueda del mouse para zoom")

cbar = fig.colorbar(img, ax=ax, ticks=range(N_CATEGORIAS))
cbar.set_label("Valor (0-9)")

# Slider horizontal (columnas)
ax_x = plt.axes([0.2, 0.08, 0.6, 0.03])
slider_x = Slider(ax_x, "← →", 0, matriz.shape[1] - ventana, valinit=0, valstep=100)

# Slider vertical (filas)
ax_y = plt.axes([0.2, 0.03, 0.6, 0.03])
slider_y = Slider(ax_y, "↑ ↓", 0, matriz.shape[0] - ventana, valinit=0, valstep=100)


def actualizar(val=None):
    x = int(slider_x.val)
    y = int(slider_y.val)
    img.set_data(matriz[y:y+ventana, x:x+ventana])
    img.set_extent((x, x+ventana, y+ventana, y))
    ax.set_title(f"Filas {y}-{y+ventana}, columnas {x}-{x+ventana} (zoom: {ventana}px)")
    fig.canvas.draw_idle()


def zoom(event):
    global ventana
    if event.inaxes != ax:
        return

    # Centro actual de la vista, para hacer zoom sobre ese punto
    x_centro = slider_x.val + ventana / 2
    y_centro = slider_y.val + ventana / 2

    factor = 0.8 if event.button == "up" else 1.25
    nueva_ventana = int(np.clip(ventana * factor, ventana_min, ventana_max))
    if nueva_ventana == ventana:
        return
    ventana = nueva_ventana

    x_max = matriz.shape[1] - ventana
    y_max = matriz.shape[0] - ventana
    slider_x.valmax = x_max
    slider_y.valmax = y_max
    slider_x.ax.set_xlim(slider_x.valmin, x_max)
    slider_y.ax.set_xlim(slider_y.valmin, y_max)

    nuevo_x = int(np.clip(x_centro - ventana / 2, 0, x_max))
    nuevo_y = int(np.clip(y_centro - ventana / 2, 0, y_max))
    slider_x.set_val(nuevo_x)
    slider_y.set_val(nuevo_y)
    actualizar()


slider_x.on_changed(actualizar)
slider_y.on_changed(actualizar)
fig.canvas.mpl_connect("scroll_event", zoom)

plt.show()
