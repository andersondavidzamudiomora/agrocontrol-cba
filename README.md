# AgroControl CBA

Sistema monolitico para gestion de produccion, inventario y ventas de una unidad
productiva asociada al Centro de Biotecnologia Agropecuaria (CBA).

Aplicacion de consola escrita en Python que centraliza productos, lotes
productivos, movimientos de inventario y ventas, con persistencia local en
archivos JSON. Solo utiliza la biblioteca estandar de Python (`json`, `os`,
`datetime`, `pathlib`); no usa bases de datos ni frameworks web.

## Descripcion

La unidad productiva registraba productos, lotes, existencias y ventas en hojas
independientes, lo que generaba inconsistencias (ventas superiores al
inventario, lotes sin trazabilidad, sin alertas de stock bajo ni reportes).
AgroControl CBA resuelve ese problema en un unico proyecto monolitico con un
unico punto de entrada (`main.py`).

## Requisitos

- Python 3.10 o superior
- Git (para el flujo de versionado)

## Instrucciones de ejecucion

```bash
# Desde la carpeta del proyecto
python main.py
```

Al iniciar, la aplicacion carga automaticamente los archivos JSON de la carpeta
`data/`. Si un archivo no existe, inicia con una coleccion vacia y lo crea al
primer guardado.

## Estructura del proyecto

```
agrocontrol_cba/
 main.py               Toda la logica de la aplicacion
 data/
  productos.json       Productos comercializables
  lotes.json           Lotes productivos
  movimientos.json     Entradas y salidas de inventario
  ventas.json          Ventas registradas
 README.md
 .gitignore
```

## Menu principal

```
==================== AGROCONTROL  CBA  ====================
1. Gestion de productos
2. Gestion de lotes productivos
3. Movimientos de inventario
4. Registrar venta
5. Consultar ventas
6. Alertas de stock
7. Reportes
8. Guardar datos
0. Salir
```

## Reglas de negocio principales

1. Los codigos de producto y de lote son unicos y se almacenan en mayuscula.
2. Un producto desactivado conserva su historial, pero no puede usarse en
   nuevos lotes ni ventas.
3. El stock actual no se guarda como dato aislado: se calcula a partir de los
   movimientos de inventario (entradas menos salidas).
4. Una salida de inventario y una venta nunca pueden dejar el stock en valores
   negativos.
5. Un lote solo puede cosecharse una vez. Al cosecharse cambia su estado y
   genera una entrada automatica de inventario.
6. Una venta debe contener al menos un item valido.
7. El precio de la venta se toma del precio vigente del producto en el momento
   del registro y se guarda dentro del detalle de la venta.
8. Las operaciones que modifican datos guardan inmediatamente la informacion
   en JSON.
9. El sistema genera identificadores secuenciales para movimientos y ventas
   (M0001, V0001, ...).

## Casos de prueba minimos

| Codigo | Caso | Resultado esperado |
|--------|------|--------------------|
| PF001  | Producto duplicado | Se rechaza el segundo registro |
| PF002  | Precio invalido (0 o texto) | Se solicita un valor valido |
| PF003  | Cosechar lote inexistente | Informa que no existe |
| PF004  | Doble cosecha del mismo lote | Se rechaza la segunda |
| PF005  | Salida mayor al stock | Se impide la operacion |
| PF006  | Venta valida | Crea venta y reduce stock |
| PF007  | Venta con varios productos | Calcula subtotales y total |
| PF008  | Persistencia | Los datos se conservan al reiniciar |
| PF009  | Stock menor o igual al minimo | Aparece en alertas |

## Autores

- Ander

---
Centro de Biotecnologia Agropecuaria - Mosquera, Cundinamarca - Material de formacion SENA.