import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path
from typing import Callable

from modelos.producto import Producto
from modelos.usuario import Usuario
from servicios.restaurante_servicio import RestauranteServicio
from ui.recursos import cargar_logo


RUTA_ASSETS = Path(__file__).resolve().parent.parent / "assets"


class MainView(ttk.Frame):
    """Panel principal de gestión del restaurante."""

    def __init__(
        self,
        master: tk.Misc,
        servicio: RestauranteServicio,
        usuario: Usuario,
        cerrar_sesion: Callable[[], None],
    ) -> None:
        super().__init__(master, padding=0, style="App.TFrame")
        self.servicio = servicio
        self.usuario = usuario
        self.cerrar_sesion = cerrar_sesion
        self._tag_scroll = f"RestauranteScroll_{str(self).replace('.', '_')}"
        self._modo_usuarios = ""
        self.bind_class(self._tag_scroll, "<MouseWheel>", self._desplazar_contenido)
        self.bind_class(self._tag_scroll, "<Button-4>", self._desplazar_contenido)
        self.bind_class(self._tag_scroll, "<Button-5>", self._desplazar_contenido)
        self.bind("<Destroy>", self._liberar_eventos, add="+")
        self._iconos = {
            "logo": cargar_logo(
                master=self,
                dimension_maxima=56,
                foreground="#B6533D",
            ),
            "inicio": tk.BitmapImage(
                master=self,
                file=str(RUTA_ASSETS / "icono_inicio.xbm"),
                foreground="#F3F6F2",
            ),
            "productos": tk.BitmapImage(
                master=self,
                file=str(RUTA_ASSETS / "icono_productos.xbm"),
                foreground="#F3F6F2",
            ),
            "usuarios": tk.BitmapImage(
                master=self,
                file=str(RUTA_ASSETS / "icono_usuarios.xbm"),
                foreground="#F3F6F2",
            ),
            "ventas": tk.BitmapImage(
                master=self,
                file=str(RUTA_ASSETS / "icono_ventas.xbm"),
                foreground="#F3F6F2",
            ),
        }
        self.columnconfigure(0, weight=0, minsize=190)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=0)
        self.rowconfigure(1, weight=1)
        self._crear_variables_producto()
        self._crear_variables_usuario()
        self.estado_var = tk.StringVar(master=self)

        encabezado = ttk.Frame(self, padding=(28, 15), style="Header.TFrame")
        encabezado.grid(row=0, column=0, columnspan=3, sticky="ew")
        encabezado.columnconfigure(0, weight=1)
        marca = ttk.Frame(encabezado, style="Header.TFrame")
        marca.grid(row=0, column=0, sticky="w")
        ttk.Label(marca, image=self._iconos["logo"], style="HeaderLogo.TLabel").pack(side="left", padx=(0, 10))
        ttk.Label(marca, text="Sistema Restaurante", style="HeaderTitle.TLabel").pack(side="left")
        ttk.Label(encabezado, text=f"Sesión  ·  {usuario.nombre_usuario}", style="HeaderMeta.TLabel").grid(
            row=0, column=1, padx=18
        )
        ttk.Button(
            encabezado,
            text="Cerrar sesión",
            command=self.cerrar_sesion,
            style="Header.TButton",
        ).grid(
            row=0, column=2, sticky="e"
        )

        menu = ttk.Frame(self, padding=(16, 24), style="Sidebar.TFrame")
        menu.grid(row=1, column=0, sticky="nsew")
        menu.grid_propagate(False)
        ttk.Label(menu, text="NAVEGACIÓN", style="SidebarHeading.TLabel").pack(
            anchor="w", pady=(0, 12)
        )
        self._boton_inicio = ttk.Button(
            menu,
            text="Inicio",
            image=self._iconos["inicio"],
            compound="left",
            command=self.mostrar_inicio,
            style="Nav.TButton",
        )
        self._boton_inicio.pack(fill="x", pady=3)
        self._boton_productos = ttk.Button(
            menu,
            text="Productos",
            image=self._iconos["productos"],
            compound="left",
            command=self.mostrar_productos,
            style="NavActive.TButton",
        )
        self._boton_productos.pack(fill="x", pady=3)
        self._boton_usuarios = ttk.Button(
            menu,
            text="Usuarios",
            image=self._iconos["usuarios"],
            compound="left",
            command=self.mostrar_usuarios,
            style="Nav.TButton",
        )
        self._boton_usuarios.pack(fill="x", pady=3)
        self._boton_ventas = ttk.Button(
            menu,
            text="Ventas",
            image=self._iconos["ventas"],
            compound="left",
            command=self.mostrar_ventas,
            style="Nav.TButton",
        )
        self._boton_ventas.pack(fill="x", pady=3)
        ttk.Separator(menu).pack(fill="x", pady=(18, 12))
        ttk.Label(menu, text="GESTIÓN  /  SEMANA 15", style="SidebarHeading.TLabel").pack(anchor="w")

        self.canvas_contenido = tk.Canvas(self, highlightthickness=0, background="#F3F6F2")
        self.scrollbar_contenido = ttk.Scrollbar(self, orient="vertical", command=self.canvas_contenido.yview)
        self.canvas_contenido.configure(yscrollcommand=self.scrollbar_contenido.set)
        self.canvas_contenido.grid(row=1, column=1, sticky="nsew")
        self.scrollbar_contenido.grid(row=1, column=2, sticky="ns")

        self.contenido = ttk.Frame(self.canvas_contenido, padding=(30, 26), style="App.TFrame")
        self._ventana_contenido = self.canvas_contenido.create_window(
            (0, 0), window=self.contenido, anchor="nw"
        )
        self.contenido.bind("<Configure>", self._actualizar_scroll_contenido)
        self.canvas_contenido.bind("<Configure>", self._ajustar_ancho_contenido)
        self.contenido.columnconfigure(0, weight=1)
        self.contenido.rowconfigure(1, weight=1)
        self._crear_variables_venta()
        self.mostrar_productos()

    def _seleccionar_seccion(self, seleccion: str) -> None:
        self._boton_inicio.configure(
            style="NavActive.TButton" if seleccion == "inicio" else "Nav.TButton"
        )
        self._boton_productos.configure(
            style="NavActive.TButton" if seleccion == "productos" else "Nav.TButton"
        )
        self._boton_usuarios.configure(
            style="NavActive.TButton" if seleccion == "usuarios" else "Nav.TButton"
        )
        self._boton_ventas.configure(
            style="NavActive.TButton" if seleccion == "ventas" else "Nav.TButton"
        )

    def _actualizar_scroll_contenido(self, evento: tk.Event | None = None) -> None:
        self.canvas_contenido.update_idletasks()
        region = self.canvas_contenido.bbox("all")
        if region is not None:
            self.canvas_contenido.configure(scrollregion=region)

    def _ajustar_ancho_contenido(self, evento: tk.Event) -> None:
        self.canvas_contenido.itemconfigure(self._ventana_contenido, width=evento.width)
        self._actualizar_scroll_contenido()

    def _limpiar_contenido(self) -> None:
        for widget in self.contenido.winfo_children():
            widget.destroy()
        self._actualizar_scroll_contenido()

    def mostrar_inicio(self) -> None:
        self._limpiar_contenido()
        self._seleccionar_seccion("inicio")
        for columna in range(3):
            self.contenido.columnconfigure(columna, weight=1)
        self.contenido.rowconfigure(1, weight=0)
        ttk.Label(self.contenido, text="Panel principal", style="PageTitle.TLabel").grid(
            row=0, column=0, columnspan=3, sticky="w", pady=(0, 8)
        )
        ttk.Label(
            self.contenido,
            text=f"Bienvenido, {self.usuario.nombre}",
            style="Muted.TLabel",
        ).grid(row=1, column=0, columnspan=3, sticky="w", pady=(0, 22))

        marca = ttk.Frame(self.contenido, padding=18, style="Header.TFrame")
        marca.grid(row=2, column=0, columnspan=3, sticky="ew", pady=(0, 18))
        self._logo_inicio = cargar_logo(
            self, dimension_maxima=220, foreground="#B6533D"
        )
        ttk.Label(marca, image=self._logo_inicio, style="HeaderLogo.TLabel").pack(
            side="left", padx=(0, 22)
        )
        marca_texto = ttk.Frame(marca, style="Header.TFrame")
        marca_texto.pack(side="left", anchor="center")
        ttk.Label(
            marca_texto,
            text="Sistema Restaurante",
            style="HeaderTitle.TLabel",
        ).pack(anchor="w")
        ttk.Label(
            marca_texto,
            text="Gestión de usuarios, productos y ventas",
            style="HeaderMeta.TLabel",
        ).pack(anchor="w", pady=(6, 0))

        resumenes = (
            ("Usuarios", self.servicio.cantidad_usuarios()),
            ("Productos", self.servicio.cantidad_productos()),
            ("Ventas", len(self.servicio.listar_ventas())),
        )
        for columna, (etiqueta, cantidad) in enumerate(resumenes):
            resumen = ttk.LabelFrame(
                self.contenido,
                text=etiqueta,
                padding=(18, 14),
                style="Panel.TLabelframe",
            )
            resumen.grid(row=3, column=columna, sticky="ew", padx=(0, 12))
            ttk.Label(resumen, text=str(cantidad), style="StatValue.TLabel").pack(anchor="w")
        self._habilitar_scroll_contenido()

    def mostrar_productos(self) -> None:
        self._limpiar_contenido()
        self._seleccionar_seccion("productos")
        self.contenido.columnconfigure(0, weight=0, minsize=245)
        self.contenido.columnconfigure(1, weight=1)
        self.contenido.rowconfigure(1, weight=1)
        ttk.Label(
            self.contenido,
            text="Productos registrados",
            style="PageTitle.TLabel",
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 12))
        self._crear_formulario_producto()
        self._crear_tabla_productos()
        ttk.Label(self.contenido, textvariable=self.estado_var, style="Muted.TLabel").grid(
            row=2, column=0, columnspan=2, sticky="e", pady=(8, 0)
        )
        self._refrescar_tabla_productos()
        self._habilitar_scroll_contenido()

    def _habilitar_scroll_contenido(self) -> None:
        def agregar_tag(widget: tk.Misc, tag: str) -> None:
            tags = widget.bindtags()
            if tag not in tags:
                widget.bindtags((tags[0], tag, *tags[1:]))
            for hijo in widget.winfo_children():
                agregar_tag(hijo, tag)

        agregar_tag(self.contenido, self._tag_scroll)
        self.canvas_contenido.yview_moveto(0)

    def _desplazar_contenido(self, evento: tk.Event) -> str:
        if getattr(evento, "num", None) == 4:
            unidades = -1
        elif getattr(evento, "num", None) == 5:
            unidades = 1
        else:
            unidades = -1 if getattr(evento, "delta", 0) > 0 else 1
            if abs(getattr(evento, "delta", 0)) >= 120:
                unidades *= max(1, abs(evento.delta) // 120)
        self.canvas_contenido.yview_scroll(unidades, "units")
        return "break"

    def _liberar_eventos(self, evento: tk.Event) -> None:
        if evento.widget is not self:
            return
        for secuencia in ("<MouseWheel>", "<Button-4>", "<Button-5>"):
            self.bind_class(self._tag_scroll, secuencia, "")

    def _crear_variables_producto(self) -> None:
        self.id_producto_var = tk.StringVar()
        self.nombre_producto_var = tk.StringVar()
        self.precio_producto_var = tk.StringVar()
        self.categoria_producto_var = tk.StringVar()
        self.stock_producto_var = tk.StringVar()

    def _crear_variables_usuario(self) -> None:
        self.nombre_nuevo_usuario_var = tk.StringVar()
        self.apellido_nuevo_usuario_var = tk.StringVar()
        self.cuenta_nuevo_usuario_var = tk.StringVar()
        self.contrasena_nuevo_usuario_var = tk.StringVar()
        self.correo_nuevo_usuario_var = tk.StringVar()
        self.fecha_nacimiento_nuevo_usuario_var = tk.StringVar()
        self.rol_nuevo_usuario_var = tk.StringVar(
            value="Empleado" if self.usuario.es_administrador else "Cliente"
        )
        self.rango_nuevo_usuario_var = self.rol_nuevo_usuario_var
        self.usuario_seleccionado_id = None

    def _crear_formulario_producto(self) -> None:
        formulario = ttk.LabelFrame(
            self.contenido, text="Datos del producto", padding=14, style="Panel.TLabelframe"
        )
        formulario.grid(row=1, column=0, sticky="new", padx=(0, 16))
        formulario.columnconfigure(0, weight=1)

        campos = (
            ("ID", self.id_producto_var, 0),
            ("Nombre", self.nombre_producto_var, 1),
            ("Precio", self.precio_producto_var, 2),
            ("Categoría", self.categoria_producto_var, 3),
            ("Stock", self.stock_producto_var, 4),
        )
        for fila, (etiqueta, variable, _) in enumerate(campos):
            ttk.Label(formulario, text=etiqueta, style="Panel.TLabel").grid(
                row=fila * 2, column=0, sticky="w", padx=4
            )
            ttk.Entry(formulario, textvariable=variable).grid(
                row=fila * 2 + 1, column=0, sticky="ew", padx=4, pady=(2, 4)
            )

        acciones = ttk.Frame(formulario, style="Panel.TFrame")
        acciones.grid(row=10, column=0, sticky="ew", pady=(8, 0))
        ttk.Button(
            acciones, text="Registrar", command=self._registrar_producto, style="Primary.TButton"
        ).pack(fill="x", pady=2)
        ttk.Button(
            acciones, text="Cargar / Consultar", command=self._consultar_producto, style="TButton"
        ).pack(fill="x", pady=2)
        ttk.Button(
            acciones, text="Actualizar", command=self._actualizar_producto, style="TButton"
        ).pack(fill="x", pady=2)
        ttk.Button(
            acciones, text="Eliminar", command=self._eliminar_producto, style="Danger.TButton"
        ).pack(fill="x", pady=2)
        ttk.Button(
            acciones, text="Limpiar", command=self._limpiar_formulario_producto, style="TButton"
        ).pack(fill="x", pady=2)

    def _crear_tabla_productos(self) -> None:
        contenedor = ttk.Frame(self.contenido)
        contenedor.grid(row=1, column=1, sticky="nsew")
        contenedor.columnconfigure(0, weight=1)
        contenedor.rowconfigure(0, weight=1)
        self.tabla_productos = ttk.Treeview(
            contenedor,
            columns=("id", "nombre", "categoria", "precio", "stock"),
            show="headings",
            height=12,
            style="Table.Treeview",
        )
        for columna, encabezado in zip(
            ("id", "nombre", "categoria", "precio", "stock"),
            ("ID", "Nombre", "Categoría", "Precio", "Cantidad"),
        ):
            self.tabla_productos.heading(columna, text=encabezado)
            anchos = {"id": 70, "nombre": 230, "categoria": 160, "precio": 110, "stock": 100}
            self.tabla_productos.column(columna, width=anchos[columna], anchor="center", stretch=True)
        self.tabla_productos.grid(row=0, column=0, sticky="nsew")
        barra = ttk.Scrollbar(contenedor, orient="vertical", command=self.tabla_productos.yview)
        barra.grid(row=0, column=1, sticky="ns")
        barra_horizontal = ttk.Scrollbar(contenedor, orient="horizontal", command=self.tabla_productos.xview)
        barra_horizontal.grid(row=1, column=0, sticky="ew")
        self.tabla_productos.configure(yscrollcommand=barra.set, xscrollcommand=barra_horizontal.set)

    def _refrescar_tabla_productos(self) -> None:
        for fila in self.tabla_productos.get_children():
            self.tabla_productos.delete(fila)
        productos = self.servicio.listar_productos()
        for producto in productos:
            self.tabla_productos.insert(
                "",
                "end",
                values=(
                    producto.id_producto,
                    producto.nombre,
                    producto.categoria,
                    f"${producto.precio:.2f}",
                    producto.stock,
                ),
            )
        self.estado_var.set(f"{len(productos)} productos")

    def _datos_producto(self) -> tuple[int, str, float, str, int]:
        return (
            int(self.id_producto_var.get().strip()),
            self.nombre_producto_var.get(),
            float(self.precio_producto_var.get().strip()),
            self.categoria_producto_var.get(),
            int(self.stock_producto_var.get().strip()),
        )

    def _registrar_producto(self) -> None:
        try:
            self.servicio.registrar_producto(*self._datos_producto())
            self._refrescar_tabla_productos()
            self._limpiar_formulario_producto()
            messagebox.showinfo("Producto registrado", "El producto se guardó correctamente.")
        except (ValueError, OSError) as error:
            messagebox.showerror("No se pudo registrar", str(error))

    def _consultar_producto(self) -> None:
        try:
            producto = self.servicio.buscar_producto(int(self.id_producto_var.get().strip()))
            if producto is None:
                raise ValueError("No existe un producto con ese identificador.")
            self._mostrar_producto_en_formulario(producto)
        except ValueError as error:
            messagebox.showerror("Consulta no disponible", str(error))

    def _actualizar_producto(self) -> None:
        try:
            self.servicio.actualizar_producto(*self._datos_producto())
            self._refrescar_tabla_productos()
            messagebox.showinfo("Producto actualizado", "Los cambios se guardaron correctamente.")
        except (ValueError, OSError) as error:
            messagebox.showerror("No se pudo actualizar", str(error))

    def _eliminar_producto(self) -> None:
        try:
            id_producto = int(self.id_producto_var.get().strip())
            if not messagebox.askyesno(
                "Confirmar eliminación",
                f"¿Desea eliminar el producto con ID {id_producto}?",
            ):
                return
            self.servicio.eliminar_producto(id_producto)
            self._refrescar_tabla_productos()
            self._limpiar_formulario_producto()
            messagebox.showinfo("Producto eliminado", "El producto dejó de estar disponible.")
        except (ValueError, OSError) as error:
            messagebox.showerror("No se pudo eliminar", str(error))

    def _mostrar_producto_en_formulario(self, producto: Producto) -> None:
        self.nombre_producto_var.set(producto.nombre)
        self.precio_producto_var.set(str(producto.precio))
        self.categoria_producto_var.set(producto.categoria)
        self.stock_producto_var.set(str(producto.stock))

    def _limpiar_formulario_producto(self) -> None:
        for variable in (
            self.id_producto_var,
            self.nombre_producto_var,
            self.precio_producto_var,
            self.categoria_producto_var,
            self.stock_producto_var,
        ):
            variable.set("")

    def mostrar_usuarios(self) -> None:
        if not self.usuario.es_administrador and self.usuario.rol != "Empleado":
            messagebox.showwarning(
                "Acceso restringido",
                "Las cuentas de cliente no tienen acceso a la administración del sistema.",
            )
            self.mostrar_inicio()
            return

        if self.usuario.es_administrador:
            self._modo_usuarios = "admin"
            self._rol_permitido = ("Empleado", "Cliente")
            titulo = "Administración de usuarios"
            descripcion = "El administrador puede gestionar las cuentas del equipo y los clientes."
        else:
            self._modo_usuarios = "clientes"
            self._rol_permitido = ("Cliente",)
            titulo = "Registro de clientes"
            descripcion = "El personal puede registrar y mantener únicamente cuentas de clientes."

        self._limpiar_contenido()
        self._seleccionar_seccion("usuarios")
        self.contenido.columnconfigure(0, weight=1)
        self.contenido.rowconfigure(1, weight=0)
        self.contenido.rowconfigure(2, weight=1)
        ttk.Label(self.contenido, text=titulo, style="PageTitle.TLabel").grid(
            row=0, column=0, sticky="w", pady=(0, 12)
        )
        ttk.Label(self.contenido, text=descripcion, style="Muted.TLabel").grid(
            row=1, column=0, sticky="w", pady=(0, 12)
        )
        self.contenido.rowconfigure(2, weight=0)
        self.contenido.rowconfigure(3, weight=1)
        self._crear_formulario_usuario()
        self._crear_tabla_usuarios()
        ttk.Label(self.contenido, textvariable=self.estado_var, style="Muted.TLabel").grid(
            row=4, column=0, sticky="e", pady=(8, 0)
        )
        self._refrescar_tabla_usuarios()
        self._habilitar_scroll_contenido()

    def _crear_formulario_usuario(self) -> None:
        formulario = ttk.LabelFrame(
            self.contenido,
            text="Registrar usuario" if self._modo_usuarios == "admin" else "Registrar cliente",
            padding=14,
            style="Panel.TLabelframe",
        )
        formulario.grid(row=2, column=0, sticky="ew", pady=(0, 16))
        for columna in range(4):
            formulario.columnconfigure(columna, weight=1)

        campos = (
            ("Nombre", self.nombre_nuevo_usuario_var, 0, 0, 1, "text"),
            ("Apellido", self.apellido_nuevo_usuario_var, 0, 1, 1, "text"),
            ("Usuario", self.cuenta_nuevo_usuario_var, 0, 2, 1, "text"),
            ("Contraseña", self.contrasena_nuevo_usuario_var, 0, 3, 1, "password"),
            ("Correo electrónico", self.correo_nuevo_usuario_var, 2, 0, 2, "text"),
            ("Nacimiento (AAAA-MM-DD)", self.fecha_nacimiento_nuevo_usuario_var, 2, 2, 1, "text"),
        )
        for etiqueta, variable, fila, columna, span, tipo in campos:
            ttk.Label(formulario, text=etiqueta, style="Panel.TLabel").grid(
                row=fila, column=columna, columnspan=span, sticky="w", padx=5
            )
            entrada = ttk.Entry(
                formulario,
                textvariable=variable,
                show=(
                    ""
                    if tipo == "password" and self.usuario.es_administrador
                    else "*" if tipo == "password" else ""
                ),
            )
            entrada.grid(
                row=fila + 1,
                column=columna,
                columnspan=span,
                sticky="ew",
                padx=5,
                pady=(4, 12),
            )
            entrada.bind("<Return>", self._evento_enter_usuario)
            entrada.bind("<Escape>", self._evento_escape_usuario)
            if variable is self.contrasena_nuevo_usuario_var:
                self.contrasena_usuario_entry = entrada

        ttk.Label(formulario, text="Rol", style="Panel.TLabel").grid(
            row=2, column=3, sticky="w", padx=5
        )
        self.rol_selector_usuario = ttk.Combobox(
            formulario,
            textvariable=self.rol_nuevo_usuario_var,
            values=self._rol_permitido,
            state="readonly",
        )
        if self._modo_usuarios != "admin":
            self.rol_nuevo_usuario_var.set("Cliente")
        elif not self.rol_nuevo_usuario_var.get():
            self.rol_nuevo_usuario_var.set("Empleado")
        self.rol_selector_usuario.grid(row=3, column=3, sticky="ew", padx=5, pady=(4, 12))
        self.rol_selector_usuario.bind("<<ComboboxSelected>>", self._evento_cambio_rol_usuario)
        self.rol_selector_usuario.bind("<Return>", self._evento_enter_usuario)
        self.rol_selector_usuario.bind("<Escape>", self._evento_escape_usuario)

        acciones = ttk.Frame(formulario, style="Panel.TFrame")
        acciones.grid(row=4, column=0, columnspan=4, sticky="ew", padx=5, pady=(2, 0))
        ttk.Button(
            acciones,
            text="Registrar usuario",
            command=self._registrar_usuario,
            style="Primary.TButton",
        ).pack(side="left")
        ttk.Button(
            acciones,
            text="Actualizar",
            command=self._actualizar_usuario,
            style="TButton",
        ).pack(side="left", padx=8)
        ttk.Button(
            acciones,
            text="Eliminar",
            command=self._eliminar_usuario,
            style="Danger.TButton",
        ).pack(side="left", padx=8)
        ttk.Button(
            acciones,
            text="Limpiar",
            command=self._limpiar_formulario_usuario,
            style="TButton",
        ).pack(side="left", padx=8)

    def _crear_tabla_usuarios(self) -> None:
        contenedor = ttk.Frame(self.contenido)
        contenedor.grid(row=3, column=0, sticky="nsew")
        contenedor.columnconfigure(0, weight=1)
        contenedor.rowconfigure(0, weight=1)

        columnas = ("id", "nombre", "apellido", "nombre_usuario", "correo", "fecha_nacimiento", "rol")
        encabezados = ("ID", "Nombre", "Apellido", "Usuario", "Correo electrónico", "Nacimiento", "Rol")

        self.tabla_usuarios = ttk.Treeview(
            contenedor,
            columns=columnas,
            show="headings",
            height=9,
            style="Table.Treeview",
        )
        anchos = (60, 120, 130, 130, 220, 140, 120)
        for columna, encabezado, ancho in zip(columnas, encabezados, anchos):
            self.tabla_usuarios.heading(columna, text=encabezado)
            self.tabla_usuarios.column(columna, width=ancho, minwidth=75, anchor="center", stretch=True)
        self.tabla_usuarios.grid(row=0, column=0, sticky="nsew")
        barra_vertical = ttk.Scrollbar(contenedor, orient="vertical", command=self.tabla_usuarios.yview)
        barra_vertical.grid(row=0, column=1, sticky="ns")
        barra_horizontal = ttk.Scrollbar(contenedor, orient="horizontal", command=self.tabla_usuarios.xview)
        barra_horizontal.grid(row=1, column=0, sticky="ew")
        self.tabla_usuarios.configure(
            yscrollcommand=barra_vertical.set,
            xscrollcommand=barra_horizontal.set,
        )
        self.tabla_usuarios.bind("<<TreeviewSelect>>", self._cargar_usuario_seleccionado)
        self.tabla_usuarios.bind("<Escape>", self._evento_escape_usuario)

    def _refrescar_tabla_usuarios(self) -> None:
        for fila in self.tabla_usuarios.get_children():
            self.tabla_usuarios.delete(fila)
        usuarios = self.servicio.usuarios_permitidos_para(self.usuario)
        for usuario in usuarios:
            valores = (
                usuario.id_usuario,
                usuario.nombre,
                usuario.apellido,
                usuario.nombre_usuario,
                usuario.correo_electronico,
                usuario.fecha_nacimiento,
                usuario.rol,
            )
            self.tabla_usuarios.insert("", "end", values=valores)
        self.estado_var.set(f"{len(usuarios)} usuarios")

    def _evento_cambio_rol_usuario(self, evento: tk.Event | None = None) -> None:
        self.estado_var.set(f"Rol seleccionado: {self.rol_nuevo_usuario_var.get()}")

    def _evento_enter_usuario(self, evento: tk.Event | None = None) -> str:
        self._registrar_usuario()
        return "break"

    def _evento_escape_usuario(self, evento: tk.Event | None = None) -> str:
        self._limpiar_formulario_usuario()
        return "break"

    def _cargar_usuario_seleccionado(self, evento: tk.Event | None = None) -> None:
        seleccion = self.tabla_usuarios.selection()
        if not seleccion:
            return
        valores = self.tabla_usuarios.item(seleccion[0], "values")
        if not valores:
            return
        id_usuario = int(valores[0])
        self.usuario_seleccionado_id = id_usuario
        usuario = self.servicio.buscar_usuario(id_usuario)
        if usuario is None:
            return
        if not self.usuario.es_administrador and usuario.rol != "Cliente":
            messagebox.showwarning(
                "Acceso restringido",
                "Los cajeros y meseros solo pueden administrar clientes.",
            )
            self._limpiar_formulario_usuario()
            return
        self.nombre_nuevo_usuario_var.set(usuario.nombre)
        self.apellido_nuevo_usuario_var.set(usuario.apellido)
        self.cuenta_nuevo_usuario_var.set(usuario.nombre_usuario)
        self.contrasena_nuevo_usuario_var.set(usuario.contrasena)
        self.correo_nuevo_usuario_var.set(usuario.correo_electronico)
        self.fecha_nacimiento_nuevo_usuario_var.set(usuario.fecha_nacimiento)
        self.rol_nuevo_usuario_var.set(usuario.rol)
        self.estado_var.set(f"Seleccionado: {usuario.nombre_usuario}")

    def _registrar_usuario(self) -> None:
        try:
            rol = self.rol_nuevo_usuario_var.get()
            self.servicio.validar_permiso_rol(self.usuario, rol)
            if not self.usuario.es_administrador:
                rol = "Cliente"
            usuario = self.servicio.registrar_usuario(
                self.nombre_nuevo_usuario_var.get(),
                self.apellido_nuevo_usuario_var.get(),
                self.cuenta_nuevo_usuario_var.get(),
                self.contrasena_nuevo_usuario_var.get(),
                self.correo_nuevo_usuario_var.get(),
                self.fecha_nacimiento_nuevo_usuario_var.get(),
                rol=rol,
                usuario_actual=self.usuario,
            )
            self._refrescar_tabla_usuarios()
            self._limpiar_formulario_usuario()
            messagebox.showinfo(
                "Usuario registrado",
                (
                    f"El cliente '{usuario.nombre_usuario}' quedó registrado para ventas. "
                    "Las cuentas de cliente no pueden iniciar sesión."
                    if usuario.rol == "Cliente"
                    else f"La cuenta de personal '{usuario.nombre_usuario}' ya puede iniciar sesión."
                ),
            )
        except (ValueError, OSError) as error:
            messagebox.showerror("No se pudo registrar", str(error))

    def _actualizar_usuario(self) -> None:
        try:
            if self.usuario_seleccionado_id is None:
                raise ValueError("Seleccione un usuario en la tabla para actualizarlo.")
            usuario_actual = self.servicio.buscar_usuario(self.usuario_seleccionado_id)
            if usuario_actual is None:
                raise ValueError("El usuario seleccionado ya no existe.")
            nuevo_rol = self.rol_nuevo_usuario_var.get()
            if not self.usuario.es_administrador and usuario_actual.rol != "Cliente":
                raise ValueError("Los cajeros y meseros solo pueden editar clientes.")
            if not self.usuario.es_administrador:
                self.servicio.validar_permiso_rol(self.usuario, nuevo_rol)
            if not self.usuario.es_administrador:
                nuevo_rol = "Cliente"
            usuario_actualizado = self.servicio.actualizar_usuario(
                self.usuario_seleccionado_id,
                self.nombre_nuevo_usuario_var.get(),
                self.apellido_nuevo_usuario_var.get(),
                self.cuenta_nuevo_usuario_var.get(),
                self.contrasena_nuevo_usuario_var.get(),
                self.correo_nuevo_usuario_var.get(),
                self.fecha_nacimiento_nuevo_usuario_var.get(),
                rol=nuevo_rol,
                usuario_actual=self.usuario,
            )
            self._refrescar_tabla_usuarios()
            self._limpiar_formulario_usuario()
            messagebox.showinfo(
                "Usuario actualizado",
                f"La cuenta '{usuario_actualizado.nombre_usuario}' se actualizó correctamente.",
            )
        except (ValueError, OSError) as error:
            messagebox.showerror("No se pudo actualizar", str(error))

    def _eliminar_usuario(self) -> None:
        try:
            if self.usuario_seleccionado_id is None:
                raise ValueError("Seleccione un usuario en la tabla para eliminarlo.")
            usuario = self.servicio.buscar_usuario(self.usuario_seleccionado_id)
            if usuario is None:
                raise ValueError("El usuario seleccionado ya no existe.")
            if not self.usuario.es_administrador and usuario.rol != "Cliente":
                raise ValueError("Los cajeros y meseros solo pueden eliminar clientes.")
            if usuario.id_usuario == self.usuario.id_usuario:
                raise ValueError("No puedes eliminar la cuenta administrativa actualmente autenticada.")
            if not messagebox.askyesno(
                "Confirmar eliminación",
                f"¿Desea eliminar al usuario '{usuario.nombre_usuario}'?",
            ):
                return
            self.servicio.eliminar_usuario(
                usuario.id_usuario,
                usuario_actual=self.usuario,
            )
            self._refrescar_tabla_usuarios()
            self._limpiar_formulario_usuario()
            messagebox.showinfo("Usuario eliminado", "La cuenta fue eliminada del sistema.")
        except (ValueError, OSError) as error:
            messagebox.showerror("No se pudo eliminar", str(error))

    def _limpiar_formulario_usuario(self) -> None:
        if hasattr(self, "tabla_usuarios") and self.tabla_usuarios.winfo_exists():
            seleccion = self.tabla_usuarios.selection()
            if seleccion:
                self.tabla_usuarios.selection_remove(*seleccion)
        self.usuario_seleccionado_id = None
        for variable in (
            self.nombre_nuevo_usuario_var,
            self.apellido_nuevo_usuario_var,
            self.cuenta_nuevo_usuario_var,
            self.contrasena_nuevo_usuario_var,
            self.correo_nuevo_usuario_var,
            self.fecha_nacimiento_nuevo_usuario_var,
        ):
            variable.set("")
        self.rol_nuevo_usuario_var.set(
            "Cliente" if self._modo_usuarios != "admin" else "Empleado"
        )
        self.estado_var.set("")

    def _crear_variables_venta(self) -> None:
        self.usuario_venta_var = tk.StringVar(master=self)
        self.producto_venta_var = tk.StringVar(master=self)
        self._usuarios_por_opcion: dict[str, int] = {}
        self._productos_por_opcion: dict[str, int] = {}

    def mostrar_ventas(self) -> None:
        self._limpiar_contenido()
        self._seleccionar_seccion("ventas")
        self.contenido.columnconfigure(0, weight=0, minsize=245)
        self.contenido.columnconfigure(1, weight=1)
        self.contenido.rowconfigure(1, weight=1)
        ttk.Label(self.contenido, text="Registro de ventas", style="PageTitle.TLabel").grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(0, 12)
        )
        self._crear_formulario_venta()
        self._crear_tabla_ventas()
        ttk.Label(self.contenido, textvariable=self.estado_var, style="Muted.TLabel").grid(
            row=2, column=0, columnspan=2, sticky="e", pady=(8, 0)
        )
        self._refrescar_tabla_ventas()
        self._habilitar_scroll_contenido()

    def _crear_formulario_venta(self) -> None:
        formulario = ttk.LabelFrame(
            self.contenido, text="Nueva venta", padding=16, style="Panel.TLabelframe"
        )
        formulario.grid(row=1, column=0, sticky="new", padx=(0, 16))
        formulario.columnconfigure(0, weight=1)

        usuarios = [
            usuario
            for usuario in self.servicio.listar_usuarios()
            if usuario.rol == "Cliente"
        ]
        productos = self.servicio.listar_productos()
        self._usuarios_por_opcion = {
            f"{usuario.id_usuario} · {usuario.nombre} {usuario.apellido} (@{usuario.nombre_usuario})": usuario.id_usuario
            for usuario in usuarios
        }
        self._productos_por_opcion = {
            f"{producto.id_producto} · {producto.nombre} (${producto.precio:.2f})": producto.id_producto
            for producto in productos
        }

        ttk.Label(formulario, text="Usuario", style="Panel.TLabel").grid(
            row=0, column=0, sticky="w", padx=5
        )
        ttk.Label(formulario, text="Producto", style="Panel.TLabel").grid(
            row=2, column=0, sticky="w", padx=5
        )
        ttk.Combobox(
            formulario,
            textvariable=self.usuario_venta_var,
            values=tuple(self._usuarios_por_opcion),
            state="readonly",
        ).grid(row=1, column=0, sticky="ew", padx=5, pady=(4, 12))
        ttk.Combobox(
            formulario,
            textvariable=self.producto_venta_var,
            values=tuple(self._productos_por_opcion),
            state="readonly",
        ).grid(row=3, column=0, sticky="ew", padx=5, pady=(4, 12))
        ttk.Button(
            formulario,
            text="Registrar venta",
            command=self._registrar_venta,
            style="Primary.TButton",
        ).grid(row=4, column=0, sticky="ew", padx=5, pady=(8, 0))
        ttk.Button(
            formulario,
            text="Generar reporte PDF",
            command=self._generar_reporte_ventas,
            style="TButton",
        ).grid(row=5, column=0, sticky="ew", padx=5, pady=(8, 0))

    def _crear_tabla_ventas(self) -> None:
        contenedor = ttk.Frame(self.contenido)
        contenedor.grid(row=1, column=1, sticky="nsew")
        contenedor.columnconfigure(0, weight=1)
        contenedor.rowconfigure(0, weight=1)
        self.tabla_ventas = ttk.Treeview(
            contenedor,
            columns=("venta", "usuario", "producto", "fecha"),
            show="headings",
            height=12,
            style="Table.Treeview",
        )
        for columna, encabezado, ancho in (
            ("venta", "Venta", 75),
            ("usuario", "Usuario", 210),
            ("producto", "Producto", 230),
            ("fecha", "Fecha y hora", 175),
        ):
            self.tabla_ventas.heading(columna, text=encabezado)
            self.tabla_ventas.column(columna, width=ancho, minwidth=120, anchor="w", stretch=True)
        self.tabla_ventas.grid(row=0, column=0, sticky="nsew")
        barra = ttk.Scrollbar(contenedor, orient="vertical", command=self.tabla_ventas.yview)
        barra.grid(row=0, column=1, sticky="ns")
        self.tabla_ventas.configure(yscrollcommand=barra.set)

    def _refrescar_tabla_ventas(self) -> None:
        for fila in self.tabla_ventas.get_children():
            self.tabla_ventas.delete(fila)
        usuarios = {usuario.id_usuario: usuario for usuario in self.servicio.listar_usuarios()}
        productos = {producto.id_producto: producto for producto in self.servicio.listar_productos()}
        ventas = self.servicio.listar_ventas()
        for consecutivo, venta in enumerate(ventas, start=1):
            usuario = usuarios.get(venta.usuario_id)
            producto = productos.get(venta.producto_id)
            self.tabla_ventas.insert(
                "",
                "end",
                values=(
                    f"V{consecutivo:03d}",
                    f"{usuario.id_usuario:03d} · {usuario.nombre_usuario}" if usuario else f"Usuario {venta.usuario_id}",
                    f"{producto.id_producto:03d} · {producto.nombre}" if producto else f"Producto {venta.producto_id}",
                    venta.fecha.replace("T", " "),
                ),
            )
        self.estado_var.set(f"{len(ventas)} ventas registradas")

    def _registrar_venta(self) -> None:
        usuario_id = self._usuarios_por_opcion.get(self.usuario_venta_var.get())
        producto_id = self._productos_por_opcion.get(self.producto_venta_var.get())
        if usuario_id is None or producto_id is None:
            messagebox.showerror("Selección requerida", "Seleccione un usuario y un producto.")
            return

        try:
            self.servicio.registrar_venta(usuario_id, producto_id)
            self._refrescar_tabla_ventas()
            messagebox.showinfo("Venta registrada", "La venta se guardó correctamente.")
        except (ValueError, OSError) as error:
            messagebox.showerror("No se pudo registrar la venta", str(error))

    def _generar_reporte_ventas(self) -> None:
        ruta_archivo = filedialog.asksaveasfilename(
            title="Guardar reporte de ventas",
            initialfile="reporte_ventas.pdf",
            defaultextension=".pdf",
            filetypes=(("Documento PDF", "*.pdf"),),
        )
        if not ruta_archivo:
            return

        try:
            ruta_guardada = self.servicio.generar_reporte_ventas(ruta_archivo)
            messagebox.showinfo("Reporte generado", f"El reporte se guardó en:\n{ruta_guardada}")
        except (ValueError, OSError) as error:
            messagebox.showerror("No se pudo generar el reporte", str(error))
