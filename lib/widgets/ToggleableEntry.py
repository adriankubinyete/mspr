import tkinter as tk
from tkinter import ttk
from lib.config import Config  # Importando o singleton diretamente

class UIToggleableEntry(ttk.Frame):
    def __init__(self, parent, section, key, label, info=None, padx=0, pady=0, width=35, fallback=""):
        super().__init__(parent)
        self.section = section
        self.key = key

        self.pack(fill="x", pady=pady, padx=padx, anchor="w")

        row_frame = ttk.Frame(self)
        row_frame.pack(fill="x")

        # Obtém valores do Config ou usa fallback
        initial_enabled = Config.get(self.section, f"{key}_enabled", "1") == "1"
        initial_value = Config.get(self.section, key, fallback)

        # Variável da checkbox (ativa/desativa o input)
        self.toggle_var = tk.BooleanVar(value=initial_enabled)
        self.toggle_var.trace_add("write", self.on_toggle_change)

        # Checkbox para ativar/desativar o campo
        self.toggle_button = ttk.Checkbutton(row_frame, variable=self.toggle_var, takefocus=False)
        self.toggle_button.pack(side="left", padx=(0, 5))

        # Botão de Info (se fornecido)
        if info:
            info_button = ttk.Label(row_frame, text="ℹ", foreground="blue", cursor="hand2")
            info_button.pack(side="right", padx=(0, 5))
            # Adicionar tooltip aqui, se tiver um método para isso

        ttk.Label(row_frame, text=label).pack(side="left", padx=(0, 5))

        # Campo de entrada (input)
        self.entry_var = tk.StringVar(value=initial_value)
        self.entry_var.trace_add("write", self.on_entry_change)

        self.entry = ttk.Entry(row_frame, width=width, textvariable=self.entry_var)
        self.entry.pack(side="right", padx=(0, 5))

        row_frame.columnconfigure(1, weight=1)

        # Define o estado inicial baseado na checkbox
        self.toggle_entry()

    def toggle_entry(self):
        """Ativa ou desativa o campo de entrada baseado no checkbox."""
        state = "normal" if self.toggle_var.get() else "disabled"
        self.entry.config(state=state)

    def on_toggle_change(self, *args):
        """Salva automaticamente quando a checkbox muda."""
        self.toggle_entry()
        Config.set(self.section, f"{self.key}_enabled", str(int(self.toggle_var.get())))
        Config.save()

    def on_entry_change(self, *args):
        """Salva automaticamente quando o usuário digita no campo."""
        Config.set(self.section, self.key, self.entry_var.get())
        Config.save()

    def get_value(self):
        """Retorna o valor do campo de entrada."""
        return self.entry_var.get()

    def is_enabled(self):
        """Retorna se o campo está ativado ou não."""
        return self.toggle_var.get()
