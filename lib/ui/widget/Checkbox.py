import tkinter as tk

from tkinter import ttk

from lib.config import Config  # Importando o singleton diretamente
from lib.ui.widget.Tooltip import UIToolTip


class UICheckbox(ttk.Frame):
    def __init__(
        self, parent, section, key, label, info=None, padx=0, pady=0, autosave=True
    ):
        """
        Cria um checkbox com opção de salvamento manual ou automático.

        :param parent: Widget pai.
        :param section: Seção no config.ini.
        :param key: Chave no config.ini.
        :param label: Texto do checkbox.
        :param info: Texto informativo opcional.
        :param padx: Padding horizontal.
        :param pady: Padding vertical.
        :param autosave: Define se o valor será salvo automaticamente ao mudar.
        """
        super().__init__(parent)
        self.section = section
        self.key = key
        self.autosave = autosave

        self.pack(fill="x", pady=pady, padx=padx, anchor="w")

        # Variável do checkbox
        self.checkbox_var = tk.BooleanVar()
        self.checkbox_var.set(Config.get(self.section, self.key, "0") == "1")

        # Se autosave estiver ativado, adiciona um trace para salvar automaticamente
        if self.autosave:
            self.checkbox_var.trace_add("write", self.on_checkbox_change)

        # Linha única para Checkbox, Info e Label
        row_frame = ttk.Frame(self)
        row_frame.pack(fill="x")

        # Checkbox
        self.checkbox = ttk.Checkbutton(
            row_frame, variable=self.checkbox_var, takefocus=False
        )
        self.checkbox.pack(side="left", padx=(0, 5))

        # Botão de Info (se fornecido)
        if info:
            info_button = ttk.Label(
                row_frame, text="ℹ", foreground="blue", cursor="hand2"
            )
            info_button.pack(side="right", padx=5)
            UIToolTip(info_button, info)

        # Label à direita do checkbox
        ttk.Label(row_frame, text=label).pack(side="left", padx=(0, 5))

    def on_checkbox_change(self, *args):
        """Salva automaticamente quando o valor do checkbox muda (se autosave=True)."""
        if self.autosave:
            self.save()

    def save(self):
        """Salva manualmente o estado do checkbox no Config."""
        Config.set(self.section, self.key, str(int(self.checkbox_var.get())))
        Config.save()

    def get_value(self):
        """Retorna se o checkbox está marcado ou não."""
        return self.checkbox_var.get()

    def set_value(self, value):
        """Define o estado do checkbox e salva automaticamente se autosave=True."""
        self.checkbox_var.set(bool(value))
        if self.autosave:
            self.save()
