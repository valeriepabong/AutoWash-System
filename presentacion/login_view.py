import customtkinter as ctk
from tkinter import messagebox
from logica.login_logica import LoginLogica

class LoginView(ctk.CTkFrame):
    def __init__(self, parent, al_ingresar=None):
        super().__init__(parent)
        self.al_ingresar = al_ingresar
        self.pack(fill="both", expand=True)

        self.frame_login = ctk.CTkFrame(self, width=350, height=400)
        self.frame_login.place(relx=0.5, rely=0.5, anchor="center")

        lbl_titulo = ctk.CTkLabel(self.frame_login, text="Iniciar Sesión", font=("Roboto", 22, "bold"))
        lbl_titulo.pack(pady=(30, 20))

        self.txt_usuario = ctk.CTkEntry(self.frame_login, placeholder_text="Usuario", width=250)
        self.txt_usuario.pack(pady=10)

        self.txt_password = ctk.CTkEntry(self.frame_login, placeholder_text="Contraseña", show="*", width=250)
        self.txt_password.pack(pady=10)

        btn_ingresar = ctk.CTkButton(self.frame_login, text="Ingresar", command=self._validar_login, width=250)
        btn_ingresar.pack(pady=20)

    def _validar_login(self):
        usuario = self.txt_usuario.get().strip()
        password = self.txt_password.get().strip()

        if not usuario or not password:
            messagebox.showwarning("Advertencia", "Por favor ingrese usuario y contraseña.")
            return

        try:
            # Usamos la función exacta de tus compañeros
            LoginLogica.iniciar_sesion(usuario, password)
            
            
            if self.al_ingresar:
                self.al_ingresar()
                
        except ValueError as e:
            # Captura el texto de error que lanzaron ("Usuario o contraseña incorrectos.")
            messagebox.showerror("Error de Autenticación", str(e))