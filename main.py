"""AgroControl CBA - Sistema monolitico para gestion de produccion, inventario y ventas.

Aplicacion de consola con persistencia local en archivos JSON.
Solo utiliza modulos de la biblioteca estandar de Python.
"""

import json
import os
from datetime import datetime
from pathlib import Path

# ---------------------------------------------------------------------------
# Constantes y persistencia
# ---------------------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

ARCHIVOS = {
    "productos": DATA_DIR / "productos.json",
    "lotes": DATA_DIR / "lotes.json",
    "movimientos": DATA_DIR / "movimientos.json",
    "ventas": DATA_DIR / "ventas.json",
}


def leer_json(ruta):
    """Lee un archivo JSON y devuelve su contenido.

    Si el archivo no existe o esta corrupto, devuelve una lista vacia.
    """
    if not ruta.exists():
        return []
    try:
        with open(ruta, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return []


def escribir_json(ruta, datos):
    """Guarda datos en un archivo JSON con formato legible."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=4)


def cargar_datos():
    """Carga todos los archivos JSON. Si no existen, inicia con colecciones vacias."""
    return {
        "productos": leer_json(ARCHIVOS["productos"]),
        "lotes": leer_json(ARCHIVOS["lotes"]),
        "movimientos": leer_json(ARCHIVOS["movimientos"]),
        "ventas": leer_json(ARCHIVOS["ventas"]),
    }


def guardar_datos(datos):
    """Guarda inmediatamente todos los datos en sus archivos JSON."""
    for clave, ruta in ARCHIVOS.items():
        escribir_json(ruta, datos[clave])


def generar_id(prefijo, coleccion, digitos=4):
    """Genera un identificador secuencial, por ejemplo M0001, V0002.

    Toma el numero mas alto existente en la coleccion y le suma uno.
    """
    mayor = 0
    for elemento in coleccion:
        identificador = str(elemento.get("id", elemento.get("id_lote", "")))
        if identificador.startswith(prefijo):
            try:
                numero = int(identificador[len(prefijo):])
                if numero > mayor:
                    mayor = numero
            except ValueError:
                continue
    return f"{prefijo}{mayor + 1:0{digitos}d}"


def fecha_actual():
    """Devuelve la fecha y hora actual en formato YYYY-MM-DD HH:MM."""
    return datetime.now().strftime("%Y-%m-%d %H:%M")


def main():
    """Punto de entrada principal de la aplicacion."""
    print("AgroControl CBA - en construccion")


if __name__ == "__main__":
    main()