from tkinter import ttk


VERDE = "#183D34"
VERDE_CLARO = "#E6EEE8"
TERRACOTA = "#B6533D"
FONDO = "#F3F6F2"
PANEL = "#FFFFFF"
TEXTO = "#24362F"
TEXTO_SUAVE = "#6A7B73"
BORDE = "#D9E2DC"


def configurar_estilos(master: ttk.Widget) -> None:
    estilos = ttk.Style(master)
    if "clam" in estilos.theme_names():
        estilos.theme_use("clam")

    estilos.configure(".", font=("Segoe UI", 10))
    estilos.configure("TFrame", background=FONDO)
    estilos.configure("TLabel", background=FONDO, foreground=TEXTO)
    estilos.configure(
        "TButton",
        background=VERDE_CLARO,
        foreground=VERDE,
        padding=(12, 8),
        borderwidth=0,
        focusthickness=0,
    )
    estilos.map(
        "TButton",
        background=[("pressed", "#D4E1D8"), ("active", "#DCE8E0")],
    )
    estilos.configure("TEntry", padding=(9, 8), fieldbackground=PANEL, foreground=TEXTO)
    estilos.configure("TSeparator", background=BORDE)

    estilos.configure("App.TFrame", background=FONDO)
    estilos.configure("Header.TFrame", background=PANEL)
    estilos.configure("HeaderTitle.TLabel", background=PANEL, foreground=VERDE, font=("Segoe UI", 20, "bold"))
    estilos.configure("HeaderMeta.TLabel", background=PANEL, foreground=TEXTO_SUAVE)
    estilos.configure("HeaderLogo.TLabel", background=PANEL)
    estilos.configure("Header.TButton", background=PANEL, foreground=VERDE, padding=(10, 7))
    estilos.map("Header.TButton", background=[("active", VERDE_CLARO)])

    estilos.configure("Sidebar.TFrame", background=VERDE)
    estilos.configure("SidebarHeading.TLabel", background=VERDE, foreground="#B8CEC3", font=("Segoe UI", 9, "bold"))
    estilos.configure("Nav.TButton", background=VERDE, foreground="#F3F6F2", anchor="w", padding=(14, 11))
    estilos.map("Nav.TButton", background=[("active", "#2B5549")], foreground=[("active", "#FFFFFF")])
    estilos.configure("NavActive.TButton", background=TERRACOTA, foreground="#FFFFFF", anchor="w", padding=(14, 11))
    estilos.map("NavActive.TButton", background=[("active", "#A74734")])

    estilos.configure("PageTitle.TLabel", background=FONDO, foreground=VERDE, font=("Segoe UI", 18, "bold"))
    estilos.configure("StatValue.TLabel", background=PANEL, foreground=VERDE, font=("Segoe UI", 24, "bold"))
    estilos.configure("Muted.TLabel", background=FONDO, foreground=TEXTO_SUAVE)
    estilos.configure("Panel.TLabelframe", background=PANEL, bordercolor=BORDE, borderwidth=1, relief="solid")
    estilos.configure("Panel.TLabelframe.Label", background=PANEL, foreground=VERDE, font=("Segoe UI", 10, "bold"))
    estilos.configure("Panel.TFrame", background=PANEL)
    estilos.configure("Primary.TButton", background=TERRACOTA, foreground="#FFFFFF", font=("Segoe UI", 10, "bold"))
    estilos.map("Primary.TButton", background=[("pressed", "#963F2F"), ("active", "#A74734")], foreground=[("active", "#FFFFFF")])
    estilos.configure("Danger.TButton", background="#F5E7E3", foreground="#983F32")
    estilos.map("Danger.TButton", background=[("active", "#EED4CD")])
    estilos.configure("Table.Treeview", background=PANEL, fieldbackground=PANEL, foreground=TEXTO, rowheight=31)
    estilos.map("Table.Treeview", background=[("selected", VERDE)], foreground=[("selected", "#FFFFFF")])
    estilos.configure("Table.Treeview.Heading", background=VERDE_CLARO, foreground=VERDE, font=("Segoe UI", 9, "bold"), padding=(8, 8))
    estilos.map("Table.Treeview.Heading", background=[("active", "#D8E5DC")])

    estilos.configure("LoginHero.TFrame", background=VERDE)
    estilos.configure("LoginLogo.TLabel", background=VERDE)
    estilos.configure("LoginBrand.TLabel", background=VERDE, foreground="#FFFFFF", font=("Segoe UI", 31, "bold"))
    estilos.configure("LoginKicker.TLabel", background=VERDE, foreground="#B8CEC3", font=("Segoe UI", 9, "bold"))
    estilos.configure("LoginHeroCopy.TLabel", background=VERDE, foreground="#D6E3DC", font=("Segoe UI", 12))
    estilos.configure("LoginForm.TFrame", background=PANEL)
    estilos.configure("LoginTitle.TLabel", background=PANEL, foreground=VERDE, font=("Segoe UI", 24, "bold"))
    estilos.configure("LoginSubtitle.TLabel", background=PANEL, foreground=TEXTO_SUAVE)
    estilos.configure("LoginFormKicker.TLabel", background=PANEL, foreground=TERRACOTA, font=("Segoe UI", 9, "bold"))
    estilos.configure("LoginField.TLabel", background=PANEL, foreground=TEXTO, font=("Segoe UI", 10, "bold"))
    estilos.configure("LoginHint.TLabel", background=PANEL, foreground=TEXTO_SUAVE, font=("Segoe UI", 9))
    estilos.configure("Panel.TLabel", background=PANEL, foreground=TEXTO)