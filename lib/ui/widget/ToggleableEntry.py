import tkinter as tk
from tkinter import ttk
from lib.config import Config  # Importando o singleton diretamente
from lib.ui.widget.Tooltip import UIToolTip

class UIToggleableEntry(ttk.Frame):
    def __init__(self, parent, section, key, label, info=None, padx=0, pady=0, width=35, fallback="", autosave=True):
        """
        Cria um campo de entrada com um checkbox para ativá-lo/desativá-lo.

        :param parent: Widget pai.
        :param section: Seção no config.ini.
        :param key: Chave no config.ini.
        :param label: Texto do campo.
        :param info: Texto informativo opcional.
        :param padx: Padding horizontal.
        :param pady: Padding vertical.
        :param width: Largura do campo de entrada.
        :param fallback: Valor padrão caso não exista no config.
        :param autosave: Define se o valor será salvo automaticamente ao mudar.
        """
        super().__init__(parent)
        self.section = section
        self.key = key
        self.autosave = autosave

        self.pack(fill="x", pady=pady, padx=padx, anchor="w")

        row_frame = ttk.Frame(self)
        row_frame.pack(fill="x")

        # Obtém valores do Config ou usa fallback
        initial_enabled = Config.get(self.section, f"{key}_enabled", "1") == "1"
        initial_value = Config.get(self.section, key, fallback)

        # Variável da checkbox (ativa/desativa o input)
        self.toggle_var = tk.BooleanVar(value=initial_enabled)

        # Checkbox para ativar/desativar o campo
        self.toggle_button = ttk.Checkbutton(row_frame, variable=self.toggle_var, takefocus=False, command=self.toggle_entry)
        self.toggle_button.pack(side="left", padx=(0, 5))

        # Botão de Info (se fornecido)
        if info:
            info_button = ttk.Label(row_frame, text="ℹ", foreground="blue", cursor="hand2")
            info_button.pack(side="right", padx=5)
            UIToolTip(info_button, info)

        ttk.Label(row_frame, text=label).pack(side="left", padx=(0, 5))

        # Campo de entrada (input)
        self.entry_var = tk.StringVar(value=initial_value)

        self.entry = ttk.Entry(row_frame, width=width, textvariable=self.entry_var)
        self.entry.pack(side="right", padx=(0, 5))

        row_frame.columnconfigure(1, weight=1)

        # Define o estado inicial baseado na checkbox
        self.toggle_entry()

    def toggle_entry(self):
        """Ativa ou desativa o campo de entrada baseado no checkbox."""
        state = "normal" if self.toggle_var.get() else "disabled"
        self.entry.config(state=state)

    def save(self):
        """Salva manualmente o estado da checkbox e o valor do campo no Config."""
        Config.set(self.section, f"{self.key}_enabled", str(int(self.toggle_var.get())))
        Config.set(self.section, self.key, self.entry_var.get())
        Config.save()

    def get_value(self):
        """Retorna o valor do campo de entrada."""
        return self.entry_var.get()

    def is_enabled(self):
        """Retorna se o campo está ativado ou não."""
        return self.toggle_var.get()
