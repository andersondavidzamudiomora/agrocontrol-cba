import csv
import getpass
import json
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
USUARIOS = {
    "operador": {"clave": "operador123", "rol": "OPERADOR"},
    "admin": {"clave": "admin123", "rol": "ADMINISTRADOR"},
}


# Menu principal


def main():
    datos = cargar_datos()
    usuario = iniciar_sesion()
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
        print("9. Devolver venta")
        print("0. Salir")
        opcion = leer_opcion("Seleccione una opcion: ",
                             {"0", "1", "2", "3", "4", "5", "6", "7", "8", "9"})

        if opcion == "1":
            ejecutar_con_permiso(usuario, "ADMINISTRADOR", menu_productos, datos)
        elif opcion == "2":
            ejecutar_con_permiso(usuario, "ADMINISTRADOR", menu_lotes, datos)
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
        elif opcion == "9":
            ejecutar_con_permiso(usuario, "ADMINISTRADOR", devolver_venta, datos)
        else:
            guardar_datos(datos)
            print("\nDatos guardados. Hasta pronto!")
            break


def iniciar_sesion():
    """Solicita credenciales y devuelve el usuario autenticado."""
    print("\n--- Inicio de sesion ---")
    while True:
        nombre = leer_texto("Usuario: ").lower()
        clave = getpass.getpass("Clave: ")
        usuario = USUARIOS.get(nombre)
        if usuario and usuario["clave"] == clave:
            print(f"Sesion iniciada como {usuario['rol']}.")
            return {"nombre": nombre, "rol": usuario["rol"]}
        print("Error: usuario o clave incorrectos.")


def ejecutar_con_permiso(usuario, rol_requerido, funcion, datos):
    """Ejecuta una accion solo si el rol autenticado tiene permiso."""
    if usuario["rol"] != rol_requerido:
        print(f"Acceso denegado: esta accion requiere rol {rol_requerido}.")
        return
    funcion(datos)


def leer_json(ruta):

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
    """Solicita una fecha obligatoria en formato DD-MM-AAAA."""
    while True:
        texto = input(mensaje).strip()
        try:
            fecha = datetime.strptime(texto, "%d-%m-%Y")
        except (ValueError, OverflowError, OSError):
            print("Error: la fecha debe tener el formato DD-MM-AAAA y ser valida.")
            continue
        if fecha.year < 2000 or fecha.year > 2100:
            print("Error: el ano debe estar entre 2000 y 2100.")
            continue
        return fecha.strftime("%d-%m-%Y")


def leer_opcion(mensaje, opciones):
    """Solicita una opcion valida dentro de un rango definido."""
    while True:
        texto = input(mensaje).strip()
        if texto in opciones:
            return texto
        print(f"Error: opcion invalida. Elija una de: {', '.join(opciones)}.")


# Utilidades de presentacion


def imprimir_tabla(titulo, cabeceras, filas, derecha=()):
    """Imprime resultados en una tabla con bordes para que se lean ordenados.

    Si no hay filas muestra un aviso en lugar de una tabla vacia.
    derecha recibe los indices de las columnas alineadas a la derecha.
    """
    print(f"\n{titulo}")
    if not filas:
        print("No hay datos para mostrar.")
        return
    celdas = [[str(valor) for valor in fila] for fila in filas]
    cabecera_texto = [str(valor) for valor in cabeceras]
    anchos = [len(valor) for valor in cabecera_texto]
    for fila in celdas:
        for columna, valor in enumerate(fila):
            anchos[columna] = max(anchos[columna], len(valor))

    separador = "+" + "+".join("-" * (ancho + 2) for ancho in anchos) + "+"

    def fila_texto(valores):
        partes = []
        for columna, valor in enumerate(valores):
            if columna in derecha:
                partes.append(f" {valor.rjust(anchos[columna])} ")
            else:
                partes.append(f" {valor.ljust(anchos[columna])} ")
        return "|" + "|".join(partes) + "|"

    print(separador)
    print(fila_texto(cabecera_texto))
    print(separador)
    for fila in celdas:
        print(fila_texto(fila))
    print(separador)


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
        if len(codigo) != 4 or codigo[0] != "P" or not codigo[1:].isdigit():
            print("Error: el codigo debe tener el formato P000, por ejemplo P001.")
            continue
        if not obtener_producto(datos, codigo):
            break
        print(f"Error: ya existe un producto con el codigo {codigo}. Intente otro.")

    nombre = leer_letras("Nombre: ", obligatorio=True)
    categoria = leer_letras("Categoria: ", obligatorio=True)
    unidad = leer_unidad("Unidad o cantidad (ej. unidad, kg, 10 unidades): ", obligatorio=True)
    precio = leer_numero("Precio: ", tipo=float, minimo=0.01)
    costo_unitario = leer_numero("Costo unitario: ", tipo=float, minimo=0.01)
    stock_minimo = leer_numero("Stock minimo: ", tipo=float, minimo=0)

    producto = {
        "codigo": codigo,
        "nombre": nombre,
        "categoria": categoria,
        "unidad": unidad,
        "precio": precio,
        "costo_unitario": costo_unitario,
        "stock_minimo": stock_minimo,
        "activo": True,
    }
    datos["productos"].append(producto)
    guardar_datos(datos)
    print(f"Producto {codigo} registrado correctamente.")


def listar_productos(datos, solo_activos=False):
    """RF02: Lista los productos activos. Con solo_activos=False incluye los desactivados."""
    productos = datos["productos"]
    if solo_activos:
        productos = [p for p in productos if p["activo"]]
    filas = [
        [p["codigo"], p["nombre"], p["categoria"], f"${p['precio']:.2f}",
         f"{p['stock_minimo']:g}", "SI" if p["activo"] else "NO"]
        for p in productos
    ]
    titulo = ("--- Lista de productos activos ---" if solo_activos
              else "--- Lista de todos los productos ---")
    imprimir_tabla(
        titulo,
        ["Codigo", "Nombre", "Categoria", "Precio", "Stock min", "Activo"],
        filas,
        derecha=(3, 4),
    )


def buscar_producto(datos, texto):
    """RF02: Busca productos por codigo exacto o parte del nombre (activos)."""
    texto = texto.strip().upper()
    resultados = [p for p in datos["productos"] if p["activo"]
                  and (texto in p["codigo"].upper() or texto in p["nombre"].upper())]
    if not resultados:
        print(f"\nNo se encontraron productos que coincidan con {texto!r}.")
        return
    filas = [
        [p["codigo"], p["nombre"], p["categoria"], f"${p['precio']:.2f}",
         p["unidad"], f"{p['stock_minimo']:g}"]
        for p in resultados
    ]
    imprimir_tabla(
        f"--- Resultados de busqueda para {texto!r} ---",
        ["Codigo", "Nombre", "Categoria", "Precio", "Unidad", "Stock min"],
        filas,
        derecha=(3, 5),
    )


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
    costo_texto = input(f"Costo unitario [{producto.get('costo_unitario', producto['precio']):g}]: ").strip()
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
    if costo_texto:
        try:
            costo_unitario = float(costo_texto)
            if costo_unitario <= 0:
                print("Error: el costo unitario debe ser mayor que 0. No se cambio.")
            else:
                producto["costo_unitario"] = costo_unitario
        except ValueError:
            print(f"Error: {costo_texto!r} no es un costo valido. No se cambio.")
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
        print("2. Listar productos activos")
        print("3. Buscar producto")
        print("4. Actualizar producto")
        print("5. Desactivar producto")
        print("6. Reactivar producto")
        print("7. Listar todos los productos")
        print("0. Volver")
        opcion = leer_opcion("Seleccione una opcion: ", {"0", "1", "2", "3", "4", "5", "6", "7"})
        if opcion == "1":
            registrar_producto(datos)
        elif opcion == "2":
            listar_productos(datos, solo_activos=True)
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
        elif opcion == "7":
            listar_productos(datos)
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

    fecha_siembra = leer_fecha_siembra("Fecha de siembra (DD-MM-AAAA): ")
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
    filas = [
        [l["id_lote"], l["producto_codigo"], l["fecha_siembra"],
         f"{l['area_m2']:g}", f"{l['cantidad_producida']:g}", l["estado"]]
        for l in datos["lotes"]
    ]
    imprimir_tabla(
        "--- Lista de lotes ---",
        ["Lote", "Producto", "Siembra", "Area m2", "Producido", "Estado"],
        filas,
        derecha=(3, 4),
    )


def cosechar_lote(datos):
    """RF07: Cosecha un lote, registra la cantidad producida y genera una entrada automatica.

    Regla 5: un lote solo puede cosecharse una vez.
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
    """RF06: Cambia el estado de un lote entre EN_PRODUCCION y CANCELADO.

    COSECHADO es un estado final: solo se alcanza mediante la cosecha (RF07).
    """
    print("\n--- Cambiar estado de lote ---")
    while True:
        id_lote = leer_texto("Id del lote: ", obligatorio=True).upper()
        lote = obtener_lote(datos, id_lote)
        if not lote:
            print(f"Error: no existe el lote {id_lote}. Intente nuevamente.")
        elif lote["estado"] == "COSECHADO":
            print("Error: el lote ya fue cosechado (estado final) y no puede cambiarse. "
                  "Intente con otro lote.")
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
    codigo = leer_texto("Codigo del producto: ", obligatorio=True).upper()
    if not validar_producto_para_operacion(datos, codigo):
        return
    cantidad = leer_numero("Cantidad: ", tipo=float, minimo=0.0001)
    motivo = leer_texto("Motivo (obligatorio): ", obligatorio=True)
    registrar_movimiento(datos, codigo, "ENTRADA", cantidad, motivo)
    print(f"Entrada registrada. Stock actual de {codigo}: {calcular_stock(datos, codigo):g}")


def salida_manual(datos):
    """RF09: Salida manual solo si existe stock suficiente (regla 4)."""
    print("\n--- Salida manual de inventario ---")
    codigo = leer_texto("Codigo del producto: ", obligatorio=True).upper()
    if not validar_producto_para_operacion(datos, codigo):
        return
    stock = calcular_stock(datos, codigo)
    print(f"Stock disponible de {codigo}: {stock:g}")
    cantidad = leer_numero("Cantidad a sacar: ", tipo=float, minimo=0.0001)
    if cantidad > stock:
        print(f"Error: stock insuficiente. Disponible: {stock:g}, solicitado: {cantidad:g}. "
              "La salida no se registro.")
        return
    motivo = leer_texto("Motivo: es obligatorio: ", obligatorio=True)
    registrar_movimiento(datos, codigo, "SALIDA", cantidad, motivo)
    print(f"Salida registrada. Stock actual de {codigo}: {calcular_stock(datos, codigo):g}")


def listar_movimientos(datos):
    """Lista los movimientos de inventario, opcionalmente filtrados por producto."""
    codigo = leer_texto("Codigo del producto (vacio para todos): ").upper()
    movimientos = datos["movimientos"]
    if codigo:
        movimientos = [m for m in movimientos if m["producto_codigo"] == codigo]
    filas = [
        [m["id"], m["producto_codigo"], m["tipo"], f"{m['cantidad']:g}",
         m["motivo"], m["fecha"]]
        for m in movimientos
    ]
    imprimir_tabla(
        "--- Movimientos de inventario ---",
        ["Id", "Producto", "Tipo", "Cantidad", "Motivo", "Fecha"],
        filas,
        derecha=(3,),
    )


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
            codigo = leer_texto("Codigo del producto: ", obligatorio=True).upper()
            if obtener_producto(datos, codigo):
                print(f"Stock de {codigo}: {calcular_stock(datos, codigo):g}")
            else:
                print(f"Error: no existe el producto {codigo}.")
        else:
            break


# Ventas (RF10 - RF11)


def registrar_venta(datos):
    """RF10 y RF11: Registra una venta con uno o varios productos.

    Primero se arma la lista de items y luego se valida el stock de TODOS
    (regla 4 y 6). Solo si todo esta correcto se descuenta el inventario y se
    guarda la venta: todo o nada.
    """
    print("\n--- Registrar venta ---")
    print("Puede agregar varios productos. Deje el codigo vacio para terminar.")
    items = []

    while True:
        codigo = leer_texto("Codigo del producto (vacio para terminar): ").upper()
        if not codigo:
            break
        producto = validar_producto_para_operacion(datos, codigo)
        if not producto:
            continue
        cantidad = leer_numero("Cantidad: ", tipo=int, minimo=1)
        items.append({
            "codigo": codigo,
            "cantidad": cantidad,
            "precio_unitario": producto["precio"],
        })
        print(f"Item agregado: {producto['nombre']} x {cantidad} @ ${producto['precio']:.0f}")

    if not items:
        print("La venta debe contener al menos un item valido. Operacion cancelada.")
        return False

    # Verificar stock de TODOS los items antes de registrar cualquier cosa
    necesidades = {}
    for item in items:
        necesidades[item["codigo"]] = necesidades.get(item["codigo"], 0) + item["cantidad"]
    for codigo, cantidad in necesidades.items():
        stock = calcular_stock(datos, codigo)
        if cantidad > stock:
            print(f"Error: stock insuficiente de {codigo}. Disponible: {stock:g}, solicitado: {cantidad:g}.")
            print("La venta NO se registro y el inventario no se modifico.")
            return False

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

    # Descontar inventario: una salida por item, despues de validar todo
    for item in items:
        registrar_movimiento(
            datos,
            item["codigo"],
            "SALIDA",
            item["cantidad"],
            f"Venta {venta['id']}",
        )
    guardar_datos(datos)
    print(f"\nVenta {venta['id']} registrada. Total: ${total:.0f}")
    for item, sub in zip(items, subtotales):
        print(f"  - {item['codigo']} x {item['cantidad']:g} @ "
              f"${item['precio_unitario']:.0f} = ${sub:.0f}")
    return True


def consultar_ventas(datos):
    """Muestra las ventas registradas, opcionalmente filtradas por rango de fechas."""
    ventas = datos["ventas"]
    if not ventas:
        print("\nNo hay ventas registradas.")
        return

    print("\n--- Consultar ventas ---")
    desde = leer_texto("Fecha desde (AAAA-MM-DD, vacio para todas): ")
    hasta = leer_texto("Fecha hasta (AAAA-MM-DD, vacio para todas): ")
    if desde:
        ventas = [v for v in ventas if v["fecha"][:10] >= desde]
    if hasta:
        ventas = [v for v in ventas if v["fecha"][:10] <= hasta]
    if not ventas:
        print("No hay ventas en ese rango de fechas.")
        return

    filas = []
    for v in ventas:
        detalle = ", ".join(
            f"{item['codigo']} x {item['cantidad']:g} @ ${item['precio_unitario']:.0f}"
            for item in v["items"]
        )
        filas.append([v["id"], v["fecha"], detalle, f"${v['total']:.0f}"])
    filas.append(["TOTAL", "", "", f"${sum(v['total'] for v in ventas):.0f}"])
    imprimir_tabla(
        f"--- Ventas encontradas: {len(ventas)} ---",
        ["Id", "Fecha", "Productos", "Total"],
        filas,
        derecha=(3,),
    )


def devolver_venta(datos):
    """Devuelve una venta completa y repone sus productos en inventario."""
    print("\n--- Devolver venta ---")
    id_venta = leer_texto("Id de la venta (ej. V0001): ", obligatorio=True).upper()
    venta = next((item for item in datos["ventas"] if item["id"] == id_venta), None)
    if not venta:
        print(f"Error: no existe la venta {id_venta}.")
        return False
    if venta.get("devuelta", False):
        print(f"Error: la venta {id_venta} ya fue devuelta.")
        return False

    confirmar = leer_texto(f"Confirma devolver {id_venta}? [s/N]: ").lower()
    if confirmar != "s":
        print("Operacion cancelada.")
        return False

    for item in venta["items"]:
        registrar_movimiento(
            datos,
            item["codigo"],
            "ENTRADA",
            item["cantidad"],
            f"Devolucion {id_venta}",
        )
    venta["devuelta"] = True
    guardar_datos(datos)
    print(f"Venta {id_venta} devuelta. El inventario fue repuesto.")
    return True


# Alertas (RF12)


def mostrar_alertas(datos):
    """RF12: Muestra los productos activos cuyo stock es menor o igual al stock minimo.

    Regla 3: el stock no se guarda, se calcula a partir de los movimientos.
    Los productos desactivados no se alertan porque ya no pueden venderse ni moverse.
    """
    print("\n--- Alertas de stock ---")
    alertas = []
    for p in datos["productos"]:
        if not p["activo"]:
            continue
        stock = calcular_stock(datos, p["codigo"])
        if stock <= p["stock_minimo"]:
            alertas.append([p["codigo"], p["nombre"], f"{stock:g}",
                            f"{p['stock_minimo']:g}", f"{p['stock_minimo'] - stock:g}"])

    if not alertas:
        print("\nNo hay alertas. Todo el stock activo esta por encima del minimo.")
        return

    imprimir_tabla(
        f"--- ALERTAS DE STOCK ({len(alertas)} productos en nivel critico) ---",
        ["Codigo", "Nombre", "Stock actual", "Stock minimo", "Faltante"],
        alertas,
        derecha=(2, 3, 4),
    )
    print("Sugerencia: registre una entrada de inventario para estos productos.")


# Reportes (RF13 - RF15) y retos de ampliacion


def reporte_inventario(datos):
    """RF13: Existencias y valor del inventario a precio de venta."""
    filas = []
    valor_total = 0.0
    for p in datos["productos"]:
        stock = calcular_stock(datos, p["codigo"])
        valor = round(stock * p["precio"], 2)
        valor_total += valor
        filas.append([
            p["codigo"], p["nombre"], f"{stock:g}", f"${p['precio']:.2f}",
            f"${valor:.2f}", "SI" if p["activo"] else "NO",
        ])
    imprimir_tabla(
        "--- Reporte de inventario (a precio de venta) ---",
        ["Codigo", "Nombre", "Stock", "Precio", "Valor", "Activo"],
        filas,
        derecha=(2, 3, 4),
    )
    if filas:
        print(f"Valor total del inventario a precio de venta: ${valor_total:.2f}")


def reporte_ventas(datos):
    """RF14: Numero de ventas, unidades vendidas e ingresos acumulados."""
    ventas = datos["ventas"]
    if not ventas:
        print("\nNo hay ventas registradas.")
        return
    numero_ventas = len(ventas)
    unidades = sum(item["cantidad"] for v in ventas for item in v["items"])
    ingresos = sum(v["total"] for v in ventas)
    print("\n--- Reporte de ventas ---")
    print(f"Numero de ventas: {numero_ventas}")
    print(f"Unidades vendidas: {unidades:g}")
    print(f"Ingresos acumulados: ${ingresos:.2f}")


def reporte_utilidad(datos):
    """Calcula utilidad estimada usando precio y costo unitario actuales."""
    utilidad_total = 0.0
    filas = []
    for venta in datos["ventas"]:
        if venta.get("devuelta", False):
            continue
        utilidad_venta = 0.0
        for item in venta["items"]:
            producto = obtener_producto(datos, item["codigo"])
            costo = producto.get("costo_unitario", producto["precio"] * 0.7) if producto else 0
            utilidad_venta += item["cantidad"] * (item["precio_unitario"] - costo)
        utilidad_venta = round(utilidad_venta, 2)
        utilidad_total += utilidad_venta
        filas.append([venta["id"], f"${venta['total']:.0f}", f"${utilidad_venta:.0f}"])
    if not filas:
        print("\nNo hay ventas validas para calcular utilidad.")
        return
    imprimir_tabla(
        "--- Reporte de utilidad estimada ---",
        ["Venta", "Ingresos", "Utilidad estimada"],
        filas,
        derecha=(1, 2),
    )
    print(f"Utilidad estimada acumulada: ${utilidad_total:.0f}")


def ranking_productos(datos):
    """RF15: Ranking de los 3 productos con mayor cantidad vendida."""
    vendidos = {}
    for v in datos["ventas"]:
        for item in v["items"]:
            vendidos[item["codigo"]] = vendidos.get(item["codigo"], 0) + item["cantidad"]
    if not vendidos:
        print("\nNo hay datos de ventas para calcular el ranking.")
        return
    top = sorted(vendidos.items(), key=lambda x: x[1], reverse=True)[:3]
    filas = []
    for puesto, (codigo, cantidad) in enumerate(top, start=1):
        producto = obtener_producto(datos, codigo)
        nombre = producto["nombre"] if producto else "(producto no encontrado)"
        filas.append([str(puesto), codigo, nombre, f"{cantidad:g}"])
    imprimir_tabla(
        "--- Ranking de los 3 productos con mayor cantidad vendida ---",
        ["Puesto", "Codigo", "Nombre", "Unidades vendidas"],
        filas,
        derecha=(3,),
    )


def exportar_inventario_csv(datos):
    """Reto de ampliacion: exporta el inventario a CSV con la biblioteca estandar csv."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    ruta_csv = DATA_DIR / "inventario.csv"
    try:
        with open(ruta_csv, "w", encoding="utf-8", newline="") as f:
            escritor = csv.writer(f)
            escritor.writerow(["codigo", "nombre", "stock", "precio", "valor", "activo"])
            for p in datos["productos"]:
                stock = calcular_stock(datos, p["codigo"])
                escritor.writerow([
                    p["codigo"], p["nombre"], stock, p["precio"],
                    round(stock * p["precio"], 2), p["activo"],
                ])
    except OSError as error:
        print(f"Error: no se pudo escribir el archivo CSV ({error}).")
        return
    print(f"Reporte de inventario exportado a {ruta_csv}")


def menu_reportes(datos):
    """Menu secundario de alertas y reportes."""
    while True:
        print("\n=== REPORTES ===")
        print("1. Alertas de stock")
        print("2. Reporte de inventario")
        print("3. Reporte de ventas")
        print("4. Ranking de los 3 productos mas vendidos")
        print("5. Exportar inventario a CSV")
        print("6. Reporte de utilidad estimada")
        print("0. Volver")
        opcion = leer_opcion("Seleccione una opcion: ", {"0", "1", "2", "3", "4", "5", "6"})
        if opcion == "1":
            mostrar_alertas(datos)
        elif opcion == "2":
            reporte_inventario(datos)
        elif opcion == "3":
            reporte_ventas(datos)
        elif opcion == "4":
            ranking_productos(datos)
        elif opcion == "5":
            exportar_inventario_csv(datos)
        elif opcion == "6":
            reporte_utilidad(datos)
        else:
            break


if __name__ == "__main__":
    main()
