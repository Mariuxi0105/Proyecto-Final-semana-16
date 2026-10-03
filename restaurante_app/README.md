# Sistema Restaurante

**Autora:** Mariuxi Jessenia Tejada Mayorga
**Trabajo:** Semana 16

## Descripción

Aplicación de escritorio para administrar el menú, ventas y usuarios de un restaurante. Conserva el inicio de sesión, la navegación, productos, ventas, reportes y almacenamiento JSON desarrollados previamente. La evolución de esta semana se centra en la gestión de usuarios mediante eventos Tkinter.

La aplicación separa modelos, servicios, persistencia, interfaz y punto de entrada. La interfaz captura las acciones y presenta resultados; `RestauranteServicio` aplica validaciones y reglas; `ArchivoServicio` lee y guarda los archivos JSON.

## Estructura

```text
restaurante_app/
├── main.py
├── README.md
├── requirements.txt
├── assets/                  # Logotipo e iconos de navegación
├── datos/
│   ├── productos.json
│   ├── usuarios.json
│   └── ventas.json
├── modelos/
│   ├── producto.py
│   ├── usuario.py
│   └── venta.py
├── servicios/
│   ├── archivo_servicio.py
│   └── restaurante_servicio.py
├── tests/
│   └── test_gestion_usuarios.py
└── ui/
    ├── estilos.py
    ├── login_view.py
    ├── main_view.py
    └── recursos.py
```

## Roles y acceso

- **Administrador:** inicia sesión y gestiona cuentas de Empleado y Cliente. Puede consultar, registrar, actualizar y eliminar cuentas desde la vista administrativa.
- **Empleado (cajero/mesero):** inicia sesión y puede gestionar únicamente cuentas de Cliente; el selector de rol queda limitado a Cliente.
- **Cliente:** es una cuenta de cliente utilizada en el registro de ventas. No puede iniciar sesión ni abrir las vistas administrativas.

Las reglas de registro, actualización, eliminación y acceso se verifican en `RestauranteServicio`, además de las restricciones presentadas en la interfaz. La pantalla de inicio de sesión no muestra credenciales. Los datos de demostración están en `datos/usuarios.json`; allí se pueden consultar para las pruebas locales. Las contraseñas de esta aplicación educativa se almacenan como texto plano y no deben utilizarse en un sistema real.

## Gestión de usuarios y eventos

En la vista **Usuarios** se muestra un formulario y un `Treeview`. Para el administrador, el título indica **Administración de usuarios**; el empleado ve **Registro de clientes**. La tabla presenta identificador, nombre, usuario, contacto y rol; no contiene contraseñas. Al seleccionar una cuenta de personal, el administrador puede consultar su clave en el campo de contraseña del formulario. En la vista del empleado ese campo permanece enmascarado. Las filas guardan solo el identificador y el callback de selección recupera el objeto mediante `RestauranteServicio.buscar_usuario`.

Eventos requeridos:

- `TreeviewSelect` → `bind()` → consulta por ID al servicio → carga el formulario.
- `ComboboxSelected` → `bind()` → muestra el rol elegido en el estado de la vista.
- `Return` → `bind()` → reutiliza el callback de registro.
- `Escape` → `bind()` → limpia el formulario y quita la selección.
- Botones Registrar, Actualizar, Eliminar y Limpiar → `command=`.

Flujo general: interacción → evento/botón → callback de interfaz → servicio → persistencia JSON → actualización de tabla y respuesta visual. Los formularios, tablas y panel principal admiten scroll con la barra vertical y la rueda del mouse.

## Productos

La sección **Productos** conserva el registro, consulta por identificador, actualización y eliminación con confirmación. Las validaciones y persistencia son responsabilidad de `RestauranteServicio`; después de cada operación satisfactoria la interfaz vuelve a cargar la tabla.

## Ventas

La sección **Ventas** permite registrar ventas asociando un cliente y un producto. El historial se conserva en `datos/ventas.json`. El botón **Generar reporte PDF** solicita una ruta y delega la creación a `RestauranteServicio`.

## Archivos de datos

- `datos/productos.json`: catálogo y stock.
- `datos/usuarios.json`: cuentas de personal y clientes.
- `datos/ventas.json`: identificadores del cliente y producto, y fecha/hora ISO.

## Instalación y ejecución

El proyecto declara ReportLab (generación de PDF) y Pillow (carga de imágenes) en `requirements.txt`. Desde la carpeta `restaurante_app`, instala todas las dependencias con:

```bash
python -m pip install -r requirements.txt
```

Si solo necesitas instalar o actualizar ReportLab:

```bash
python -m pip install reportlab
```

Ejecuta la aplicación:

```bash
python main.py
```

La ventana se centra y ajusta a la resolución disponible. En secciones con contenido más alto que la ventana, utiliza la barra de desplazamiento o la rueda del mouse. Los JSON y recursos visuales se resuelven relativos a los módulos mediante `Path(__file__).resolve()`, sin depender de la carpeta actual. El PDF se guarda en la ruta elegida por la persona usuaria.

## Comprobación funcional de Semana 16

1. Ejecuta `python main.py`; confirma que aparece la pantalla de acceso sin credenciales prellenadas ni credenciales de demostración visibles.
2. Inicia sesión con el administrador de demostración indicado en `datos/usuarios.json`. Abre **Usuarios** y comprueba que puede gestionar cuentas de Empleado y Cliente.
3. Selecciona una fila y verifica que `TreeviewSelect` cargue el usuario y el servicio recupere los datos por su identificador.
4. Registra una cuenta de Empleado y otra de Cliente. Comprueba que el Treeview se actualice y que la persistencia se refleje en `datos/usuarios.json`.
5. Actualiza una cuenta, elimina otra y confirma que la eliminación requiere confirmación. Verifica que no se permita eliminar ni modificar la cuenta actualmente autenticada.
6. Usa `Enter` para registrar desde el formulario; usa `Escape` para borrar campos y cancelar la selección. Cambia el rol y verifica la respuesta visual de `ComboboxSelected`.
7. Cierra sesión e inicia sesión con un empleado. Comprueba que su vista muestre **Registro de clientes**, que solo aparezcan registros Cliente y que no permita gestionar cuentas de Empleado o Administrador.
8. Intenta iniciar sesión con un cliente; el acceso debe ser rechazado.
9. Comprueba Productos: registra, consulta, actualiza y elimina un producto con confirmación.
10. Registra una venta para un cliente y un producto; genera un reporte PDF.
11. Revisa el scroll mediante la barra y la rueda del mouse, y comprueba la vista en una ventana reducida y maximizada.
12. Cierra y vuelve a ejecutar la aplicación; confirma que los productos, usuarios y ventas se recuperan desde JSON.

## Verificación técnica

Compilación de los módulos:

```bash
python -m compileall -q main.py modelos servicios ui
```

Pruebas de las reglas del servicio:

```bash
python -m unittest discover -s tests -v
```
