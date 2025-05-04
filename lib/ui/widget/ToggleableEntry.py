import tkinter as tk
from tkinter import ttk
from lib.config import Config  # Importando o singleton diretamente
from lib.ui.widget.Tooltip import UIToolTip

class UIToggleableEntry(ttk.Frame):
    def __init__(self, parent, section, key, label, info=None, padx=0, pady=0, width=35, fallback="", autosave=True):
        super().__init__(parent)
        self.section = section
        self.key = key
        
        self.autosave = autosave
        self._debounce_job = None 
        self.DEBOUNCE = 300  # ms : debounce for save job

        self.pack(fill="x", pady=pady, padx=padx, anchor="w")

        row_frame = ttk.Frame(self)
        row_frame.pack(fill="x")

        initial_enabled = Config.get(self.section, f"{key}_enabled", "1") == "1"
        initial_value = Config.get(self.section, key, fallback)

        self.toggle_var = tk.BooleanVar(value=initial_enabled)

        self.toggle_button = ttk.Checkbutton(row_frame, variable=self.toggle_var, takefocus=False, command=self._on_toggle)
        self.toggle_button.pack(side="left", padx=(0, 5))

        if info:
            info_button = ttk.Label(row_frame, text="ℹ", foreground="blue", cursor="hand2")
            info_button.pack(side="right", padx=5)
            UIToolTip(info_button, info)

        ttk.Label(row_frame, text=label).pack(side="left", padx=(0, 5))

        self.entry_var = tk.StringVar(value=initial_value)

        self.entry = ttk.Entry(row_frame, width=width, textvariable=self.entry_var)
        self.entry.pack(side="right", padx=(0, 5))
        self.entry.bind("<KeyRelease>", self._on_key_release)

        row_frame.columnconfigure(1, weight=1)

        self.toggle_entry()

    def toggle_entry(self):
        """Ativa ou desativa o campo de entrada baseado no checkbox."""
        state = "normal" if self.toggle_var.get() else "disabled"
        self.entry.config(state=state)

    def _on_toggle(self):
        self.toggle_entry()
        if self.autosave:
            self.save()

    def _on_key_release(self, event):
        """Inicia o debounce ao digitar no campo de entrada."""
        if self.autosave:
            if self._debounce_job:
                self.after_cancel(self._debounce_job)
            self._debounce_job = self.after(self.DEBOUNCE, self._delayed_save)

    def _delayed_save(self):
        """Executado após o debounce, salva o valor."""
        self._debounce_job = None
        self.save()

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
