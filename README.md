 # AgroControl CBA

Sistema monolitico en Python para administrar productos agricolas, lotes
productivos, inventario y ventas. La aplicacion utiliza archivos JSON como
almacenamiento local y concentra la logica principal en `main.py`.

## Ejecucion

Requisitos: Python 3.10 o superior. No se necesitan dependencias externas.

Desde esta carpeta ejecutar:

```text
python main.py
```

La aplicacion crea la carpeta `data/` y sus archivos JSON si no existen.

## Estructura

```text
agrocontrol_cba/
|-- main.py
|-- README.md
|-- RESPUESTAS_REFLEXION.md
|-- data/
	|-- productos.json
	|-- lotes.json
	|-- movimientos.json
	|-- ventas.json
	|-- backups/
```

## Funcionalidades

- Registrar, listar, buscar, actualizar, desactivar y reactivar productos.
- Registrar lotes, cambiar estados y cosechar lotes.
- Registrar entradas y salidas de inventario.
- Calcular el stock a partir de los movimientos.
- Registrar ventas con uno o varios productos.
- Consultar ventas por rango de fechas.
- Mostrar alertas, existencias, valor del inventario y ranking de ventas.
- Exportar el inventario a CSV.
- Crear copias de seguridad antes de guardar cambios.
- Calcular utilidad estimada con costo unitario por producto.
- Registrar devoluciones y reponer el inventario mediante entradas inversas.
- Autenticar usuarios con roles OPERADOR y ADMINISTRADOR.

## Reglas principales

- Los codigos de productos y lotes son unicos y se guardan en mayuscula.
- Los productos desactivados conservan su historial, pero no se pueden operar.
- El stock se calcula como entradas menos salidas.
- No se permiten salidas ni ventas por encima del stock disponible.
- Un lote solo puede cosecharse una vez.
- Una cosecha genera automaticamente una entrada de inventario.
- Cada venta conserva el precio vigente de cada producto al registrarse.
- Las operaciones modifican inmediatamente los archivos JSON.
- El OPERADOR puede consultar y operar inventario y ventas.
- El ADMINISTRADOR puede gestionar productos, lotes, reportes y devoluciones.

## Usuarios de prueba

| Usuario | Clave | Rol |
|---|---|---|
| operador | operador123 | OPERADOR |
| admin | admin123 | ADMINISTRADOR |

El reporte de utilidad se encuentra en `7. Reportes`, opcion `6`.
Las devoluciones se realizan desde la opcion `9. Devolver venta` del menu
principal y solo pueden hacerse una vez por venta.

## Datos y respaldos

Los archivos JSON se encuentran en `data/`. Antes de cada guardado, los
archivos existentes se copian en `data/backups/` con fecha y hora.

## Autor

Ander - proyecto academico AgroControl CBA.
