# Preguntas de reflexion - AgroControl CBA

## 1. ¿Por qué AgroControl CBA sigue siendo una aplicación monolítica aunque tenga varios módulos lógicos?

Porque la arquitectura monolítica no se refiere a la cantidad de funcionalidades, sino a cómo se ejecuta y despliega la aplicación. Todo el código vive en un único proyecto con un único punto de entrada (`main.py`): los "módulos lógicos" (productos, lotes, inventario, ventas, alertas y reportes) son secciones de funciones dentro del mismo archivo que comparten un mismo diccionario de datos en memoria y un mismo mecanismo de persistencia JSON. No hay servicios separados, procesos independientes, bases de datos aisladas ni comunicación entre aplicaciones: una sola ejecución de un solo programa realiza todas las operaciones.

## 2. ¿Qué ventaja ofrece calcular el stock a partir de movimientos y no modificar directamente un campo stock?

Trazabilidad, integridad y auditabilidad. Como el stock se calcula en cada momento como entradas menos salidas, siempre refleja exactamente la realidad de los movimientos registrados y es imposible que se desincronice: si se guardara un campo `stock`, cualquier operación que olvidara actualizarlo dejaría un dato obsoleto e inconsistente. Además, a partir de los movimientos se puede reconstruir el historial (qué entró, cuándo y por qué), auditar errores y responder preguntas como "¿cuánto se cosechó del lote L001?" sin información adicional.

## 3. ¿Qué riesgo existe si una venta descuenta inventario antes de verificar todos sus productos?

El riesgo es dejar el sistema en un estado inconsistente a medias. Si se descuenta el primer ítem y luego se descubre que el segundo no tiene stock suficiente, la venta se rechaza pero el inventario ya quedó modificado: habría salidas sin venta registrada, datos corruptos y un usuario confundido. Por eso AgroControl verifica primero el stock de TODOS los ítems y solo si la venta completa es válida descuenta inventario y la guarda; la operación es atómica (todo o nada).

## 4. ¿Qué diferencia existe entre desactivar un producto y eliminarlo físicamente?

Desactivar es un cambio de estado (`activo: false`): el producto deja de poder usarse en nuevas operaciones (lotes, ventas, movimientos), pero su registro y todo su historial se conservan, de modo que los reportes históricos y la trazabilidad siguen siendo válidos. Eliminarlo físicamente (borrarlo del JSON) rompería las referencias: ventas, lotes y movimientos apuntarían a un código inexistente y se perdería información contable e histórica irrecuperable. En sistemas reales lo que se borra es información, no se "oculta": los registros se desactivan.

## 5. ¿Qué problema resuelve la persistencia JSON frente al ejercicio anterior?

En el ejercicio anterior (AgroCBA) los datos vivían únicamente en memoria y se perdían al cerrar el programa. Con persistencia JSON los datos sobreviven entre ejecuciones: la aplicación carga los archivos al iniciar (RF17) y los guarda tras cada operación (RF16). Además, JSON es legible por humanos, fácil de versionar con Git, no requiere instalar nada (biblioteca estándar) y es sencillo de inspeccionar o corregir a mano.

## 6. ¿Qué información debería incluir un buen mensaje de commit?

Debe ser corto pero explicar el *qué* y el *porqué* del cambio. Conviene incluir: un prefijo de tipo (`feat`, `fix`, `docs`, `refactor`, `chore`, `test`), un verbo en imperativo o presente, el alcance o componente afectado, y cuando aplique, la referencia al Issue (`#1`). Ejemplo: `feat: agrega reporte de rotacion de productos - cierra el issue #1`. Un buen mensaje permite reconstruir la historia del proyecto sin necesidad de abrir el código, y mensajes vagos como "cambios" o "actualización" no sirven.

## 7. ¿Cuál es la finalidad de trabajar una mejora en una rama diferente a main?

Aislar el trabajo nuevo o experimental del código estable. `main` permanece siempre en un estado funcional y entregable, mientras la mejora se desarrolla, prueba y corrige en su rama sin arriesgar lo que ya funciona. Solo cuando está lista y revisada se integra. Además permite que varias personas trabajen en paralelo sin pisarse y deja un registro claro de qué se cambió, en qué orden y por qué.

## 8. ¿Qué aporta un Pull Request incluso cuando el proyecto es académico?

Aporta el flujo profesional completo: obliga a explicar qué se cambió y cómo se probó, habilita la revisión por otra persona (instructor o compañeros) antes de integrar, y deja evidencia formal del proceso colaborativo que se usa en la industria. Aunque el código sea de estudio, el PR desarrolla hábitos de calidad, comunicación y trabajo en equipo, y demuestra dominio de Git/GitHub en el portafolio.

## 9. ¿Qué partes del sistema serían candidatas a convertirse en módulos separados en una evolución futura?

Las secciones que hoy son bloques de funciones con responsabilidades claras: persistencia (carga/guardado JSON), gestión de productos, gestión de lotes, inventario (movimientos y stock), ventas y reportes. Una evolución natural sería convertirlas en paquetes (`persistencia/`, `productos/`, `ventas/`...) o, si la aplicación creciera mucho, en servicios independientes. La separación ya existe a nivel lógico; el paso siguiente es físico.

## 10. ¿Qué limitaciones tendría JSON si el sistema creciera y fuera usado simultáneamente por varias personas?

JSON no ofrece concurrencia ni transacciones: si dos usuarios escriben a la vez, el último guardado puede sobrescribir al primero (pérdida de datos), y un lector puede ver el archivo a medio escribir. Tampoco hay bloqueos, permisos por usuario, consultas, índices ni relaciones. Para uso simultáneo real se necesitaría una base de datos (SQLite para un solo servidor local, o PostgreSQL/MySQL en red) con transacciones ACID y control de concurrencia.