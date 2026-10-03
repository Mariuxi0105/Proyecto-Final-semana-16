import tkinter as tk
from pathlib import Path
from typing import Optional

from PIL import Image, ImageChops, ImageTk


RUTA_ASSETS = Path(__file__).resolve().parent.parent / "assets"


def cargar_logo(
    master: tk.Misc,
    dimension_maxima: int,
    foreground: str,
    background: Optional[str] = None,
) -> tk.Image:
    rutas_png = (
        RUTA_ASSETS / "logo_restaurante.png",
        RUTA_ASSETS / "logo-restaurante.png",
        RUTA_ASSETS / "logo_restaurante.jpg",
        RUTA_ASSETS / "logo-restaurante.jpg",
        RUTA_ASSETS / "logo_restaurante.jpeg",
        RUTA_ASSETS / "logo-restaurante.jpeg",
    )
    ruta_png = next((ruta for ruta in rutas_png if ruta.is_file()), None)
    if ruta_png is not None:
        with Image.open(ruta_png) as imagen_original:
            imagen = imagen_original.convert("RGB")
        fondo = Image.new("RGB", imagen.size, "white")
        diferencia = ImageChops.difference(imagen, fondo).convert("L")
        limites = diferencia.point(lambda pixel: 255 if pixel > 18 else 0).getbbox()
        if limites:
            imagen = imagen.crop(limites)
        imagen.thumbnail(
            (dimension_maxima, dimension_maxima), Image.Resampling.LANCZOS
        )
        return ImageTk.PhotoImage(imagen, master=master)

    opciones = {
        "master": master,
        "file": str(RUTA_ASSETS / "logo_restaurante.xbm"),
        "foreground": foreground,
    }
    if background:
        opciones["background"] = background
    return tk.BitmapImage(**opciones)