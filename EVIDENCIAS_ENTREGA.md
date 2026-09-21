# Evidencias de entrega - AgroControl CBA

## Estado funcional

- `main.py`: funcional y validado con `python -m py_compile main.py`.
- `data/`: contiene `productos.json`, `lotes.json`, `movimientos.json` y `ventas.json`.
- `README.md`: contiene descripcion, ejecucion, estructura, reglas, respaldos, roles y autor.
- `.gitignore`: configurado para entornos, archivos compilados, respaldos, CSV y temporales.
- Respuestas de reflexion: disponibles en `RESPUESTAS_REFLEXION.md`.

## Casos de prueba minimos

Los casos PF001-PF009 fueron ejecutados con resultado PASS:

| Caso | Resultado |
|---|---|
| PF001 Producto duplicado | PASS |
| PF002 Precio invalido | PASS |
| PF003 Lote inexistente | PASS |
| PF004 Doble cosecha | PASS |
| PF005 Salida excesiva | PASS |
| PF006 Venta valida | PASS |
| PF007 Venta multiple | PASS |
| PF008 Persistencia | PASS |
| PF009 Alerta de stock | PASS |

Para repetirlos, ejecutar el programa con `py -3 .\\main.py` y guardar una captura
por cada caso mostrando la entrada y el resultado esperado.

## Retos de ampliacion

- Consulta de ventas por rango de fechas: menu `5. Consultar ventas`.
- Utilidad estimada: menu `7. Reportes`, opcion `6`.
- Devolucion de ventas: menu `9. Devolver venta`.
- Exportacion CSV: menu `7. Reportes`, opcion `5`.
- Copias de seguridad: se generan en `data/backups/` antes de guardar.
- Roles: `operador / operador123` y `admin / admin123`.

Guardar capturas de estas evidencias junto con la entrega:

- Consulta por fecha.
- Reporte de utilidad.
- Devolucion y movimiento inverso.
- Archivo CSV.
- Archivos de `data/backups/`.
- Acceso denegado del operador.
- Acceso permitido del administrador.

## Evidencias Git pendientes

El repositorio local tiene 19 commits y una rama `feature/reporte-rotacion`.
Para completar la entrega aun se necesita:

1. Publicar el repositorio en GitHub.
2. Crear un Issue relacionado con una mejora real.
3. Crear un Pull Request desde una rama de mejora hacia `main`.
4. Tomar una captura de `git log --oneline --graph --decorate --all`.
5. Registrar el enlace del repositorio, del Issue y del Pull Request.

Comando para la evidencia del historial:

```text
git log --oneline --graph --decorate --all
```
