import tkinter as tk

from tkinter import ttk

from lib.config import Config  # Importando o singleton diretamente
from lib.ui.widget.Tooltip import UIToolTip


class UIEntry(ttk.Frame):
    def __init__(
        self,
        parent,
        section,
        key,
        label,
        info=None,
        padx=0,
        pady=0,
        width=35,
        fallback="",
        autosave=True,
    ):
        super().__init__(parent)
        self.key = key
        self.section = section
        self.autosave = autosave

        self.pack(fill="x", pady=pady, padx=padx, anchor="w")

        row_frame = ttk.Frame(self)
        row_frame.pack(fill="x")

        if info:
            info_button = ttk.Label(
                row_frame, text="ℹ", foreground="blue", cursor="hand2"
            )
            info_button.pack(side="right", padx=5)
            UIToolTip(info_button, info)

        ttk.Label(row_frame, text=label).pack(side="left", padx=(0, 5))

        # Obtém valor do Config ou usa o fallback
        initial_value = Config.get(self.section, self.key, fallback)

        # Variável associada ao Entry
        self.entry_var = tk.StringVar(value=initial_value)

        # Adiciona um trace para salvar automaticamente apenas se autosave=True
        if self.autosave:
            self.entry_var.trace_add("write", self.on_entry_change)

        self.entry = ttk.Entry(row_frame, width=width, textvariable=self.entry_var)
        self.entry.pack(side="right", padx=(0, 5))

        row_frame.columnconfigure(1, weight=1)

    def on_entry_change(self, *args):
        """Callback para salvar automaticamente quando o valor do Entry muda (se autosave=True)."""
        if self.autosave:
            self.save()

    def save(self):
        """Salva o valor manualmente no Config."""
        Config.set(self.section, self.key, self.entry_var.get())
        Config.save()

    def get_value(self):
        """Retorna o valor atual do campo de entrada."""
        return self.entry_var.get()

    def set_value(self, value):
        """Define o valor do campo de entrada e salva automaticamente no Config (se autosave=True)."""
        self.entry_var.set(value)
        if self.autosave:
            self.save()
