import tkinter as tk

from modelos.usuario import Usuario
from servicios.restaurante_servicio import RestauranteServicio
from ui.estilos import configurar_estilos
from ui.login_view import LoginView
from ui.main_view import MainView


def main() -> None:
    raiz = tk.Tk()
    raiz.title("Sistema Restaurante | Gestión del menú")

    ancho_pantalla = raiz.winfo_screenwidth()
    alto_pantalla = raiz.winfo_screenheight()
    ancho_ventana = min(1280, max(640, ancho_pantalla - 40))
    alto_ventana = min(860, max(480, alto_pantalla - 80))
    raiz.geometry(
        f"{ancho_ventana}x{alto_ventana}"
        f"+{max(0, (ancho_pantalla - ancho_ventana) // 2)}"
        f"+{max(0, (alto_pantalla - alto_ventana) // 2)}"
    )
    raiz.minsize(min(980, ancho_ventana), min(640, alto_ventana))
    raiz.configure(background="#F3F6F2")
    configurar_estilos(raiz)

    servicio = RestauranteServicio()
    servicio.cargar_datos()

    def mostrar_login() -> None:
        for widget in raiz.winfo_children():
            widget.destroy()
        LoginView(raiz, servicio, mostrar_panel).pack(fill="both", expand=True)

    def mostrar_panel(usuario: Usuario) -> None:
        for widget in raiz.winfo_children():
            widget.destroy()
        MainView(raiz, servicio, usuario, mostrar_login).pack(fill="both", expand=True)

    mostrar_login()
    raiz.mainloop()


if __name__ == "__main__":
    main()