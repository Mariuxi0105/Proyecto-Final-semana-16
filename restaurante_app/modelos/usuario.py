from datetime import datetime
from typing import Any, Dict


class Usuario:
    @staticmethod
    def _normalizar_rol(valor_rol: str | None) -> str:
        valor = str(valor_rol or "Cliente").strip()
        if not valor:
            return "Cliente"
        equivalencia = {
            "administrador": "Administrador",
            "admin": "Administrador",
            "empleado": "Empleado",
            "cajero": "Empleado",
            "cocina": "Empleado",
            "mesero": "Empleado",
            "mesera": "Empleado",
            "cliente": "Cliente",
        }
        return equivalencia.get(valor.casefold(), valor)

    def __init__(
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
    ) -> None:
        id_usuario = int(id_usuario)

        if id_usuario <= 0:
            raise ValueError("El ID de usuario debe ser un entero positivo.")
        if not nombre or not nombre.strip():
            raise ValueError("El nombre del usuario no puede estar vacío.")
        if not apellido or not apellido.strip():
            raise ValueError("El apellido del usuario no puede estar vacío.")
        if not nombre_usuario or not nombre_usuario.strip():
            raise ValueError("El nombre de usuario no puede estar vacío.")
        if not contrasena or not contrasena.strip():
            raise ValueError("La contraseña no puede estar vacía.")
        if not correo_electronico or not correo_electronico.strip() or "@" not in correo_electronico:
            raise ValueError("El correo electrónico no es válido.")
        try:
            datetime.strptime(fecha_nacimiento, "%Y-%m-%d")
        except (TypeError, ValueError) as error_fecha:
            raise ValueError("La fecha de nacimiento debe usar el formato AAAA-MM-DD.") from error_fecha

        valor_rol = (rol if rol is not None else rango) if (rol is not None or rango is not None) else "Cliente"
        valor_rol = self._normalizar_rol(valor_rol)
        if not valor_rol or not valor_rol.strip():
            raise ValueError("El rol del usuario no puede estar vacío.")

        self.id_usuario: int = id_usuario
        self.nombre: str = nombre.strip()
        self.apellido: str = apellido.strip()
        self.nombre_usuario: str = nombre_usuario.strip()
        self.contrasena: str = contrasena.strip()
        self.correo_electronico: str = correo_electronico.strip()
        self.fecha_nacimiento: str = fecha_nacimiento
        self.rol: str = valor_rol.strip()
        self.rango: str = self.rol

    @property
    def es_administrador(self) -> bool:
        return self.rol == "Administrador"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id_usuario": self.id_usuario,
            "nombre": self.nombre,
            "apellido": self.apellido,
            "nombre_usuario": self.nombre_usuario,
            "contrasena": self.contrasena,
            "correo_electronico": self.correo_electronico,
            "fecha_nacimiento": self.fecha_nacimiento,
            "rol": self.rol,
            "rango": self.rango,
        }

    @classmethod
    def from_dict(cls, datos: Dict[str, Any]) -> "Usuario":
        rol = datos.get("rol", datos.get("rango", "Cliente"))
        for llave in [
            "id_usuario",
            "nombre",
            "apellido",
            "nombre_usuario",
            "contrasena",
            "correo_electronico",
            "fecha_nacimiento",
        ]:
            if llave not in datos:
                raise KeyError(llave)
        return cls(
            id_usuario=int(datos["id_usuario"]),
            nombre=str(datos["nombre"]),
            apellido=str(datos["apellido"]),
            nombre_usuario=str(datos["nombre_usuario"]),
            contrasena=str(datos["contrasena"]),
            correo_electronico=str(datos["correo_electronico"]),
            fecha_nacimiento=str(datos["fecha_nacimiento"]),
            rol=str(rol),
        )

    def __str__(self) -> str:
        return f"ID: {self.id_usuario} | Nombre: {self.nombre} {self.apellido} | Usuario: {self.nombre_usuario} | Rol: {self.rol}"