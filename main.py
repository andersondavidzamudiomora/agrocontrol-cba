import csv
import json
import os
import shutil
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

ARCHIVOS = {
    "productos": DATA_DIR / "productos.json",
    "lotes": DATA_DIR / "lotes.json",
    "movimientos": DATA_DIR / "movimientos.json",
    "ventas": DATA_DIR / "ventas.json",
}

ESTADOS_LOTE = ("EN_PRODUCCION", "COSECHADO", "CANCELADO")


# Menu principal


def main():
    """Punto de entrada principal: carga datos y muestra el menu hasta salir."""
    datos = cargar_datos()
    print("==================== AGROCONTROL  CBA  ====================")
    print("Sistema monolitico de produccion, inventario y ventas")

    while True:
        print("\n==================== AGROCONTROL  CBA  ====================")
        print("1. Gestion de productos")
        print("2. Gestion de lotes productivos")
        print("3. Movimientos de inventario")
        print("4. Registrar venta")
        print("5. Consultar ventas")
        print("6. Alertas de stock")
        print("7. Reportes")
        print("8. Guardar datos")
        print("0. Salir")
        opcion = leer_opcion("Seleccione una opcion: ",
                             {"0", "1", "2", "3", "4", "5", "6", "7", "8"})

        if opcion == "1":
            menu_productos(datos)
        elif opcion == "2":
            menu_lotes(datos)
        elif opcion == "3":
            menu_inventario(datos)
        elif opcion == "4":
            registrar_venta(datos)
        elif opcion == "5":
            consultar_ventas(datos)
        elif opcion == "6":
            mostrar_alertas(datos)
        elif opcion == "7":
            menu_reportes(datos)
        elif opcion == "8":
            guardar_datos(datos)
            print("Datos guardados en la carpeta data/.")
        else:
            guardar_datos(datos)
            print("\nDatos guardados. Hasta pronto!")
            break


def leer_json(ruta):
    """Lee un archivo JSON y devuelve su contenido.

    Si el archivo no existe o esta corrupto, devuelve una lista vacia.
    """
    if not ruta.exists():
        return []
    try:
        with open(ruta, "r", encoding="utf-8") as f:
            datos = json.load(f)
        # Si el archivo esta corrupto o no contiene una lista, se reinicia vacio
        if not isinstance(datos, list):
            return []
        return datos
    except (json.JSONDecodeError, OSError, UnicodeDecodeError):
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
    """Guarda inmediatamente todos los datos en sus archivos JSON.

    Reto cumplido: antes de sobrescribir, copia los archivos existentes a
    data/backups/ con marca de tiempo.
    """
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    backup_dir = DATA_DIR / "backups"
    backup_dir.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    for clave, ruta in ARCHIVOS.items():
        if ruta.exists():
            shutil.copy2(ruta, backup_dir / f"{timestamp}_{clave}.json")
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



# Utilidades de entrada


def leer_texto(mensaje, obligatorio=False):
    """Solicita texto al usuario. Si es obligatorio, no acepta valores vacios."""
    while True:
        valor = input(mensaje).strip()
        if not valor and obligatorio:
            print("Error: este campo es obligatorio.")
            continue
        return valor


def leer_letras(mensaje, obligatorio=False):
    """Solicita texto formado solo por letras y espacios."""
    while True:
        valor = input(mensaje).strip()
        if not valor and obligatorio:
            print("Error: este campo es obligatorio.")
            continue
        if valor and not all(caracter.isalpha() or caracter.isspace() for caracter in valor):
            print("Error: solo se permiten letras y espacios.")
            continue
        return valor


def leer_unidad(mensaje, obligatorio=False):
    """Solicita una unidad o cantidad, como kg, unidad o 10 unidades."""
    while True:
        valor = input(mensaje).strip()
        if not valor and obligatorio:
            print("Error: este campo es obligatorio.")
            continue
        if valor and not all(caracter.isalnum() or caracter.isspace() or caracter in "/.-" for caracter in valor):
            print("Error: la unidad solo puede contener letras, numeros y espacios.")
            continue
        return valor


def leer_numero(mensaje, tipo=int, minimo=None):
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


def leer_fecha_siembra(mensaje):
    """Solicita una fecha obligatoria en formato AAAA-MM-DD (ISO 8601)."""
    while True:
        texto = input(mensaje).strip()
        try:
            fecha = datetime.strptime(texto, "%Y-%m-%d")
        except (ValueError, OverflowError, OSError):
            print("Error: la fecha debe tener el formato AAAA-MM-DD y ser valida.")
            continue
        if fecha.year < 2000 or fecha.year > 2100:
            print("Error: el ano debe estar entre 2000 y 2100.")
            continue
        return fecha.strftime("%Y-%m-%d")


def leer_opcion(mensaje, opciones):
    """Solicita una opcion valida dentro de un rango definido."""
    while True:
        texto = input(mensaje).strip()
        if texto in opciones:
            return texto
        print(f"Error: opcion invalida. Elija una de: {', '.join(opciones)}.")


# Gestion de productos (RF01 - RF04)


def obtener_producto(datos, codigo):
    """Devuelve el producto con el codigo dado, o None si no existe."""
    for producto in datos["productos"]:
        if producto["codigo"] == codigo:
            return producto
    return None


def registrar_producto(datos):
    """RF01: Registra un producto validando codigo unico, precio > 0 y stock minimo >= 0."""
    print("\n--- Registrar producto ---")
    while True:
        codigo = leer_texto("Codigo (ej. P001): ", obligatorio=True).upper()
        if not obtener_producto(datos, codigo):
            break
        print(f"Error: ya existe un producto con el codigo {codigo}. Intente otro.")

    nombre = leer_letras("Nombre: ", obligatorio=True)
    categoria = leer_letras("Categoria: ", obligatorio=True)
    unidad = leer_unidad("Unidad o cantidad (ej. unidad, kg, 10 unidades): ", obligatorio=True)
    precio = leer_numero("Precio: ", tipo=float, minimo=0.01)
    stock_minimo = leer_numero("Stock minimo: ", tipo=float, minimo=0)

    producto = {
        "codigo": codigo,
        "nombre": nombre,
        "categoria": categoria,
        "unidad": unidad,
        "precio": precio,
        "stock_minimo": stock_minimo,
        "activo": True,
    }
    datos["productos"].append(producto)
    guardar_datos(datos)
    print(f"Producto {codigo} registrado correctamente.")


def listar_productos(datos, solo_activos=False):
    """RF02: Lista todos los productos y muestra si estan activos."""
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
              f"{p['stock_minimo']:>10.2f} {estado}")


def buscar_producto(datos, texto):
    """RF02: Busca productos por codigo exacto o parte del nombre (activos)."""
    texto = texto.strip().upper()
    resultados = [p for p in datos["productos"] if p["activo"]
                  and (texto in p["codigo"].upper() or texto in p["nombre"].upper())]
    if not resultados:
        print(f"\nNo se encontraron productos que coincidan con {texto!r}.")
        return
    print(f"\n--- Resultados de busqueda para {texto!r} ---")
    print(f"{'Codigo':<7} {'Nombre':<20} {'Categoria':<13} {'Precio':>9} {'Unidad':<8} {'Stock min':>9}")
    print("-" * 74)
    for p in resultados:
        print(f"{p['codigo']:<7} {p['nombre']:<20} {p['categoria']:<13} {p['precio']:>9.2f} "
              f"{p['unidad']:<8} {p['stock_minimo']:>9.2f}")


def actualizar_producto(datos):
    """RF03: Actualiza nombre, categoria, unidad, precio y stock minimo sin cambiar el codigo."""
    print("\n--- Actualizar producto ---")
    while True:
        codigo = leer_texto("Codigo del producto: ", obligatorio=True).upper()
        producto = obtener_producto(datos, codigo)
        if producto:
            break
        print(f"Error: no existe el producto {codigo}. Intente nuevamente.")

    print(f"Actualizando {codigo} - {producto['nombre']} (deje en blanco para conservar el valor)")
    nombre = leer_letras(f"Nombre [{producto['nombre']}]: ")
    categoria = leer_letras(f"Categoria [{producto['categoria']}]: ")
    unidad = leer_unidad(f"Unidad [{producto['unidad']}]: ")
    precio_texto = input(f"Precio [{producto['precio']:g}]: ").strip()
    min_texto = input(f"Stock minimo [{producto['stock_minimo']:g}]: ").strip()

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
                producto["precio"] = precio
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
    while True:
        codigo = leer_texto("Codigo del producto: ", obligatorio=True).upper()
        producto = obtener_producto(datos, codigo)
        if producto:
            break
        print(f"Error: no existe el producto {codigo}. Intente nuevamente.")
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


def reactivar_producto(datos):
    """Reactiva un producto desactivado sin modificar su historial."""
    print("\n--- Reactivar producto ---")
    while True:
        codigo = leer_texto("Codigo del producto: ", obligatorio=True).upper()
        producto = obtener_producto(datos, codigo)
        if producto:
            break
        print(f"Error: no existe el producto {codigo}. Intente nuevamente.")
    if producto["activo"]:
        print(f"El producto {codigo} ya esta activo.")
        return

    confirmar = leer_texto(f"Confirma reactivar {codigo} ({producto['nombre']})? [s/N]: ").lower()
    if confirmar != "s":
        print("Operacion cancelada.")
        return
    producto["activo"] = True
    guardar_datos(datos)
    print(f"Producto {codigo} reactivado correctamente.")

def menu_productos(datos):
    """Menu secundario de gestion de productos."""
    while True:
        print("\n=== GESTION DE PRODUCTOS ===")
        print("1. Registrar producto")
        print("2. Listar productos")
        print("3. Buscar producto")
        print("4. Actualizar producto")
        print("5. Desactivar producto")
        print("6. Reactivar producto")
        print("0. Volver")
        opcion = leer_opcion("Seleccione una opcion: ", {"0", "1", "2", "3", "4", "5", "6"})
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
        elif opcion == "6":
            reactivar_producto(datos)
        else:
            break


def obtener_lote(datos, id_lote):
    """Devuelve el lote con el id dado, o None si no existe."""
    for lote in datos["lotes"]:
        if lote["id_lote"] == id_lote:
            return lote
    return None


def registrar_movimiento(datos, producto_codigo, tipo, cantidad, motivo):
    """Crea y guarda un movimiento de inventario (ENTRADA o SALIDA)."""
    movimiento = {
        "id": generar_id("M", datos["movimientos"]),
        "producto_codigo": producto_codigo,
        "tipo": tipo,
        "cantidad": cantidad,
        "motivo": motivo,
        "fecha": fecha_actual(),
    }
    datos["movimientos"].append(movimiento)
    guardar_datos(datos)
    return movimiento


def registrar_lote(datos):
    """RF05: Registra un lote asociado unicamente a un producto existente y activo."""
    print("\n--- Registrar lote productivo ---")
    while True:
        codigo_producto = leer_texto("Codigo del producto: ", obligatorio=True).upper()
        producto = obtener_producto(datos, codigo_producto)
        if not producto:
            print(f"Error: no existe el producto {codigo_producto}. Intente nuevamente.")
        elif not producto["activo"]:
            print(f"Error: el producto {codigo_producto} esta desactivado. Intente nuevamente.")
        else:
            break

    while True:
        id_lote = leer_texto("Id del lote (ej. L001): ", obligatorio=True).upper()
        if not obtener_lote(datos, id_lote):
            break
        print(f"Error: ya existe un lote con el id {id_lote}. Intente otro.")

    fecha_siembra = leer_fecha_siembra("Fecha de siembra (AAAA-MM-DD): ")
    area_m2 = leer_numero("Area (m2): ", tipo=int, minimo=1)

    lote = {
        "id_lote": id_lote,
        "producto_codigo": codigo_producto,
        "fecha_siembra": fecha_siembra,
        "area_m2": area_m2,
        "cantidad_producida": 0,
        "estado": "EN_PRODUCCION",
    }
    datos["lotes"].append(lote)
    guardar_datos(datos)
    print(f"Lote {id_lote} registrado correctamente.")


def listar_lotes(datos):
    """Lista todos los lotes registrados."""
    if not datos["lotes"]:
        print("\nNo hay lotes registrados.")
        return
    print("\n--- Lista de lotes ---")
    print(f"{'Lote':<8} {'Producto':<10} {'Siembra':<12} {'Area m2':>10} {'Producido':>12} {'Estado'}")
    print("-" * 70)
    for l in datos["lotes"]:
        print(f"{l['id_lote']:<8} {l['producto_codigo']:<10} {l['fecha_siembra']:<12} "
              f"{l['area_m2']:>10} {l['cantidad_producida']:>12} {l['estado']}")


def cosechar_lote(datos):
    """RF07: Cosecha un lote, registra la cantidad producida y genera una entrada automatica.

    Regla 5: un lote no puede cosecharse dos veces (su estado pasa a COSECHADO).
    """
    print("\n--- Cosechar lote ---")
    while True:
        id_lote = leer_texto("Id del lote: ", obligatorio=True).upper()
        lote = obtener_lote(datos, id_lote)
        if not lote:
            print(f"Error: no existe el lote {id_lote}. Intente nuevamente.")
        elif lote["estado"] != "EN_PRODUCCION":
            print(f"Error: el lote {id_lote} ya no esta en produccion (estado: {lote['estado']}). "
                  "Intente con otro lote.")
        else:
            break
    cantidad = leer_numero("Cantidad producida: ", tipo=int, minimo=1)
    lote["cantidad_producida"] = cantidad
    lote["estado"] = "COSECHADO"

    # Entrada automatica de inventario por la cosecha
    registrar_movimiento(
        datos,
        lote["producto_codigo"],
        "ENTRADA",
        cantidad,
        f"Cosecha lote {id_lote}",
    )
    guardar_datos(datos)
    print(f"Lote {id_lote} cosechado: {cantidad} unidades entraron al inventario.")


def cambiar_estado_lote(datos):
    """RF06: Permite cancelar un lote en produccion."""
    print("\n--- Cambiar estado de lote ---")
    while True:
        id_lote = leer_texto("Id del lote: ", obligatorio=True).upper()
        lote = obtener_lote(datos, id_lote)
        if not lote:
            print(f"Error: no existe el lote {id_lote}. Intente nuevamente.")
        elif lote["estado"] == "COSECHADO":
            print("Error: un lote cosechado no puede cambiar de estado. Intente con otro lote.")
        elif lote["estado"] == "CANCELADO":
            print("Error: un lote cancelado no puede reactivarse. Intente con otro lote.")
        else:
            break

    print(f"Lote {id_lote} - estado actual: {lote['estado']}")

    print("Estados disponibles: EN_PRODUCCION, CANCELADO")
    while True:
        nuevo_estado = leer_texto("Nuevo estado: ", obligatorio=True).upper()
        if nuevo_estado in ("EN_PRODUCCION", "CANCELADO"):
            break
        print(f"Error: {nuevo_estado} no es un estado valido. Intente nuevamente.")
    if nuevo_estado == lote["estado"]:
        print("El lote ya se encuentra en ese estado.")
        return
    lote["estado"] = nuevo_estado
    guardar_datos(datos)
    print(f"Lote {id_lote} cambio a estado {nuevo_estado}.")


def menu_lotes(datos):
    """Menu secundario de gestion de lotes productivos."""
    while True:
        print("\n=== GESTION DE LOTES PRODUCTIVOS ===")
        print("1. Registrar lote")
        print("2. Listar lotes")
        print("3. Cosechar lote")
        print("4. Cambiar estado de lote")
        print("0. Volver")
        opcion = leer_opcion("Seleccione una opcion: ", {"0", "1", "2", "3", "4"})
        if opcion == "1":
            registrar_lote(datos)
        elif opcion == "2":
            listar_lotes(datos)
        elif opcion == "3":
            cosechar_lote(datos)
        elif opcion == "4":
            cambiar_estado_lote(datos)
        else:
            break


# Inventario

def calcular_stock(datos, codigo_producto):
    """Regla 3: calcula el stock actual a partir de los movimientos de inventario.

    El stock no se guarda como dato aislado: entradas menos salidas.
    """
    stock = 0.0
    for m in datos["movimientos"]:
        if m["producto_codigo"] == codigo_producto:
            if m["tipo"] == "ENTRADA":
                stock += m["cantidad"]
            elif m["tipo"] == "SALIDA":
                stock -= m["cantidad"]
    return stock


def validar_producto_para_operacion(datos, codigo):
    """Verifica que el producto exista y este activo. Devuelve el producto o None."""
    producto = obtener_producto(datos, codigo)
    if not producto:
        print(f"Error: no existe el producto {codigo}.")
        return None
    if not producto["activo"]:
        print(f"Error: el producto {codigo} esta desactivado y no puede operarse.")
        return None
    return producto


def entrada_manual(datos):
    """RF08: Entrada manual de inventario con motivo obligatorio."""
    print("\n--- Entrada manual de inventario ---")
    while True:
        codigo = leer_texto("Codigo del producto: ", obligatorio=True).upper()
        if validar_producto_para_operacion(datos, codigo):
            break
        print("Intente nuevamente.")
    cantidad = leer_numero("Cantidad: ", tipo=float, minimo=0.0001)
    motivo = leer_texto("Motivo (obligatorio): ", obligatorio=True)
    registrar_movimiento(datos, codigo, "ENTRADA", cantidad, motivo)
    print(f"Entrada registrada. Stock actual de {codigo}: {calcular_stock(datos, codigo):g}")


def salida_manual(datos):
    """RF09: Salida manual solo si existe stock suficiente (regla 4)."""
    print("\n--- Salida manual de inventario ---")
    while True:
        codigo = leer_texto("Codigo del producto: ", obligatorio=True).upper()
        if validar_producto_para_operacion(datos, codigo):
            break
        print("Intente nuevamente.")
    stock = calcular_stock(datos, codigo)
    print(f"Stock disponible de {codigo}: {stock:g}")
    cantidad = leer_numero("Cantidad a sacar: ", tipo=float, minimo=0.0001)
    if cantidad > stock:
        print(f"Error: stock insuficiente. Disponible: {stock:g}, solicitado: {cantidad:g}. "
              "La salida no se registro.")
        return
    motivo = leer_texto("Motivo (obligatorio): ", obligatorio=True)
    registrar_movimiento(datos, codigo, "SALIDA", cantidad, motivo)
    print(f"Salida registrada. Stock actual de {codigo}: {calcular_stock(datos, codigo):g}")


def listar_movimientos(datos):
    """Lista los movimientos de inventario, opcionalmente filtrados por producto."""
    codigo = leer_texto("Codigo del producto (vacio para todos): ").upper()
    movimientos = datos["movimientos"]
    if codigo:
        movimientos = [m for m in movimientos if m["producto_codigo"] == codigo]
    if not movimientos:
        print("\nNo hay movimientos para mostrar.")
        return
    print("\n--- Movimientos de inventario ---")
    print(f"{'Id':<8} {'Producto':<10} {'Tipo':<10} {'Cantidad':>10} {'Motivo':<30} Fecha")
    print("-" * 95)
    for m in movimientos:
        print(f"{m['id']:<8} {m['producto_codigo']:<10} {m['tipo']:<10} "
              f"{m['cantidad']:>10g} {m['motivo']:<30} {m['fecha']}")


def menu_inventario(datos):
    """Menu secundario de movimientos de inventario."""
    while True:
        print("\n=== MOVIMIENTOS DE INVENTARIO ===")
        print("1. Entrada manual")
        print("2. Salida manual")
        print("3. Listar movimientos")
        print("4. Consultar stock de un producto")
        print("0. Volver")
        opcion = leer_opcion("Seleccione una opcion: ", {"0", "1", "2", "3", "4"})
        if opcion == "1":
            entrada_manual(datos)
        elif opcion == "2":
            salida_manual(datos)
        elif opcion == "3":
            listar_movimientos(datos)
        elif opcion == "4":
            while True:
                codigo = leer_texto("Codigo del producto: ", obligatorio=True).upper()
                if obtener_producto(datos, codigo):
                    print(f"Stock de {codigo}: {calcular_stock(datos, codigo):g}")
                    break
                print(f"Error: no existe el producto {codigo}. Intente nuevamente.")
        else:
            break


# ---------------------------------------------------------------------------
# Ventas (RF10 - RF11)
# ---------------------------------------------------------------------------

def registrar_venta(datos):
    """RF10/RF11: Registra una venta con uno o varios productos.

    Valida primero TODOS los items y el stock de cada uno; solo si la
    venta completa es valida se descuenta inventario y se guarda.
    El precio se toma del precio vigente del producto (regla 7).
    """
    print("\n--- Registrar venta ---")
    print("Ingrese los productos de la venta. Codigo vacio para terminar.")

    items = []
    while True:
        codigo = leer_texto("Codigo del producto (vacio para terminar): ").upper()
        if not codigo:
            if not items:
                print("Error: la venta debe contener al menos un item valido (regla 6).")
                continue
            break
        producto = validar_producto_para_operacion(datos, codigo)
        if not producto:
            continue
        cantidad = leer_numero("Cantidad: ", tipo=float, minimo=0.0001)
        items.append({"codigo": codigo, "cantidad": cantidad, "precio_unitario": producto["precio"]})
        print(f"Item agregado: {producto['nombre']} x {cantidad} @ ${producto['precio']:.2f}")

    # Verificar stock de TODOS los items antes de registrar cualquier cosa
    necesidades = {}
    for item in items:
        necesidades[item["codigo"]] = necesidades.get(item["codigo"], 0) + item["cantidad"]
    for codigo, cantidad in necesidades.items():
        stock = calcular_stock(datos, codigo)
        if cantidad > stock:
            print(f"Error: stock insuficiente de {codigo}. Disponible: {stock}, solicitado: {cantidad}.")
            print("La venta NO se registro y el inventario no se modifico.")
            return

    subtotales = [item["cantidad"] * item["precio_unitario"] for item in items]
    total = round(sum(subtotales), 2)
    venta = {
        "id": generar_id("V", datos["ventas"]),
        "fecha": fecha_actual(),
        "items": [
            {"codigo": it["codigo"], "cantidad": it["cantidad"], "precio_unitario": it["precio_unitario"]}
            for it in items
        ],
        "total": total,
    }
    datos["ventas"].append(venta)

    # Descontar inventario: una salida por item
    for item in items:
        registrar_movimiento(
            datos,
            item["codigo"],
            "SALIDA",
            item["cantidad"],
            f"Venta {venta['id']}",
        )
    guardar_datos(datos)
    print(f"\nVenta {venta['id']} registrada. Total: ${total:.2f}")
    for item, sub in zip(items, subtotales):
        print(f"  - {item['codigo']} x {item['cantidad']} = ${sub:.2f}")


def consultar_ventas(datos):
    """Muestra las ventas registradas, opcionalmente filtradas por rango de fechas."""
    ventas = datos["ventas"]
    if not ventas:
        print("\nNo hay ventas registradas.")
        return

    print("\n--- Consultar ventas ---")
    desde = leer_texto("Fecha desde (YYYY-MM-DD, vacio para todas): ")
    hasta = leer_texto("Fecha hasta (YYYY-MM-DD, vacio para todas): ")
    if desde:
        ventas = [v for v in ventas if v["fecha"][:10] >= desde]
    if hasta:
        ventas = [v for v in ventas if v["fecha"][:10] <= hasta]
    if not ventas:
        print("No hay ventas en ese rango de fechas.")
        return

    for v in ventas:
        print(f"\nVenta {v['id']} - {v['fecha']} - Total: ${v['total']:.2f}")
        for item in v["items"]:
            sub = item["cantidad"] * item["precio_unitario"]
            print(f"   {item['codigo']} x {item['cantidad']} @ ${item['precio_unitario']:.2f} = ${sub:.2f}")


# ---------------------------------------------------------------------------
# Alertas y reportes (RF12 - RF15)
# ---------------------------------------------------------------------------

def mostrar_alertas(datos):
    """RF12: Muestra productos cuyo stock es menor o igual al stock minimo."""
    print("\n--- Alertas de stock ---")
    con_alerta = False
    for p in datos["productos"]:
        if not p["activo"]:
            continue
        stock = calcular_stock(datos, p["codigo"])
        if stock <= p["stock_minimo"]:
            con_alerta = True
            print(f"[ALERTA] {p['codigo']} {p['nombre']}: stock {stock} "
                  f"<= minimo {p['stock_minimo']}")
    if not con_alerta:
        print("No hay productos por debajo del stock minimo.")


def reporte_inventario(datos):
    """RF13: Reporte de existencias y valor del inventario a precio de venta."""
    print("\n--- Reporte de inventario ---")
    print(f"{'Codigo':<8} {'Nombre':<25} {'Stock':>10} {'Precio':>10} {'Valor':>12}")
    print("-" * 70)
    valor_total = 0.0
    for p in datos["productos"]:
        stock = calcular_stock(datos, p["codigo"])
        valor = stock * p["precio"]
        valor_total += valor
        print(f"{p['codigo']:<8} {p['nombre']:<25} {stock:>10} {p['precio']:>10.2f} {valor:>12.2f}")
    print("-" * 70)
    print(f"Valor total del inventario (a precio de venta): ${valor_total:.2f}")


def reporte_ventas(datos):
    """RF14: Numero de ventas, unidades vendidas e ingresos acumulados."""
    print("\n--- Reporte de ventas ---")
    if not datos["ventas"]:
        print("No hay ventas registradas.")
        return
    numero_ventas = len(datos["ventas"])
    unidades = sum(item["cantidad"] for v in datos["ventas"] for item in v["items"])
    ingresos = sum(v["total"] for v in datos["ventas"])
    print(f"Numero de ventas: {numero_ventas}")
    print(f"Unidades vendidas: {unidades}")
    print(f"Ingresos acumulados: ${ingresos:.2f}")


def ranking_productos(datos):
    """RF15: Ranking de los 3 productos con mayor cantidad vendida."""
    print("\n--- Ranking de productos mas vendidos ---")
    vendidos = {}
    for v in datos["ventas"]:
        for item in v["items"]:
            vendidos[item["codigo"]] = vendidos.get(item["codigo"], 0) + item["cantidad"]
    if not vendidos:
        print("No hay datos de ventas para calcular el ranking.")
        return
    top = sorted(vendidos.items(), key=lambda x: x[1], reverse=True)[:3]
    for i, (codigo, cantidad) in enumerate(top, start=1):
        producto = obtener_producto(datos, codigo)
        nombre = producto["nombre"] if producto else "(sin producto)"
        print(f"{i}. {codigo} {nombre}: {cantidad} unidades")


def exportar_inventario_csv(datos):
    """Reto: exporta el reporte de inventario a un archivo CSV (biblioteca csv)."""
    ruta_csv = DATA_DIR / "inventario.csv"
    with open(ruta_csv, "w", encoding="utf-8", newline="") as f:
        escritor = csv.writer(f)
        escritor.writerow(["codigo", "nombre", "stock", "precio", "valor"])
        for p in datos["productos"]:
            stock = calcular_stock(datos, p["codigo"])
            escritor.writerow([p["codigo"], p["nombre"], stock, p["precio"],
                               round(stock * p["precio"], 2)])
    print(f"Reporte de inventario exportado a {ruta_csv}")


def menu_reportes(datos):
    """Menu secundario de reportes."""
    while True:
        print("\n=== REPORTES ===")
        print("1. Reporte de inventario")
        print("2. Reporte de ventas")
        print("3. Ranking de los 3 productos mas vendidos")
        print("4. Exportar inventario a CSV")
        print("0. Volver")
        opcion = leer_opcion("Seleccione una opcion: ", {"0", "1", "2", "3", "4"})
        if opcion == "1":
            reporte_inventario(datos)
        elif opcion == "2":
            reporte_ventas(datos)
        elif opcion == "3":
            ranking_productos(datos)
        elif opcion == "4":
            exportar_inventario_csv(datos)
        else:
            break


if __name__ == "__main__":
    main()




