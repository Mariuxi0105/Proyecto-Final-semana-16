from typing import Any, Dict


class Producto:
    def __init__(self, id_producto: int, nombre: str, precio: float, categoria: str, stock: int = 10) -> None:
        id_producto = int(id_producto)
        stock = int(stock)
        precio = float(precio)

        if id_producto <= 0:
            raise ValueError("El ID del producto debe ser un entero positivo.")
        if not nombre or not nombre.strip():
            raise ValueError("El nombre del producto no puede estar vacío.")
        if precio <= 0:
            raise ValueError("El precio debe ser un número mayor a cero.")
        if stock < 0:
            raise ValueError("El stock no puede ser negativo.")

        self.id_producto: int = id_producto
        self.id: int = id_producto
        self.nombre: str = nombre.strip()
        self.precio: float = precio
        self.categoria: str = categoria.strip()
        self.stock: int = stock

    def vender(self, cantidad: int) -> None:
        """Disminuye el stock disponible tras validar suficiencia."""
        if cantidad <= 0:
            raise ValueError("La cantidad a vender debe ser mayor a cero.")
        if self.stock < cantidad:
            raise ValueError("Stock insuficiente para realizar la venta.")
        self.stock -= cantidad

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id_producto,
            "id_producto": self.id_producto,
            "nombre": self.nombre,
            "precio": self.precio,
            "categoria": self.categoria,
            "stock": self.stock,
        }

    @classmethod
    def desde_diccionario(cls, datos: Dict[str, Any]) -> "Producto":
        """Método compatible para UI y servicios."""
        return cls(
            id_producto=int(datos.get("id") or datos.get("id_producto", 1)),
            nombre=str(datos.get("nombre", "")),
            precio=float(datos.get("precio", 0.0)),
            categoria=str(datos.get("categoria", "")),
            stock=int(datos.get("stock", 10)),
        )

    @classmethod
    def from_dict(cls, datos: Dict[str, Any]) -> "Producto":
        """Alias para compatibilidad con el resto del proyecto."""
        return cls.desde_diccionario(datos)

    def __str__(self) -> str:
        return (
            f"ID: {self.id_producto} | {self.nombre} ({self.categoria}) | "
            f"${self.precio:.2f} | Stock: {self.stock}"
        )