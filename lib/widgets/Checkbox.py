import tkinter as tk
from tkinter import ttk
from lib.config import Config  # Importando o singleton diretamente

class UICheckbox(ttk.Frame):
    def __init__(self, parent, section, key, label, info=None, padx=0, pady=0):
        super().__init__(parent)
        self.section = section
        self.key = key

        self.pack(fill="x", pady=pady, padx=padx, anchor="w")

        # Variável do checkbox
        self.checkbox_var = tk.BooleanVar()
        self.checkbox_var.set(Config.get(self.section, self.key, "0") == "1")

        # Adicionando o trace para salvar automaticamente no Config ao alterar o valor
        self.checkbox_var.trace_add("write", self.on_checkbox_change)

        # Linha única para Checkbox, Info e Label
        row_frame = ttk.Frame(self)
        row_frame.pack(fill="x")

        # Checkbox
        self.checkbox = ttk.Checkbutton(row_frame, variable=self.checkbox_var, takefocus=False)
        self.checkbox.pack(side="left", padx=(0, 5))

        # Botão de Info (se fornecido)
        if info:
            info_button = ttk.Label(row_frame, text="ℹ", foreground="blue", cursor="hand2")
            info_button.pack(side="right", padx=(0, 5))
            # Adicionar tooltip aqui, se tiver um método para isso

        # Label à direita do checkbox
        ttk.Label(row_frame, text=label).pack(side="left", padx=(0, 5))

    def on_checkbox_change(self, *args):
        """Callback para salvar automaticamente quando o valor do checkbox muda."""
        Config.set(self.section, self.key, str(int(self.checkbox_var.get())))
        Config.save()

    def get_value(self):
        """Retorna se o checkbox está marcado ou não."""
        return self.checkbox_var.get()

    def set_value(self, value):
        """Define o estado do checkbox e atualiza o Config automaticamente."""
        self.checkbox_var.set(bool(value))
