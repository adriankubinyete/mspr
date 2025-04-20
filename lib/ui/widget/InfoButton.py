import tkinter as tk
from tkinter import ttk
from lib.ui.widget.Tooltip import UIToolTip  # Importando o Tooltip

class UIInfoButton(ttk.Label):
    def __init__(self, parent, info, padx=0, pady=0):
        """
        Cria um botão de informação com tooltip.

        :param parent: Widget pai.
        :param info: Texto informativo a ser mostrado no tooltip.
        :param padx: Padding horizontal.
        :param pady: Padding vertical.
        """
        super().__init__(parent, text="ℹ", foreground="blue", cursor="hand2")
        
        # Adicionando o tooltip ao botão de informação
        if info:
            UIToolTip(self, info)
        
        # Usando grid em vez de pack para manter consistência com o layout
        # self.grid(padx=padx, pady=pady)

