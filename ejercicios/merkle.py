import hashlib


def sha256(data: str) -> str:
    return hashlib.sha256(data.encode()).hexdigest()


def combinar(izq: str, der: str) -> str:
    return sha256(izq + der)


def construir_arbol(transacciones: list[str]) -> list[list[str]]:
    """
    Construye un arbol de Merkle a partir de una lista de N transacciones.
    Devuelve la lista de niveles: nivel[0] son las hojas (hash de cada Tx),
    el ultimo nivel contiene un unico elemento: el Root Hash.

    Regla para N impar: el hash que queda sin pareja en un nivel se
    promueve tal cual al siguiente nivel (no se duplica), tal como H5
    en el diagrama de 5 transacciones.
    """
    if not transacciones:
        raise ValueError("Se necesita al menos una transaccion")

    nivel_actual = [sha256(tx) for tx in transacciones]
    niveles = [nivel_actual]

    while len(nivel_actual) > 1:
        siguiente_nivel = []
        i = 0
        while i < len(nivel_actual):
            if i + 1 < len(nivel_actual):
                siguiente_nivel.append(combinar(nivel_actual[i], nivel_actual[i + 1]))
                i += 2
            else:
                # nodo impar: se promueve sin combinar
                siguiente_nivel.append(nivel_actual[i])
                i += 1
        niveles.append(siguiente_nivel)
        nivel_actual = siguiente_nivel

    return niveles


def imprimir_arbol(niveles: list[list[str]], largo: int = 8) -> None:
    etiquetas_nivel_hojas = None
    total_niveles = len(niveles)

    for idx, nivel in enumerate(niveles):
        nombre = "Root Hash" if idx == total_niveles - 1 else f"Nivel {idx}"
        resumen = "  ".join(h[:largo] for h in nivel)
        print(f"{nombre:12}: {resumen}")


def root_hash(transacciones: list[str]) -> str:
    return construir_arbol(transacciones)[-1][0]


if __name__ == "__main__":
    N = 5  # <-- cambia este numero para probar con distinta cantidad de transacciones
    transacciones = [f"Tx{i}" for i in range(1, N + 1)]
    arbol = construir_arbol(transacciones)
    imprimir_arbol(arbol)
    print(f"\nRoot Hash: {root_hash(transacciones)}")
