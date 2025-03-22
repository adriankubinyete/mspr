import tkinter as tk
from tkinter import ttk
from lib.config import Config  # Importando o singleton diretamente
from lib.widgets.Tooltip import UIToolTip

class UIRadio(ttk.Frame):
    def __init__(self, parent, section, key, label, options, info=None, padx=0, pady=0, max_columns=3):
        """
        Cria um grupo de botões de rádio, ajustando para múltiplas linhas conforme necessário.

        :param parent: Widget pai.
        :param section: Seção no config.ini.
        :param key: Chave no config.ini.
        :param label: Texto do grupo.
        :param options: Lista de opções [(valor, texto), ...].
        :param info: Texto informativo opcional.
        :param padx: Padding horizontal.
        :param pady: Padding vertical.
        :param max_columns: Número máximo de colunas antes de quebrar para a próxima linha.
        """
        super().__init__(parent)
        self.section = section
        self.key = key

        self.pack(fill="x", pady=pady, padx=padx, anchor="w")

        # Obtém o valor salvo ou usa o primeiro como padrão
        initial_value = Config.get(self.section, key, options[0][0])

        self.radio_var = tk.StringVar(value=initial_value)
        self.radio_var.trace_add("write", self.on_radio_change)

        # Frame principal com borda
        frame = ttk.LabelFrame(self, text=label)
        frame.pack(fill="x")

        # Frame interno para os botões
        radio_frame = ttk.Frame(frame)
        radio_frame.pack(fill="both", expand=True)

        # Configurar grid para centralizar dinamicamente
        radio_frame.grid_columnconfigure(tuple(range(max_columns)), weight=1)

        # Adiciona os botões em múltiplas linhas
        for index, (value, text) in enumerate(options):
            row = index // max_columns
            col = index % max_columns
            ttk.Radiobutton(radio_frame, text=text, variable=self.radio_var, value=value, takefocus=False).grid(
                row=row, column=col, padx=10, pady=5
            )

        # Botão de Info POSICIONADO ABSOLUTAMENTE
        if info:
            info_button = ttk.Label(frame, text="ℹ", foreground="blue", cursor="hand2")
            info_button.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-8)  # Posição absoluta no canto inferior direito
            UIToolTip(info_button, info)

    def on_radio_change(self, *args):
        """Salva automaticamente quando o usuário muda a seleção."""
        Config.set(self.section, self.key, self.radio_var.get())
        Config.save()

    def get_value(self):
        """Retorna o valor selecionado."""
        return self.radio_var.get()

    def set_value(self, value):
        """Define o valor do botão de rádio e salva automaticamente."""
        self.radio_var.set(value)
