import customtkinter as ctk
from tkinter import messagebox
from logica.login_logica import LoginLogica


class LoginView(ctk.CTkFrame):
    """
    Vista de inicio de sesión de AutoWash System.
    Diseño fiel al prototipo React adaptado para escritorio:
    - Fondo: #0B4F66 (azul océano).
    - Tarjeta centrada: bg #D9D9D9, esquinas muy redondeadas, borde negro.
    - Campos blancos semitransparentes, anillo de foco #F79D4F.
    - Botón INGRESAR: #F79D4F con hover más intenso.
    """

    def __init__(self, parent, al_ingresar=None):
        super().__init__(parent, fg_color="#0B4F66")
        self.al_ingresar = al_ingresar
        self.pack(fill="both", expand=True)
        self._construir_interfaz()

    def _construir_interfaz(self):
        # ------------------------------------------------------------------ #
        # TARJETA PRINCIPAL — ancho generoso para escritorio                  #
        # ------------------------------------------------------------------ #
        self.card = ctk.CTkFrame(
            self,
            width=440,
            height=470,
            fg_color="#D9D9D9",
            corner_radius=36,
            border_color="#000000",
            border_width=1
        )
        self.card.place(relx=0.5, rely=0.5, anchor="center")
        self.card.pack_propagate(False)

        # Contenedor interno con paddings verticales amplios
        inner = ctk.CTkFrame(self.card, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=36, pady=32)

        # ------------------------------------------------------------------ #
        # ENCABEZADO                                                           #
        # ------------------------------------------------------------------ #
        lbl_titulo = ctk.CTkLabel(
            inner,
            text="INICIAR SESIÓN",
            font=("Segoe UI", 24),
            text_color="#000000",
            anchor="center"
        )
        lbl_titulo.pack(fill="x")

        lbl_sub = ctk.CTkLabel(
            inner,
            text="acceso solo para personal autorizado",
            font=("Segoe UI", 12),
            text_color="#888888",
            anchor="center"
        )
        lbl_sub.pack(fill="x", pady=(6, 0))

        # ------------------------------------------------------------------ #
        # CAMPO: USUARIO                                                       #
        # ------------------------------------------------------------------ #
        lbl_usuario = ctk.CTkLabel(
            inner,
            text="Usuario",
            font=("Segoe UI", 12),
            text_color="#000000",
            anchor="w"
        )
        lbl_usuario.pack(fill="x", pady=(22, 0))

        # Contenedor que da el margen lateral interno (equivale al sm:pl/pr de Tailwind)
        cont_usuario = ctk.CTkFrame(inner, fg_color="transparent")
        cont_usuario.pack(fill="x", pady=(6, 0), padx=10)

        self.txt_usuario = ctk.CTkEntry(
            cont_usuario,
            height=40,
            corner_radius=12,
            fg_color="#EFEFEF",
            text_color="#000000",
            border_width=0,
            font=("Segoe UI", 13),
            placeholder_text="Ingrese su usuario",
            placeholder_text_color="#888888"
        )
        self.txt_usuario.pack(fill="x")
        self.txt_usuario.bind("<Return>", lambda _e: self.txt_password.focus_set())
        self.txt_usuario.bind("<FocusIn>", lambda _e: self._resaltar(self.txt_usuario, True))
        self.txt_usuario.bind("<FocusOut>", lambda _e: self._resaltar(self.txt_usuario, False))

        # ------------------------------------------------------------------ #
        # CAMPO: CONTRASEÑA                                                    #
        # ------------------------------------------------------------------ #
        lbl_pass = ctk.CTkLabel(
            inner,
            text="Contraseña",
            font=("Segoe UI", 12),
            text_color="#000000",
            anchor="w"
        )
        lbl_pass.pack(fill="x", pady=(16, 0))

        cont_pass = ctk.CTkFrame(inner, fg_color="transparent")
        cont_pass.pack(fill="x", pady=(6, 0), padx=10)

        # Caja redondeada que contiene el campo + el botón del ojo
        self.caja_pass = ctk.CTkFrame(
            cont_pass,
            height=40,
            corner_radius=12,
            fg_color="#EFEFEF",
            border_width=0
        )
        self.caja_pass.pack(fill="x")
        self.caja_pass.pack_propagate(False)

        self._pass_visible = False

        self.btn_ver_pass = ctk.CTkButton(
            self.caja_pass,
            text="👁",
            width=36,
            height=30,
            corner_radius=8,
            fg_color="transparent",
            hover_color="#DDDDDD",
            text_color="#555555",
            font=("Segoe UI Emoji", 14),
            command=self._alternar_password
        )
        self.btn_ver_pass.pack(side="right", padx=(0, 6))

        self.txt_password = ctk.CTkEntry(
            self.caja_pass,
            height=36,
            corner_radius=12,
            fg_color="transparent",
            text_color="#000000",
            border_width=0,
            show="*",
            font=("Segoe UI", 13),
            placeholder_text="Ingrese su contraseña",
            placeholder_text_color="#888888"
        )
        self.txt_password.pack(side="left", fill="x", expand=True, padx=(4, 0))
        self.txt_password.bind("<Return>", lambda _e: self._validar_login())
        self.txt_password.bind("<FocusIn>", lambda _e: self._resaltar(self.caja_pass, True))
        self.txt_password.bind("<FocusOut>", lambda _e: self._resaltar(self.caja_pass, False))

        # ------------------------------------------------------------------ #
        # MENSAJE DE ERROR INLINE                                              #
        # ------------------------------------------------------------------ #
        self.lbl_error = ctk.CTkLabel(
            inner,
            text="",
            font=("Segoe UI", 11, "bold"),
            text_color="#D32F2F",
            anchor="center"
        )
        self.lbl_error.pack(fill="x", pady=(6, 0))

        # ------------------------------------------------------------------ #
        # BOTÓN INGRESAR                                                       #
        # ------------------------------------------------------------------ #
        cont_btn = ctk.CTkFrame(inner, fg_color="transparent")
        cont_btn.pack(fill="x", pady=(14, 0), padx=50)

        self.btn_ingresar = ctk.CTkButton(
            cont_btn,
            text="INGRESAR",
            height=44,
            corner_radius=12,
            fg_color="#F79D4F",   # 75 % de opacidad simulado con color
            hover_color="#F79D4F",
            text_color="#000000",
            font=("Segoe UI", 14),
            command=self._validar_login
        )
        self.btn_ingresar.pack(fill="x")

        # Foco inicial
        self.after(100, lambda: self.txt_usuario.focus_set())

    # ---------------------------------------------------------------------- #
    # MÉTODOS INTERNOS                                                         #
    # ---------------------------------------------------------------------- #

    def _resaltar(self, widget, activo):
        """Simula el anillo de foco #F79D4F al enfocar/desenfocar un campo."""
        widget.configure(border_width=2 if activo else 0,
                         border_color="#F79D4F" if activo else "transparent")

    def _alternar_password(self):
        """Muestra u oculta la contraseña al pulsar el ojito."""
        self._pass_visible = not self._pass_visible
        if self._pass_visible:
            self.txt_password.configure(show="")
            self.btn_ver_pass.configure(text="🙈")
        else:
            self.txt_password.configure(show="*")
            self.btn_ver_pass.configure(text="👁")
        self.txt_password.focus_set()

    def _validar_login(self):
        """Valida las credenciales llamando a la capa de lógica."""
        usuario = self.txt_usuario.get().strip()
        password = self.txt_password.get().strip()

        self.lbl_error.configure(text="")

        if not usuario or not password:
            self.lbl_error.configure(text="Por favor ingrese usuario y contraseña.")
            return

        try:
            LoginLogica.iniciar_sesion(usuario, password)
            if self.al_ingresar:
                self.al_ingresar()
        except ValueError as e:
            self.lbl_error.configure(text=str(e))
            messagebox.showerror("Error de Autenticación", str(e))