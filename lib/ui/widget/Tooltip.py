import tkinter as tk

from tkinter import ttk


class UIToolTip:
    def __init__(self, widget, text):
        """
        Adiciona uma tooltip ao widget especificado.

        :param widget: O widget ao qual a tooltip será vinculada.
        :param text: O texto exibido na tooltip.
        """
        self.widget = widget
        self.text = text

        # Criando a tooltip como uma janela separada
        self.tooltip = tk.Toplevel(widget)
        self.tooltip.withdraw()  # Esconde inicialmente
        self.tooltip.overrideredirect(True)  # Remove bordas da janela
        self.tooltip.geometry("+0+0")

        label = ttk.Label(
            self.tooltip,
            text=text,
            relief="solid",
            borderwidth=1,
            font=("Arial", 9),
            # anchor="center",
            # justify="center"
        )
        label.pack(ipadx=5, ipady=2)

        def show_tooltip(event):
            x = widget.winfo_rootx() + 20
            y = widget.winfo_rooty() + 20
            self.tooltip.geometry(f"+{x}+{y}")
            self.tooltip.deiconify()

        def hide_tooltip(event):
            self.tooltip.withdraw()

        # Eventos do widget para mostrar/esconder a tooltip
        self.widget.bind("<Enter>", show_tooltip)
        self.widget.bind("<Leave>", hide_tooltip)
