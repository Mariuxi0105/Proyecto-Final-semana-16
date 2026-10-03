import json
from pathlib import Path
from typing import Any, Dict, List

from modelos.producto import Producto
from modelos.usuario import Usuario
from modelos.venta import Venta


class ArchivoServicio:
    """Capa de acceso a datos para los archivos JSON del proyecto."""

    _DIRECTORIO_DATOS = Path(__file__).resolve().parent.parent / "datos"
    _UBICACION_PRODUCTOS = _DIRECTORIO_DATOS / "productos.json"
    _UBICACION_USUARIOS = _DIRECTORIO_DATOS / "usuarios.json"
    _UBICACION_VENTAS = _DIRECTORIO_DATOS / "ventas.json"

    @staticmethod
    def _crear_directorio(ruta_archivo: Path) -> None:
        ruta_archivo.parent.mkdir(parents=True, exist_ok=True)

    @classmethod
    def guardar_productos(cls, inventario: List[Producto]) -> bool:
        try:
            cls._crear_directorio(cls._UBICACION_PRODUCTOS)
            esquema_json: List[Dict[str, Any]] = [item.to_dict() for item in inventario]
            with cls._UBICACION_PRODUCTOS.open("w", encoding="utf-8") as flujo_archivo:
                json.dump(esquema_json, flujo_archivo, indent=4, ensure_ascii=False)
            return True
        except PermissionError:
            print(f"\n[Fallo de Sistema] Permiso denegado al escribir en '{cls._UBICACION_PRODUCTOS}'.")
            return False
        except OSError as error_sistema:
            print(f"\n[Fallo de Disco] Error físico de entrada/salida: {error_sistema}")
            return False

    @classmethod
    def cargar_productos(cls) -> List[Producto]:
        if not cls._UBICACION_PRODUCTOS.exists():
            return []

        try:
            with cls._UBICACION_PRODUCTOS.open("r", encoding="utf-8") as flujo_archivo:
                coleccion_plana = json.load(flujo_archivo)

            if not isinstance(coleccion_plana, list):
                raise json.JSONDecodeError(
                    "El formato del JSON raíz es incorrecto (debe ser una lista).",
                    "",
                    0,
                )

            productos_procesados: List[Producto] = []
            for posicion, elemento in enumerate(coleccion_plana):
                try:
                    productos_procesados.append(Producto.from_dict(elemento))
                except (KeyError, ValueError) as error_interno:
                    print(
                        f"\n[Aviso Operativo] Ignorando producto corrupto en posición {posicion + 1}: {error_interno}"
                    )
                    continue
            return productos_procesados
        except json.JSONDecodeError as error_json:
            print(f"\n[Alerta Estructural] El archivo '{cls._UBICACION_PRODUCTOS}' no posee un formato JSON válido: {error_json}")
            print("Iniciando la aplicación con un inventario vacío temporalmente.")
            return []
        except PermissionError:
            print(f"\n[Fallo de Sistema] No se poseen permisos de lectura para '{cls._UBICACION_PRODUCTOS}'.")
            return []

    @classmethod
    def guardar_usuarios(cls, usuarios: List[Usuario]) -> bool:
        try:
            cls._crear_directorio(cls._UBICACION_USUARIOS)
            esquema_json: List[Dict[str, Any]] = [item.to_dict() for item in usuarios]
            with cls._UBICACION_USUARIOS.open("w", encoding="utf-8") as flujo_archivo:
                json.dump(esquema_json, flujo_archivo, indent=4, ensure_ascii=False)
            return True
        except PermissionError:
            print(f"\n[Fallo de Sistema] Permiso denegado al escribir en '{cls._UBICACION_USUARIOS}'.")
            return False
        except OSError as error_sistema:
            print(f"\n[Fallo de Disco] Error físico de entrada/salida: {error_sistema}")
            return False

    @classmethod
    def cargar_usuarios(cls) -> List[Usuario]:
        if not cls._UBICACION_USUARIOS.exists():
            return []

        try:
            with cls._UBICACION_USUARIOS.open("r", encoding="utf-8") as flujo_archivo:
                coleccion_plana = json.load(flujo_archivo)

            if not isinstance(coleccion_plana, list):
                raise json.JSONDecodeError(
                    "El formato del JSON raíz es incorrecto (debe ser una lista).",
                    "",
                    0,
                )

            usuarios_procesados: List[Usuario] = []
            for posicion, elemento in enumerate(coleccion_plana):
                try:
                    usuarios_procesados.append(Usuario.from_dict(elemento))
                except (KeyError, ValueError) as error_interno:
                    print(
                        f"\n[Aviso Operativo] Ignorando usuario corrupto en posición {posicion + 1}: {error_interno}"
                    )
                    continue
            return usuarios_procesados
        except json.JSONDecodeError as error_json:
            print(f"\n[Alerta Estructural] El archivo '{cls._UBICACION_USUARIOS}' no posee un formato JSON válido: {error_json}")
            print("Iniciando la aplicación con una lista de usuarios vacía temporalmente.")
            return []
        except PermissionError:
            print(f"\n[Fallo de Sistema] No se poseen permisos de lectura para '{cls._UBICACION_USUARIOS}'.")
            return []

    @classmethod
    def guardar_ventas(cls, ventas: List[Venta]) -> bool:
        try:
            cls._crear_directorio(cls._UBICACION_VENTAS)
            esquema_json = [venta.to_dict() for venta in ventas]
            with cls._UBICACION_VENTAS.open("w", encoding="utf-8") as flujo_archivo:
                json.dump(esquema_json, flujo_archivo, indent=4, ensure_ascii=False)
            return True
        except (PermissionError, OSError) as error_sistema:
            print(f"\n[Fallo de Disco] No se pudieron guardar las ventas: {error_sistema}")
            return False

    @classmethod
    def cargar_ventas(cls) -> List[Venta]:
        if not cls._UBICACION_VENTAS.exists():
            return []

        try:
            with cls._UBICACION_VENTAS.open("r", encoding="utf-8") as flujo_archivo:
                coleccion_plana = json.load(flujo_archivo)
            if not isinstance(coleccion_plana, list):
                raise json.JSONDecodeError("La raíz debe ser una lista.", "", 0)

            ventas_procesadas: List[Venta] = []
            for posicion, elemento in enumerate(coleccion_plana):
                try:
                    ventas_procesadas.append(Venta.from_dict(elemento))
                except (KeyError, TypeError, ValueError) as error_interno:
                    print(f"\n[Aviso Operativo] Ignorando venta corrupta en posición {posicion + 1}: {error_interno}")
            return ventas_procesadas
        except json.JSONDecodeError as error_json:
            print(f"\n[Alerta Estructural] El archivo '{cls._UBICACION_VENTAS}' no posee JSON válido: {error_json}")
            return []
        except PermissionError:
            print(f"\n[Fallo de Sistema] No se poseen permisos de lectura para '{cls._UBICACION_VENTAS}'.")
            return []