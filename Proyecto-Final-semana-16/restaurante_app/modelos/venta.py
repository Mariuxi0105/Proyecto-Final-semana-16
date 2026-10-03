from datetime import datetime
from typing import Any, Dict, Optional


class Venta:
    def __init__(
        self,
        usuario_id: int,
        producto_id: int,
        fecha: Optional[str] = None,
    ) -> None:
        usuario_id = int(usuario_id)
        producto_id = int(producto_id)

        if usuario_id <= 0:
            raise ValueError("El identificador del usuario debe ser positivo.")
        if producto_id <= 0:
            raise ValueError("El identificador del producto debe ser positivo.")

        fecha = fecha or datetime.now().isoformat(timespec="seconds")
        try:
            datetime.fromisoformat(fecha)
        except (TypeError, ValueError) as error_fecha:
            raise ValueError("La fecha de venta no tiene un formato válido.") from error_fecha

        self.usuario_id: int = usuario_id
        self.producto_id: int = producto_id
        self.fecha: str = fecha

    def to_dict(self) -> Dict[str, Any]:
        return {
            "usuario_id": self.usuario_id,
            "producto_id": self.producto_id,
            "fecha": self.fecha,
        }

    @classmethod
    def from_dict(cls, datos: Dict[str, Any]) -> "Venta":
        if "usuario_id" not in datos:
            raise KeyError("usuario_id")
        if "producto_id" not in datos and "producto_codigo" not in datos:
            raise KeyError("producto_id")
        return cls(
            usuario_id=int(datos["usuario_id"]),
            producto_id=int(datos.get("producto_id", datos.get("producto_codigo"))),
            fecha=datos.get("fecha"),
        )

    def __str__(self) -> str:
        return f"Venta: Usuario {self.usuario_id} | Producto {self.producto_id} | Fecha: {self.fecha}"
