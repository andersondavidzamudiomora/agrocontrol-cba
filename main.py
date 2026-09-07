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


# ---------------------------------------------------------------------------
# Utilidades de entrada (RF18: entradas invalidas sin cerrar el programa)
# ---------------------------------------------------------------------------

def leer_texto(mensaje, obligatorio=False):
    """Solicita texto al usuario. Si es obligatorio, no acepta valores vacios."""
    while True:
        valor = input(mensaje).strip()
        if not valor and obligatorio:
            print("Error: este campo es obligatorio.")
            continue
        return valor


def leer_numero(mensaje, tipo=float, minimo=None):
    """Solicita un numero valido. Repite hasta que la entrada sea correcta."""
    while True:
        texto = input(mensaje).strip()
        try:
            valor = tipo(texto)
        except ValueError:
            print(f"Error: debe ingresar un valor numerico valido ({texto!r}).")
            continue
        if minimo is not None and valor < minimo:
            print(f"Error: el valor debe ser mayor o igual a {minimo}.")
            continue
        return valor


def leer_opcion(mensaje, opciones):
    """Solicita una opcion valida dentro de un rango definido."""
    while True:
        texto = input(mensaje).strip()
        if texto in opciones:
            return texto
        print(f"Error: opcion invalida. Elija una de: {', '.join(opciones)}.")


# ---------------------------------------------------------------------------
# Gestion de productos (RF01 - RF04)
# ---------------------------------------------------------------------------

def obtener_producto(datos, codigo):
    """Devuelve el producto con el codigo dado, o None si no existe."""
    for producto in datos["productos"]:
        if producto["codigo"] == codigo:
            return producto
    return None


def registrar_producto(datos):
    """RF01: Registra un producto validando codigo unico, precio > 0 y stock minimo >= 0."""
    print("\n--- Registrar producto ---")
    codigo = leer_texto("Codigo (ej. P001): ", obligatorio=True).upper()
    if obtener_producto(datos, codigo):
        print(f"Error: ya existe un producto con el codigo {codigo}. No se registro.")
        return

    nombre = leer_texto("Nombre: ", obligatorio=True)
    categoria = leer_texto("Categoria: ", obligatorio=True)
    unidad = leer_texto("Unidad (unidad/kg/libra): ", obligatorio=True)
    precio = leer_numero("Precio: ", tipo=float, minimo=0.0001)
    stock_minimo = leer_numero("Stock minimo: ", tipo=float, minimo=0)

    producto = {
        "codigo": codigo,
        "nombre": nombre,
        "categoria": categoria,
        "unidad": unidad,
        "precio": round(precio, 2),
        "stock_minimo": stock_minimo,
        "activo": True,
    }
    datos["productos"].append(producto)
    guardar_datos(datos)
    print(f"Producto {codigo} registrado correctamente.")


def listar_productos(datos, solo_activos=True):
    """RF02: Lista productos activos (o todos)."""
    productos = datos["productos"]
    if solo_activos:
        productos = [p for p in productos if p["activo"]]
    if not productos:
        print("\nNo hay productos para mostrar.")
        return
    print("\n--- Lista de productos ---")
    print(f"{'Codigo':<8} {'Nombre':<25} {'Categoria':<15} {'Precio':>10} {'Stock min':>10} {'Activo'}")
    print("-" * 80)
    for p in productos:
        estado = "SI" if p["activo"] else "NO"
        print(f"{p['codigo']:<8} {p['nombre']:<25} {p['categoria']:<15} {p['precio']:>10.2f} "
              f"{p['stock_minimo']:>10} {estado}")


def buscar_producto(datos, texto):
    """RF02: Busca productos por codigo exacto o parte del nombre (activos)."""
    texto = texto.strip().upper()
    resultados = [p for p in datos["productos"] if p["activo"]
                  and (texto in p["codigo"].upper() or texto in p["nombre"].upper())]
    if not resultados:
        print(f"\nNo se encontraron productos que coincidan con {texto!r}.")
        return
    print(f"\n--- Resultados de busqueda para {texto!r} ---")
    for p in resultados:
        print(f"{p['codigo']}: {p['nombre']} ({p['categoria']}) - ${p['precio']:.2f} por {p['unidad']}")


def actualizar_producto(datos):
    """RF03: Actualiza nombre, categoria, unidad, precio y stock minimo sin cambiar el codigo."""
    print("\n--- Actualizar producto ---")
    codigo = leer_texto("Codigo del producto: ", obligatorio=True).upper()
    producto = obtener_producto(datos, codigo)
    if not producto:
        print(f"Error: no existe el producto {codigo}.")
        return

    print(f"Actualizando {codigo} - {producto['nombre']} (deje en blanco para conservar el valor)")
    nombre = leer_texto(f"Nombre [{producto['nombre']}]: ")
    categoria = leer_texto(f"Categoria [{producto['categoria']}]: ")
    unidad = leer_texto(f"Unidad [{producto['unidad']}]: ")
    precio_texto = input(f"Precio [{producto['precio']}]: ").strip()
    min_texto = input(f"Stock minimo [{producto['stock_minimo']}]: ").strip()

    if nombre:
        producto["nombre"] = nombre
    if categoria:
        producto["categoria"] = categoria
    if unidad:
        producto["unidad"] = unidad
    if precio_texto:
        try:
            precio = float(precio_texto)
            if precio <= 0:
                print("Error: el precio debe ser mayor que 0. No se cambio.")
            else:
                producto["precio"] = round(precio, 2)
        except ValueError:
            print(f"Error: {precio_texto!r} no es un precio valido. No se cambio.")
    if min_texto:
        try:
            stock_minimo = float(min_texto)
            if stock_minimo < 0:
                print("Error: el stock minimo no puede ser negativo. No se cambio.")
            else:
                producto["stock_minimo"] = stock_minimo
        except ValueError:
            print(f"Error: {min_texto!r} no es un stock minimo valido. No se cambio.")

    guardar_datos(datos)
    print(f"Producto {codigo} actualizado correctamente.")


def desactivar_producto(datos):
    """RF04: Desactiva un producto. Conserva su historial, no lo elimina fisicamente."""
    print("\n--- Desactivar producto ---")
    codigo = leer_texto("Codigo del producto: ", obligatorio=True).upper()
    producto = obtener_producto(datos, codigo)
    if not producto:
        print(f"Error: no existe el producto {codigo}.")
        return
    if not producto["activo"]:
        print(f"El producto {codigo} ya estaba desactivado.")
        return

    confirmar = leer_texto(f"Confirma desactivar {codigo} ({producto['nombre']})? [s/N]: ").lower()
    if confirmar != "s":
        print("Operacion cancelada.")
        return
    producto["activo"] = False
    guardar_datos(datos)
    print(f"Producto {codigo} desactivado. Su historial se conserva.")


def menu_productos(datos):
    """Menu secundario de gestion de productos."""
    while True:
        print("\n=== GESTION DE PRODUCTOS ===")
        print("1. Registrar producto")
        print("2. Listar productos")
        print("3. Buscar producto")
        print("4. Actualizar producto")
        print("5. Desactivar producto")
        print("0. Volver")
        opcion = leer_opcion("Seleccione una opcion: ", {"0", "1", "2", "3", "4", "5"})
        if opcion == "1":
            registrar_producto(datos)
        elif opcion == "2":
            listar_productos(datos)
        elif opcion == "3":
            texto = leer_texto("Texto a buscar (codigo o parte del nombre): ")
            if texto:
                buscar_producto(datos, texto)
            else:
                print("Debe escribir un texto de busqueda.")
        elif opcion == "4":
            actualizar_producto(datos)
        elif opcion == "5":
            desactivar_producto(datos)
        else:
            break


def main():
    """Punto de entrada principal de la aplicacion."""
    print("AgroControl CBA - en construccion")


if __name__ == "__main__":
    main()