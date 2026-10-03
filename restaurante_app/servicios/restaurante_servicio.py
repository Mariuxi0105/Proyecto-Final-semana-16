from pathlib import Path
from typing import List, Optional
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape, letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from modelos.producto import Producto
from modelos.usuario import Usuario
from modelos.venta import Venta
from servicios.archivo_servicio import ArchivoServicio


class RestauranteServicio:
    """Fachada de datos y reglas necesarias para la primera interfaz gráfica."""

    ROLES_PERMITIDOS = ("Administrador", "Empleado", "Cliente")

    def __init__(self, archivo_servicio: type[ArchivoServicio] = ArchivoServicio) -> None:
        self._archivo_servicio = archivo_servicio
        self._productos: List[Producto] = []
        self._usuarios: List[Usuario] = []
        self._ventas: List[Venta] = []

    @staticmethod
    def _normalizar_rol(rol: str | None, valor_predeterminado: str = "Cliente") -> str:
        valor = (rol if rol is not None else valor_predeterminado).strip()
        if not valor:
            return valor_predeterminado
        equivalente = {
            "administrador": "Administrador",
            "admin": "Administrador",
            "empleado": "Empleado",
            "cajero": "Empleado",
            "cocina": "Empleado",
            "mesero": "Empleado",
            "mesera": "Empleado",
            "cliente": "Cliente",
        }
        return equivalente.get(valor.casefold(), valor)

    def cargar_datos(self) -> None:
        self._productos = self._archivo_servicio.cargar_productos()
        self._usuarios = self._archivo_servicio.cargar_usuarios()
        for usuario in self._usuarios:
            usuario.rol = self._normalizar_rol(usuario.rol or usuario.rango, "Cliente")
            usuario.rango = usuario.rol
        self._ventas = self._archivo_servicio.cargar_ventas()

    def validar_acceso(self, nombre_usuario: str, contrasena: str) -> Optional[Usuario]:
        """Valida el acceso comparando el nombre de usuario y su contraseña."""
        nombre_usuario_normalizado = nombre_usuario.strip().lower()
        for usuario in self._usuarios:
            if (
                usuario.nombre_usuario.lower() == nombre_usuario_normalizado
                and usuario.contrasena == contrasena.strip()
                and usuario.rol in ("Administrador", "Empleado")
            ):
                return usuario
        return None

    def listar_productos(self) -> List[Producto]:
        return list(self._productos)

    def recargar_productos(self) -> List[Producto]:
        self._productos = self._archivo_servicio.cargar_productos()
        return self.listar_productos()

    def registrar_producto(
        self,
        id_producto: int,
        nombre: str,
        precio: float,
        categoria: str,
        stock: int,
    ) -> Producto:
        if any(producto.id_producto == int(id_producto) for producto in self._productos):
            raise ValueError("Ya existe un producto con ese identificador.")

        producto = Producto(id_producto, nombre, precio, categoria, stock)
        self._productos.append(producto)
        self._guardar_productos()
        return producto

    def buscar_producto(self, id_producto: int) -> Optional[Producto]:
        id_buscado = int(id_producto)
        return next(
            (producto for producto in self._productos if producto.id_producto == id_buscado),
            None,
        )

    def actualizar_producto(
        self,
        id_producto: int,
        nombre: str,
        precio: float,
        categoria: str,
        stock: int,
    ) -> Producto:
        producto = self.buscar_producto(id_producto)
        if producto is None:
            raise ValueError("No existe un producto con ese identificador.")

        producto_actualizado = Producto(id_producto, nombre, precio, categoria, stock)
        posicion = self._productos.index(producto)
        self._productos[posicion] = producto_actualizado
        self._guardar_productos()
        return producto_actualizado

    def eliminar_producto(self, id_producto: int) -> None:
        producto = self.buscar_producto(id_producto)
        if producto is None:
            raise ValueError("No existe un producto con ese identificador.")

        self._productos.remove(producto)
        self._guardar_productos()

    def _guardar_productos(self) -> None:
        if not self._archivo_servicio.guardar_productos(self._productos):
            raise OSError("No se pudo guardar el catálogo de productos.")

    def listar_usuarios(self) -> List[Usuario]:
        return list(self._usuarios)

    def usuarios_permitidos_para(self, usuario_actual: Usuario) -> List[Usuario]:
        if usuario_actual.rol not in ("Administrador", "Empleado"):
            raise ValueError("Las cuentas de cliente no tienen acceso a la gestión de usuarios.")
        if usuario_actual.es_administrador:
            return self.listar_usuarios()
        return [usuario for usuario in self._usuarios if usuario.rol == "Cliente"]

    def puede_gestionar_usuarios(self, usuario_actual: Usuario) -> bool:
        return usuario_actual.es_administrador

    def _validar_permiso_usuario(
        self,
        usuario_actual: Usuario,
        rol_nuevo: str | None = None,
        usuario_objetivo: Usuario | None = None,
        permitir_admin_como_destino: bool = False,
    ) -> str | None:
        if usuario_actual.rol not in ("Administrador", "Empleado"):
            raise ValueError("Solo el administrador o el personal autorizado puede gestionar usuarios.")

        if self.puede_gestionar_usuarios(usuario_actual):
            if rol_nuevo is None:
                return None
            rol_normalizado = self._normalizar_rol(rol_nuevo)
            roles_admin = ("Empleado", "Cliente", "Administrador") if permitir_admin_como_destino else (
                "Empleado",
                "Cliente",
            )
            if rol_normalizado not in roles_admin:
                raise ValueError("El rol debe ser Empleado o Cliente.")
            return rol_normalizado

        if usuario_objetivo is not None and usuario_objetivo.rol != "Cliente":
            raise ValueError("El personal solo puede gestionar cuentas de clientes.")
        if rol_nuevo is None:
            return None
        rol_normalizado = self._normalizar_rol(rol_nuevo)
        if rol_normalizado != "Cliente":
            raise ValueError("El personal solo puede registrar y gestionar clientes.")
        return rol_normalizado

    def validar_permiso_rol(self, usuario_actual: Usuario, rol_nuevo: str) -> None:
        self._validar_permiso_usuario(usuario_actual, rol_nuevo)

    def buscar_usuario(self, id_usuario: int) -> Optional[Usuario]:
        id_buscado = int(id_usuario)
        return next((usuario for usuario in self._usuarios if usuario.id_usuario == id_buscado), None)

    def registrar_usuario(
        self,
        nombre: str,
        apellido: str,
        nombre_usuario: str,
        contrasena: str,
        correo_electronico: str,
        fecha_nacimiento: str,
        rol: str | None = None,
        rango: str | None = None,
        *,
        usuario_actual: Usuario,
    ) -> Usuario:
        nombre_usuario_normalizado = nombre_usuario.strip().casefold()
        correo_normalizado = correo_electronico.strip().casefold()
        if any(usuario.nombre_usuario.casefold() == nombre_usuario_normalizado for usuario in self._usuarios):
            raise ValueError("Ese nombre de usuario ya está registrado.")
        if any(usuario.correo_electronico.casefold() == correo_normalizado for usuario in self._usuarios):
            raise ValueError("Ese correo electrónico ya está registrado.")

        rol_solicitado = rol if rol is not None else rango
        rol_normalizado = self._validar_permiso_usuario(
            usuario_actual,
            rol_solicitado or "Cliente",
        )
        if rol_normalizado is None:
            raise ValueError("Seleccione un rol para el nuevo usuario.")

        siguiente_id = max((usuario.id_usuario for usuario in self._usuarios), default=0) + 1
        usuario = Usuario(
            siguiente_id,
            nombre,
            apellido,
            nombre_usuario,
            contrasena,
            correo_electronico,
            fecha_nacimiento,
            rol=rol_normalizado,
        )
        usuarios_actualizados = [*self._usuarios, usuario]
        if not self._archivo_servicio.guardar_usuarios(usuarios_actualizados):
            raise OSError("No se pudo guardar el usuario en usuarios.json.")
        self._usuarios = usuarios_actualizados
        return usuario

    def actualizar_usuario(
        self,
        id_usuario: int,
        nombre: str,
        apellido: str,
        nombre_usuario: str,
        contrasena: str,
        correo_electronico: str,
        fecha_nacimiento: str,
        rol: str | None = None,
        rango: str | None = None,
        *,
        usuario_actual: Usuario,
    ) -> Usuario:
        usuario = self.buscar_usuario(id_usuario)
        if usuario is None:
            raise ValueError("No existe un usuario con ese identificador.")

        if usuario.id_usuario == usuario_actual.id_usuario:
            raise ValueError("No puede modificar la cuenta que está usando actualmente.")
        rol_solicitado = rol if rol is not None else rango
        rol_nuevo = self._validar_permiso_usuario(
            usuario_actual,
            rol_solicitado if rol_solicitado is not None else usuario.rol,
            usuario,
            permitir_admin_como_destino=usuario.rol == "Administrador",
        )
        if rol_nuevo is None:
            raise ValueError("Seleccione un rol para el usuario.")

        nombre_usuario_normalizado = nombre_usuario.strip().casefold()
        correo_normalizado = correo_electronico.strip().casefold()
        duplicado_usuario = any(
            otro.id_usuario != usuario.id_usuario and otro.nombre_usuario.casefold() == nombre_usuario_normalizado
            for otro in self._usuarios
        )
        duplicado_correo = any(
            otro.id_usuario != usuario.id_usuario and otro.correo_electronico.casefold() == correo_normalizado
            for otro in self._usuarios
        )
        if duplicado_usuario:
            raise ValueError("Ese nombre de usuario ya está registrado.")
        if duplicado_correo:
            raise ValueError("Ese correo electrónico ya está registrado.")

        usuario_actualizado = Usuario(
            usuario.id_usuario,
            nombre,
            apellido,
            nombre_usuario,
            contrasena,
            correo_electronico,
            fecha_nacimiento,
            rol=rol_nuevo,
        )
        posicion = self._usuarios.index(usuario)
        usuarios_actualizados = list(self._usuarios)
        usuarios_actualizados[posicion] = usuario_actualizado
        if not self._archivo_servicio.guardar_usuarios(usuarios_actualizados):
            raise OSError("No se pudo actualizar el usuario en usuarios.json.")
        self._usuarios = usuarios_actualizados
        return usuario_actualizado

    def eliminar_usuario(self, id_usuario: int, *, usuario_actual: Usuario) -> None:
        usuario = self.buscar_usuario(id_usuario)
        if usuario is None:
            raise ValueError("No existe un usuario con ese identificador.")
        if usuario.id_usuario == usuario_actual.id_usuario:
            raise ValueError("No puede eliminar la cuenta que está usando actualmente.")
        self._validar_permiso_usuario(usuario_actual, usuario_objetivo=usuario)

        usuarios_actualizados = [
            item for item in self._usuarios if item.id_usuario != int(id_usuario)
        ]
        if not self._archivo_servicio.guardar_usuarios(usuarios_actualizados):
            raise OSError("No se pudo eliminar el usuario de usuarios.json.")
        self._usuarios = usuarios_actualizados

    def cantidad_productos(self) -> int:
        return len(self._productos)

    def cantidad_usuarios(self) -> int:
        return len(self._usuarios)

    def listar_ventas(self) -> List[Venta]:
        return list(self._ventas)

    def registrar_venta(self, usuario_id: int, producto_id: int) -> Venta:
        usuario = next(
            (item for item in self._usuarios if item.id_usuario == int(usuario_id)),
            None,
        )
        if usuario is None:
            raise ValueError("Seleccione un usuario registrado.")

        producto = self.buscar_producto(producto_id)
        if producto is None:
            raise ValueError("Seleccione un producto registrado.")

        venta = Venta(usuario.id_usuario, producto.id_producto)
        ventas_actualizadas = [*self._ventas, venta]
        if not self._archivo_servicio.guardar_ventas(ventas_actualizadas):
            raise OSError("No se pudo guardar la venta en ventas.json.")
        self._ventas = ventas_actualizadas
        return venta

    def generar_reporte_ventas(self, ruta_archivo: str) -> str:
        valor_ruta = ruta_archivo.strip()
        if not valor_ruta:
            raise ValueError("Seleccione dónde guardar el reporte PDF.")
        destino = Path(valor_ruta).expanduser()
        if destino.suffix.casefold() != ".pdf":
            destino = Path(f"{destino}.pdf")

        usuarios = {usuario.id_usuario: usuario for usuario in self._usuarios}
        productos = {producto.id_producto: producto for producto in self._productos}
        estilos = getSampleStyleSheet()
        filas = [["Venta", "Usuario", "Producto", "Fecha y hora"]]
        for consecutivo, venta in enumerate(self._ventas, start=1):
            usuario = usuarios.get(venta.usuario_id)
            producto = productos.get(venta.producto_id)
            nombre_usuario = (
                f"{usuario.nombre} {usuario.apellido} (@{usuario.nombre_usuario})"
                if usuario
                else f"Usuario {venta.usuario_id}"
            )
            nombre_producto = producto.nombre if producto else f"Producto {venta.producto_id}"
            filas.append(
                [
                    f"V{consecutivo:03d}",
                    Paragraph(escape(nombre_usuario), estilos["BodyText"]),
                    Paragraph(escape(nombre_producto), estilos["BodyText"]),
                    venta.fecha.replace("T", " "),
                ]
            )

        if not self._ventas:
            filas.append(["", "", "No hay ventas registradas.", ""])

        tabla = Table(filas, colWidths=(0.75 * inch, 2.2 * inch, 2.5 * inch, 1.75 * inch), repeatRows=1)
        tabla.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#183D34")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#D9E2DC")),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), (colors.white, colors.HexColor("#F3F6F2"))),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 8),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                    ("TOPPADDING", (0, 0), (-1, -1), 8),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ]
            )
        )
        documento = SimpleDocTemplate(
            str(destino),
            pagesize=landscape(letter),
            rightMargin=0.5 * inch,
            leftMargin=0.5 * inch,
            topMargin=0.55 * inch,
            bottomMargin=0.5 * inch,
        )
        contenido = [
            Paragraph("Reporte de ventas · Sistema Restaurante", estilos["Title"]),
            Spacer(1, 0.18 * inch),
            Paragraph(f"Ventas registradas: {len(self._ventas)}", estilos["BodyText"]),
            Spacer(1, 0.18 * inch),
            tabla,
        ]
        destino.parent.mkdir(parents=True, exist_ok=True)
        documento.build(contenido)
        return str(destino.resolve())
