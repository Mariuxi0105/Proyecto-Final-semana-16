import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from modelos.producto import Producto
from modelos.usuario import Usuario
from modelos.venta import Venta
from servicios.archivo_servicio import ArchivoServicio
from servicios.restaurante_servicio import RestauranteServicio


class ArchivoMemoria:
    usuarios: list[Usuario] = []
    productos: list[Producto] = []
    ventas: list[Venta] = []

    @classmethod
    def cargar_productos(cls):
        return list(cls.productos)

    @classmethod
    def cargar_usuarios(cls):
        return list(cls.usuarios)

    @classmethod
    def cargar_ventas(cls):
        return list(cls.ventas)

    @classmethod
    def guardar_usuarios(cls, usuarios):
        cls.usuarios = list(usuarios)
        return True

    @classmethod
    def guardar_productos(cls, productos):
        cls.productos = list(productos)
        return True

    @classmethod
    def guardar_ventas(cls, ventas):
        cls.ventas = list(ventas)
        return True


class GestionUsuariosTests(unittest.TestCase):
    def setUp(self):
        self.admin = Usuario(
            1, "Ada", "Admin", "admin", "secreto", "ada@example.com", "1980-01-01",
            rol="Administrador",
        )
        self.empleado = Usuario(
            2, "Eva", "Caja", "cajera", "secreto", "eva@example.com", "1990-01-01",
            rol="Empleado",
        )
        self.cliente = Usuario(
            3, "Leo", "Cliente", "leo", "secreto", "leo@example.com", "2000-01-01",
            rol="Cliente",
        )
        ArchivoMemoria.usuarios = [self.admin, self.empleado, self.cliente]
        ArchivoMemoria.productos = []
        ArchivoMemoria.ventas = []
        self.servicio = RestauranteServicio(ArchivoMemoria)
        self.servicio.cargar_datos()

    def test_solo_personal_puede_iniciar_sesion(self):
        self.assertIsNotNone(self.servicio.validar_acceso("admin", "secreto"))
        self.assertIsNotNone(self.servicio.validar_acceso("cajera", "secreto"))
        self.assertIsNone(self.servicio.validar_acceso("leo", "secreto"))

    def test_empleado_solo_lista_y_registra_clientes(self):
        self.assertEqual(
            [u.id_usuario for u in self.servicio.usuarios_permitidos_para(self.empleado)],
            [self.cliente.id_usuario],
        )
        nuevo = self.servicio.registrar_usuario(
            "Mia", "Cliente", "mia", "clave", "mia@example.com", "2001-02-03",
            rol="Cliente", usuario_actual=self.empleado,
        )
        self.assertEqual(nuevo.rol, "Cliente")
        actualizado = self.servicio.actualizar_usuario(
            nuevo.id_usuario,
            "Mia", "Cliente", "mia", "clave-actualizada", "mia@example.com",
            "2001-02-03", rol="Cliente", usuario_actual=self.empleado,
        )
        self.assertEqual(actualizado.contrasena, "clave-actualizada")
        self.servicio.eliminar_usuario(
            actualizado.id_usuario, usuario_actual=self.empleado
        )
        self.assertIsNone(self.servicio.buscar_usuario(actualizado.id_usuario))
        with self.assertRaisesRegex(ValueError, "solo puede registrar"):
            self.servicio.registrar_usuario(
                "No", "Empleado", "no", "clave", "no@example.com", "2001-02-03",
                rol="Empleado", usuario_actual=self.empleado,
            )

    def test_empleado_no_puede_actualizar_ni_eliminar_personal(self):
        otro_empleado = Usuario(
            4, "Nora", "Cocina", "nora", "secreto", "nora@example.com", "1992-01-01",
            rol="Empleado",
        )
        self.servicio._usuarios.append(otro_empleado)
        with self.assertRaisesRegex(ValueError, "solo puede gestionar"):
            self.servicio.actualizar_usuario(
                otro_empleado.id_usuario,
                "Nora", "Cocina", "nora", "secreto", "nora@example.com", "1992-01-01",
                rol="Empleado", usuario_actual=self.empleado,
            )
        with self.assertRaisesRegex(ValueError, "solo puede gestionar"):
            self.servicio.eliminar_usuario(
                otro_empleado.id_usuario, usuario_actual=self.empleado
            )

    def test_administrador_gestiona_personal_y_clientes(self):
        nuevo_empleado = self.servicio.registrar_usuario(
            "Noa", "Mesera", "noa", "clave", "noa@example.com", "1998-05-06",
            rol="Empleado", usuario_actual=self.admin,
        )
        self.assertEqual(nuevo_empleado.rol, "Empleado")
        actualizada = self.servicio.actualizar_usuario(
            self.empleado.id_usuario,
            "Eva", "Caja", "cajera", "nueva", "eva@example.com", "1990-01-01",
            rol="Empleado", usuario_actual=self.admin,
        )
        self.assertEqual(actualizada.contrasena, "nueva")
        self.servicio.eliminar_usuario(
            self.cliente.id_usuario, usuario_actual=self.admin
        )
        self.assertIsNone(self.servicio.buscar_usuario(self.cliente.id_usuario))
        self.assertIsNotNone(self.servicio.buscar_usuario(nuevo_empleado.id_usuario))
        self.assertIn(actualizada, ArchivoMemoria.usuarios)

    def test_no_se_puede_modificar_o_eliminar_la_cuenta_activa(self):
        with self.assertRaisesRegex(ValueError, "cuenta que está usando"):
            self.servicio.actualizar_usuario(
                self.admin.id_usuario,
                "Ada", "Admin", "admin", "secreto", "ada@example.com", "1980-01-01",
                rol="Administrador", usuario_actual=self.admin,
            )
        with self.assertRaisesRegex(ValueError, "cuenta que está usando"):
            self.servicio.eliminar_usuario(
                self.admin.id_usuario, usuario_actual=self.admin
            )

    def test_cliente_no_puede_gestionar_cuentas_aunque_llame_al_servicio(self):
        with self.assertRaisesRegex(ValueError, "Solo el administrador"):
            self.servicio.registrar_usuario(
                "Alguien", "Cliente", "alguien", "clave", "alguien@example.com",
                "2001-02-03", rol="Cliente", usuario_actual=self.cliente,
            )
        with self.assertRaisesRegex(ValueError, "no tienen acceso"):
            self.servicio.usuarios_permitidos_para(self.cliente)

    def test_productos_ventas_y_recarga_conservan_persistencia(self):
        producto = self.servicio.registrar_producto(
            1, "Sopa", 4.5, "Entrada", 8
        )
        self.servicio.actualizar_producto(
            producto.id_producto, "Sopa del día", 5.0, "Entrada", 7
        )
        venta = self.servicio.registrar_venta(
            self.cliente.id_usuario, producto.id_producto
        )
        self.assertEqual(venta.usuario_id, self.cliente.id_usuario)
        self.assertEqual(venta.producto_id, producto.id_producto)

        servicio_recargado = RestauranteServicio(ArchivoMemoria)
        servicio_recargado.cargar_datos()
        self.assertEqual(
            servicio_recargado.buscar_producto(producto.id_producto).nombre,
            "Sopa del día",
        )
        self.assertEqual(len(servicio_recargado.listar_ventas()), 1)
        servicio_recargado.eliminar_producto(producto.id_producto)
        self.assertIsNone(servicio_recargado.buscar_producto(producto.id_producto))

    def test_archivos_json_se_recargan_al_iniciar_otro_servicio(self):
        with TemporaryDirectory() as directorio:
            rutas = {
                "_UBICACION_PRODUCTOS": Path(directorio) / "productos.json",
                "_UBICACION_USUARIOS": Path(directorio) / "usuarios.json",
                "_UBICACION_VENTAS": Path(directorio) / "ventas.json",
            }
            with (
                patch.multiple(ArchivoServicio, **rutas),
            ):
                ArchivoServicio.guardar_usuarios([self.admin])
                servicio = RestauranteServicio(ArchivoServicio)
                servicio.cargar_datos()
                producto = servicio.registrar_producto(
                    1, "Arroz", 3.25, "Plato principal", 5
                )
                cliente = servicio.registrar_usuario(
                    "Luis", "Pérez", "luis", "clave", "luis@example.com",
                    "2000-04-05", rol="Cliente", usuario_actual=self.admin,
                )
                servicio.registrar_venta(cliente.id_usuario, producto.id_producto)

                servicio_recargado = RestauranteServicio(ArchivoServicio)
                servicio_recargado.cargar_datos()
                self.assertEqual(
                    servicio_recargado.buscar_usuario(cliente.id_usuario).nombre,
                    "Luis",
                )
                self.assertEqual(
                    servicio_recargado.buscar_producto(producto.id_producto).nombre,
                    "Arroz",
                )
                self.assertEqual(len(servicio_recargado.listar_ventas()), 1)

    def test_reporte_pdf_se_crea_en_la_ruta_seleccionada(self):
        with TemporaryDirectory() as directorio:
            ruta = Path(directorio) / "reportes" / "ventas"
            ruta_pdf = Path(self.servicio.generar_reporte_ventas(str(ruta)))

            self.assertEqual(ruta_pdf.name, "ventas.pdf")
            self.assertTrue(ruta_pdf.is_file())
            self.assertTrue(ruta_pdf.read_bytes().startswith(b"%PDF"))


if __name__ == "__main__":
    unittest.main()
