from tkinter import messagebox
import customtkinter as ctk
from logica.autenticacion_logica import AutenticacionServicio


class LoginView(ctk.CTkFrame):

  def __init__(self, master, al_ingresar_exitoso):
    super().__init__(master)
    self.master = master
    self.al_ingresar_exitoso = al_ingresar_exitoso
    self.pack(fill="both", expand=True, padx=20, pady=20)

    self._crear_interfaz()

  def _crear_interfaz(self):
    ctk.CTkLabel(
        self, text="Iniciar Sesión", font=ctk.CTkFont(size=22, weight="bold")
    ).pack(pady=20)

    self.entry_usuario = ctk.CTkEntry(self, placeholder_text="Usuario")
    self.entry_usuario.pack(pady=10, fill="x", padx=50)

    self.entry_password = ctk.CTkEntry(
        self, placeholder_text="Contraseña", show="*"
    )
    self.entry_password.pack(pady=10, fill="x", padx=50)

    btn_ingresar = ctk.CTkButton(
        self, text="Ingresar", command=self._evento_ingresar
    )
    btn_ingresar.pack(pady=20)

  def _evento_ingresar(self):
    usr = self.entry_usuario.get()
    pwd = self.entry_password.get()

    try:
      AutenticacionServicio.iniciar_sesion(usr, pwd)
      self.destroy()
      self.al_ingresar_exitoso()
    except ValueError as err:
      messagebox.showerror("Error de Autenticación", str(err))