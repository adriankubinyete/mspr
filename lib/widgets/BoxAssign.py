import tkinter as tk
from tkinter import ttk
from lib.config import Config
from lib.widgets.Tooltip import UIToolTip

class UIBoxAssign(ttk.LabelFrame):
    def __init__(self, parent, section, key, label, info=None, padx=0, pady=0):
        super().__init__(parent)
        self.section = section
        self.key = key

        self.pack(fill="x", pady=pady, padx=padx, anchor="w")

        # Criar um LabelFrame para organizar tudo
        section_frame = ttk.LabelFrame(self, text=label)
        section_frame.pack(fill="x")

        row_frame = ttk.Frame(section_frame)
        row_frame.pack(fill="x", padx=5, pady=5)

        # Recupera valores salvos ou usa "0,0,0,0" como fallback
        default_values = Config.get(self.section, self.key, "0,0,0,0").split(",")
        self.x_var = tk.IntVar(value=int(default_values[0]))
        self.y_var = tk.IntVar(value=int(default_values[1]))
        self.w_var = tk.IntVar(value=int(default_values[2]))
        self.h_var = tk.IntVar(value=int(default_values[3]))

        # Criar spinboxes para X, Y, W, H
        self.create_spinbox(row_frame, "X", self.x_var)
        self.create_spinbox(row_frame, "Y", self.y_var)
        self.create_spinbox(row_frame, "W", self.w_var)
        self.create_spinbox(row_frame, "H", self.h_var)

        # Botão de Info (se fornecido)
        if info:
            info_button = ttk.Label(row_frame, text="ℹ", foreground="blue", cursor="hand2")
            info_button.pack(side="right", padx=5)
            UIToolTip(info_button, info)  # 🔹 Adicionando tooltip
       
        # Botões de ação
        ttk.Button(row_frame, text="Assign", command=self.assign_box, takefocus=False).pack(side="right", padx=2)
        ttk.Button(row_frame, text="Show", command=self.show_box, takefocus=False).pack(side="right", padx=2)

    def create_spinbox(self, parent, text, var):
        """Cria um Spinbox com um label à esquerda."""
        ttk.Label(parent, text=f"{text}:", takefocus=False).pack(side="left", padx=2)
        spinbox = ttk.Spinbox(parent, from_=0, to=9999, textvariable=var, width=5)
        spinbox.pack(side="left", padx=2)

    def assign_box(self):
        """Cria uma overlay fullscreen para capturar a seleção da bounding box."""
        parent_window = self.winfo_toplevel()
        
        overlay = tk.Toplevel()
        overlay.attributes("-fullscreen", True)
        overlay.attributes("-alpha", 0.3)
        overlay.config(bg="black")
        overlay.overrideredirect(True)
        overlay.lift()

        canvas = tk.Canvas(overlay, bg="black", highlightthickness=0)
        canvas.pack(fill="both", expand=True)

        start_x = start_y = None
        rect_id = None

        def on_press(event):
            nonlocal start_x, start_y, rect_id
            start_x, start_y = event.x, event.y
            rect_id = canvas.create_rectangle(start_x, start_y, start_x, start_y, outline="red", width=2)

        def on_drag(event):
            canvas.coords(rect_id, start_x, start_y, event.x, event.y)

        def on_release(event):
            """Finaliza a seleção, salva no Config e fecha a overlay."""
            end_x, end_y = event.x, event.y
            x, y = min(start_x, end_x), min(start_y, end_y)
            width, height = abs(end_x - start_x), abs(end_y - start_y)

            x_root = overlay.winfo_rootx() + x
            y_root = overlay.winfo_rooty() + y

            self.x_var.set(x_root)
            self.y_var.set(y_root)
            self.w_var.set(width)
            self.h_var.set(height)

            self.save_value()
            overlay.destroy()

            # Mantém o menu de opções modal
            parent_window.grab_set()
            parent_window.focus_force()

        # Bind dos eventos do mouse
        canvas.bind("<ButtonPress-1>", on_press)
        canvas.bind("<B1-Motion>", on_drag)
        canvas.bind("<ButtonRelease-1>", on_release)

        overlay.grab_set()

    def show_box(self):
        """Mostra a bounding box na tela por 1 segundo."""
        overlay = tk.Toplevel()
        overlay.attributes("-topmost", True)
        overlay.attributes("-alpha", 0.3)
        overlay.overrideredirect(True)
        overlay.geometry(f"{self.w_var.get()}x{self.h_var.get()}+{self.x_var.get()}+{self.y_var.get()}")
        overlay.config(bg="red")

        overlay.after(1000, overlay.destroy)

    def save_value(self):
        """Salva a seleção no Config."""
        value = f"{self.x_var.get()},{self.y_var.get()},{self.w_var.get()},{self.h_var.get()}"
        Config.set(self.section, self.key, value)
        Config.save()
