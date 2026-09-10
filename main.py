import customtkinter as ctk

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")


class App(ctk.CTk):

  def __init__(self):
    super().__init__()

    self.title("Mi Aplicación")
    self.geometry("400x200")

    self.label = ctk.CTkLabel(
        self, text="Hello World", font=ctk.CTkFont(size=20, weight="bold")
    )
    self.label.pack(padx=20, pady=40)


if __name__ == "__main__":
  app = App()
  app.mainloop()