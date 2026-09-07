# Preguntas de reflexion - AgroControl CBA

## 1. ¿Por qué AgroControl CBA sigue siendo una aplicación monolítica aunque tenga varios módulos lógicos?

Porque "módulos lógicos" no es lo mismo que "aplicaciones separadas". En mi proyecto todo vive en un solo archivo `main.py`: los módulos de productos, lotes, inventario, ventas y reportes son bloques de funciones del mismo programa que comparten la misma información en memoria y el mismo archivo de persistencia. Aunque organicé el código por temas para que sea legible, a la hora de ejecutarlo sigue siendo una única aplicación con un único punto de entrada (`main()`), y eso es justamente lo que la hace monolítica.

## 2. ¿Qué ventaja ofrece calcular el stock a partir de movimientos y no modificar directamente un campo stock?

En mi aplicación no existe un campo `stock` guardado en ninguna parte: la función `calcular_stock` suma las entradas y resta las salidas cada vez que se necesita el dato. La gran ventaja es que el número siempre es correcto, porque ninguna operación puede "olvidarse" de actualizarlo. Además me da trazabilidad total: si alguien pregunta de dónde salió una cantidad, puedo revisar los movimientos y ver exactamente qué entró, qué salió, cuándo y con qué motivo.

## 3. ¿Qué riesgo existe si una venta descuenta inventario antes de verificar todos sus productos?

Cuando implementé `registrar_venta` entendí el problema: si descuento el primer producto y después me doy cuenta de que el segundo no tiene stock suficiente, la venta se rechaza pero el inventario ya quedó modificado, dejando salidas sin venta registrada. Eso sería un desastre para la consistencia de los datos. Por eso mi función primero revisa el stock de TODOS los productos de la venta y solo si todos pasan la validación descuenta inventario y guarda la venta: todo o nada.

## 4. ¿Qué diferencia existe entre desactivar un producto y eliminarlo físicamente?

Al principio pensaba que desactivar era casi lo mismo que borrar, pero no. Desactivar pone el campo `activo` en false: el producto ya no puede usarse en lotes, ventas ni movimientos nuevos, pero su registro y todo su historial quedan intactos, así los reportes no se rompen. Si lo eliminara físicamente del JSON, las ventas y movimientos viejos quedarían apuntando a un código que ya no existe y se perdería información valiosa. Por eso en mi sistema las opciones que afectan datos se validan primero y el historial siempre se conserva.

## 5. ¿Qué problema resuelve la persistencia JSON frente al ejercicio anterior?

En el ejercicio anterior, cuando cerraba el programa se perdía todo lo que había registrado, porque los datos solo existían en memoria. Con la persistencia JSON eso cambió por completo: la aplicación carga los archivos al iniciar y guarda después de cada operación, entonces puedo cerrar, volver a abrir y mis productos, lotes, movimientos y ventas siguen ahí. Además el formato es legible, puedo abrirlo en cualquier editor, y como es texto plano también puedo versionarlo con Git.

## 6. ¿Qué información debería incluir un buen mensaje de commit?

Cuando miro el `git log` de mi proyecto puedo leer la historia completa sin abrir el código: "feat: agrega gestion y validacion de productos", "fix: evita fallos con archivos JSON corruptos", "docs: documenta ejecucion y reglas de negocio". Un buen mensaje debe decir qué se hizo y por qué, con un prefijo de tipo (`feat`, `fix`, `docs`, `refactor`, `chore`) y referencia al Issue cuando aplique. Mensajes como "cambios" o "actualización" no dicen nada y no sirven para reconstruir el proceso.

## 7. ¿Cuál es la finalidad de trabajar una mejora en una rama diferente a main?

La finalidad es no arriesgar lo que ya funciona. Cuando desarrollé el reporte de rotación lo hice en la rama `feature/reporte-rotacion`, mientras `main` quedó siempre en un estado estable y entregable. Así pude probar, equivocarme y corregir sin miedo a romper nada, y la mejora se integra a `main` solo cuando está lista y revisada. También permite que varias personas trabajen en paralelo sin pisarse.

## 8. ¿Qué aporta un Pull Request incluso cuando el proyecto es académico?

El Pull Request me obligó a hacer las cosas como en la vida real: explicar qué cambié, por qué y cómo lo probé, para que otra persona pueda revisarlo antes de integrarlo. Aunque el proyecto es de clase, ese flujo es el mismo que se usa en las empresas y deja evidencia de que sé trabajar de forma ordenada y colaborativa. Además, si el instructor o un compañero revisa el PR, puedo recibir correcciones antes de que el código llegue a `main`.

## 9. ¿Qué partes del sistema serían candidatas a convertirse en módulos separados en una evolución futura?

Si el sistema creciera, yo separaría las partes que hoy ya tienen una responsabilidad clara: la persistencia (carga y guardado de JSON), la gestión de productos, los lotes, el inventario, las ventas y los reportes. Podrían convertirse en paquetes dentro del mismo proyecto (`productos/`, `ventas/`, `persistencia/`...) y, si la aplicación se volviera muy grande, en servicios independientes. La lógica ya está separada por funciones; el siguiente paso sería separarla físicamente.

## 10. ¿Qué limitaciones tendría JSON si el sistema creciera y fuera usado simultáneamente por varias personas?

JSON me funcionó perfecto porque es un programa de consola de un solo usuario, pero tiene límites claros: si dos personas escribieran a la vez, el último guardado sobrescribiría al primero y se perdería información, y no hay forma de bloquear ni controlar eso. Tampoco hay consultas, permisos ni relaciones entre datos. Para uso simultáneo de verdad se necesitaría una base de datos con transacciones y control de concurrencia, como SQLite para algo local o PostgreSQL/MySQL para una red.