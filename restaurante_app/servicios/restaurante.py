from typing import List, Optional

from modelos.producto import Producto
from modelos.usuario import Usuario
from modelos.venta import Venta
from servicios.archivo_servicio import ArchivoServicio


class Restaurante:
    def __init__(self) -> None:
        self._catalogo_productos: List[Producto] = []
        self._sesion_usuarios: List[Usuario] = []
        self._ventas: List[Venta] = []
        self._productos_por_id: dict[int, Producto] = {}
        self._usuarios_por_id: dict[int, Usuario] = {}
        self._ventas_por_usuario: dict[int, List[Venta]] = {}

    def _reconstruir_indices(self) -> None:
        self._productos_por_id = {
            producto.id_producto: producto for producto in self._catalogo_productos
        }
        self._usuarios_por_id = {
            usuario.id_usuario: usuario for usuario in self._sesion_usuarios
        }
        self._ventas_por_usuario = {}
        for venta in self._ventas:
            self._ventas_por_usuario.setdefault(venta.usuario_id, []).append(venta)

    def cargar_datos_iniciales(self) -> None:
        """Carga inicial delegada al subsistema de almacenamiento."""
        self._catalogo_productos = ArchivoServicio.cargar_productos()
        self._sesion_usuarios = ArchivoServicio.cargar_usuarios()
        self._ventas = ArchivoServicio.cargar_ventas()
        self._reconstruir_indices()

    def _actualizar_almacenamiento_productos(self) -> None:
        ArchivoServicio.guardar_productos(self._catalogo_productos)

    def _actualizar_almacenamiento_usuarios(self) -> None:
        ArchivoServicio.guardar_usuarios(self._sesion_usuarios)

    def _actualizar_almacenamiento_ventas(self) -> None:
        ArchivoServicio.guardar_ventas(self._ventas)

    def registrar_producto(self, nombre: str, precio: float, categoria: str, stock: int = 10) -> bool:
        """Genera un nuevo identificador secuencial y añade un registro validado."""
        try:
            codigo_nuevo: int = max([item.id_producto for item in self._catalogo_productos], default=0) + 1
            nuevo_articulo = Producto(codigo_nuevo, nombre, precio, categoria, stock)
            self._catalogo_productos.append(nuevo_articulo)
            self._productos_por_id[codigo_nuevo] = nuevo_articulo

            self._actualizar_almacenamiento_productos()
            print(f"\n[OK] Guardado en disco exitoso: {nuevo_articulo}")
            return True
        except ValueError as error_negocio:
            print(f"\n[Error de Regla] Registro denegado: {error_negocio}")
            return False

    def buscar_producto_por_id(self, codigo_busqueda: int) -> Optional[Producto]:
        return self._productos_por_id.get(codigo_busqueda)

    def actualizar_producto(self, codigo: int, edit_nombre: str, edit_precio: float, edit_categoria: str, stock: Optional[int] = None) -> bool:
        item = self._productos_por_id.get(codigo)
        if item is not None:
            try:
                nuevo_stock = item.stock if stock is None else stock
                Producto(codigo, edit_nombre, edit_precio, edit_categoria, nuevo_stock)

                item.nombre = edit_nombre.strip()
                item.precio = edit_precio
                item.categoria = edit_categoria.strip()
                if stock is not None:
                    item.stock = nuevo_stock

                self._actualizar_almacenamiento_productos()
                print(f"\n[OK] Producto {codigo} modificado correctamente en el archivo JSON.")
                return True
            except ValueError as error_negocio:
                print(f"\n[Error de Regla] Modificación cancelada: {error_negocio}")
                return False

        print(f"\n[Error] El código {codigo} no coincide con ningún producto activo.")
        return False

    def eliminar_producto(self, codigo_eliminar: int) -> bool:
        articulo = self.buscar_producto_por_id(codigo_eliminar)
        if articulo is None:
            print(f"\n[Error] El código {codigo_eliminar} no pertenece al menú.")
            return False

        self._catalogo_productos.remove(articulo)
        del self._productos_por_id[codigo_eliminar]
        self._actualizar_almacenamiento_productos()
        print(f"\n[OK] Registro {codigo_eliminar} eliminado del sistema físico.")
        return True

    def listar_productos(self) -> None:
        if not self._catalogo_productos:
            print("\nEl inventario se encuentra actualmente vacío.")
            return
        print("\n=== MENÚ OPERATIVO DEL RESTAURANTE ===")
        for item in self._catalogo_productos:
            print(item)

    def buscar_usuario(self, identificacion_usuario: int) -> Optional[Usuario]:
        return self._usuarios_por_id.get(identificacion_usuario)

    def registrar_usuario(self, alias: str, rango: str) -> bool:
        try:
            siguiente_id = max((usuario.id_usuario for usuario in self._sesion_usuarios), default=0) + 1
            usuario_sistema = Usuario(siguiente_id, alias, rango)
            self._sesion_usuarios.append(usuario_sistema)
            self._usuarios_por_id[siguiente_id] = usuario_sistema
            self._actualizar_almacenamiento_usuarios()
            print(f"\n[OK] {usuario_sistema} añadido a la sesión y persistido.")
            return True
        except ValueError as error_negocio:
            print(f"\n[Error de Regla] Registro de usuario denegado: {error_negocio}")
            return False

    def vender_producto(self, codigo_producto: int, identificacion_usuario: int, cantidad: int) -> bool:
        usuario = self.buscar_usuario(identificacion_usuario)
        producto = self.buscar_producto_por_id(codigo_producto)

        if usuario is None or producto is None:
            print("\n[Error] El usuario o el producto no existen en el sistema.")
            return False

        if cantidad <= 0:
            print("\n[Error] La cantidad solicitada debe ser mayor a cero.")
            return False

        if producto.stock < cantidad:
            print("\n[Error] Stock insuficiente para realizar la venta.")
            return False

        venta = Venta(usuario.id_usuario, producto.id_producto, cantidad)
        self._ventas.append(venta)
        self._ventas_por_usuario.setdefault(usuario.id_usuario, []).append(venta)
        producto.vender(cantidad)

        self._actualizar_almacenamiento_ventas()
        self._actualizar_almacenamiento_productos()
        print(f"\n[OK] Venta registrada correctamente: {venta}")
        return True

    def ventas_por_usuario(self, identificacion_usuario: int) -> List[Venta]:
        return list(self._ventas_por_usuario.get(identificacion_usuario, []))

    def consultar_ventas_usuario(self, identificacion_usuario: int) -> List[Venta]:
        return self.ventas_por_usuario(identificacion_usuario)

    def listar_ventas_por_usuario(self, identificacion_usuario: int) -> None:
        ventas_usuario = self.ventas_por_usuario(identificacion_usuario)
        if not ventas_usuario:
            print(f"\nEl usuario con ID {identificacion_usuario} no tiene ventas registradas.")
            return

        print(f"\n=== VENTAS DEL USUARIO {identificacion_usuario} ===")
        for venta in ventas_usuario:
            producto = self.buscar_producto_por_id(venta.producto_codigo)
            nombre_producto = producto.nombre if producto else "Producto no encontrado"
            print(f"- Producto: {nombre_producto} | Cantidad: {venta.cantidad}")