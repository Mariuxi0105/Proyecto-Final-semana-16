import tkinter as tk
from tkinter import messagebox, ttk
from typing import Callable

from modelos.usuario import Usuario
from servicios.restaurante_servicio import RestauranteServicio
from ui.recursos import cargar_logo


class LoginView(ttk.Frame):
    """Pantalla de acceso simulado."""

    def __init__(
        self,
        master: tk.Misc,
        servicio: RestauranteServicio,
        al_ingresar: Callable[[Usuario], None],
    ) -> None:
        super().__init__(master, padding=0, style="App.TFrame")
        self.servicio = servicio
        self.al_ingresar = al_ingresar
        self.columnconfigure(0, weight=1, minsize=400)
        self.columnconfigure(1, weight=1, minsize=480)
        self.rowconfigure(0, weight=1)

        identidad = ttk.Frame(self, padding=(54, 50), style="LoginHero.TFrame")
        identidad.grid(row=0, column=0, sticky="nsew")
        identidad.columnconfigure(0, weight=1)
        self.logo_restaurante = cargar_logo(
            master=self,
            dimension_maxima=180,
            foreground="#D6E3DC",
            background="#183D34",
        )
        marca = ttk.Frame(identidad, style="LoginHero.TFrame")
        marca.grid(row=0, column=0, sticky="w", pady=(0, 24))
        ttk.Label(marca, image=self.logo_restaurante, style="LoginLogo.TLabel").pack(
            side="left", padx=(0, 12)
        )
        ttk.Label(
            marca,
            text="SISTEMA DE RESTAURANTE",
            style="LoginKicker.TLabel",
        ).pack(side="left")
        ttk.Label(
            identidad,
            text="Sistema\nRestaurante",
            style="LoginBrand.TLabel",
            justify="left",
        ).grid(row=1, column=0, sticky="w")
        ttk.Label(
            identidad,
            text="Productos y equipo,\norganizados en un solo lugar.",
            style="LoginHeroCopy.TLabel",
            justify="left",
        ).grid(row=2, column=0, sticky="w", pady=(18, 0))

        formulario = ttk.Frame(self, padding=(64, 42), style="LoginForm.TFrame")
        formulario.grid(row=0, column=1, sticky="nsew")
        formulario.columnconfigure(0, weight=1)
        formulario.rowconfigure(0, weight=1)
        campos = ttk.Frame(formulario, style="LoginForm.TFrame")
        campos.grid(row=0, column=0, sticky="")
        campos.columnconfigure(0, weight=1)

        ttk.Label(campos, text="ACCESO", style="LoginFormKicker.TLabel").grid(
            row=0, column=0, sticky="w", pady=(0, 9)
        )
        ttk.Label(campos, text="Iniciar sesión", style="LoginTitle.TLabel").grid(
            row=1, column=0, sticky="w"
        )
        ttk.Label(
            campos,
            text="Ingrese sus credenciales para abrir el panel.",
            style="LoginSubtitle.TLabel",
        ).grid(row=2, column=0, sticky="w", pady=(7, 28))

        ttk.Label(campos, text="Usuario", style="LoginField.TLabel").grid(
            row=3, column=0, sticky="w", pady=(0, 6)
        )
        self.usuario_var = tk.StringVar()
        self.usuario_entry = ttk.Entry(campos, textvariable=self.usuario_var, width=34)
        self.usuario_entry.grid(row=4, column=0, sticky="ew", pady=(0, 18))

        ttk.Label(campos, text="Contraseña", style="LoginField.TLabel").grid(
            row=5, column=0, sticky="w", pady=(0, 6)
        )
        self.contrasena_var = tk.StringVar()
        self.contrasena_entry = ttk.Entry(
            campos, textvariable=self.contrasena_var, show="*", width=34
        )
        self.contrasena_entry.grid(
            row=6, column=0, sticky="ew", pady=(0, 24)
        )
        self.usuario_entry.bind("<Return>", self._manejar_enter)
        self.contrasena_entry.bind("<Return>", self._manejar_enter)

        ttk.Button(
            campos,
            text="Entrar al panel",
            command=self._intentar_ingreso,
            style="Primary.TButton",
        ).grid(row=7, column=0, sticky="ew", ipady=3)
        ttk.Label(
            campos,
            text="Acceso exclusivo para personal autorizado.",
            style="LoginHint.TLabel",
        ).grid(row=8, column=0, sticky="w", pady=(15, 0))
        self.usuario_entry.focus_set()

    def _manejar_enter(self, evento: tk.Event) -> str:
        self._intentar_ingreso()
        return "break"

    def _intentar_ingreso(self) -> None:
        if not self.usuario_var.get().strip() or not self.contrasena_var.get().strip():
            messagebox.showwarning("Datos incompletos", "Ingrese usuario y contraseña.")
            return

        usuario = self.servicio.validar_acceso(
            self.usuario_var.get(), self.contrasena_var.get()
        )
        if usuario is None:
            messagebox.showerror("Acceso denegado", "Las credenciales no son válidas.")
            return
        self.al_ingresar(usuario)
