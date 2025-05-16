import tkinter as tk

from tkinter import ttk

from lib.config import Config  # Importando o singleton diretamente


class UIEntry(ttk.Frame):
    def __init__(
        self,
        parent,
        section,
        key,
        label=None,
        info=None,
        padx=0,
        pady=0,
        width=35,
        fallback="",
        show_label=True,
        show_info=True,
    ):
        """
        Construtor para o widget de entrada.

        :param parent: O widget pai onde este widget será colocado.
        :param section: A seção no arquivo de configuração.
        :param key: A chave de configuração para obter o valor inicial.
        :param label: O texto do rótulo associado ao Entry (opcional).
        :param info: Texto informativo para ser exibido ao lado do rótulo (opcional).
        :param padx: Espaço extra no eixo X.
        :param pady: Espaço extra no eixo Y.
        :param width: Largura do campo de entrada.
        :param fallback: Valor padrão caso a chave não seja encontrada no arquivo de configuração.
        :param show_label: Se True, exibe o rótulo (label).
        :param show_info: Se True, exibe o botão de info.
        """
        super().__init__(parent)

        # Atributos para identificar a seção e a chave no arquivo de configuração
        self.key = key
        self.section = section

        # Variáveis opcionais
        self.show_label = show_label
        self.show_info = show_info

        # Obtém o valor do Config ou usa o fallback
        initial_value = Config.get(self.section, self.key, fallback)

        # Variável associada ao Entry
        self.entry_var = tk.StringVar(value=initial_value)

        # Criação do frame para a linha
        row_frame = ttk.Frame(self)
        row_frame.grid(row=0, column=0, sticky="w")  # Usando grid ao invés de pack

        if self.show_info and info:
            info_button = ttk.Label(
                row_frame, text="ℹ", foreground="blue", cursor="hand2"
            )
            info_button.grid(
                row=0, column=2, padx=(0, 5)
            )  # Organizando o info_button no grid

        if self.show_label and label:
            ttk.Label(row_frame, text=label).grid(
                row=0, column=0, padx=(0, 5)
            )  # Organizando o label no grid

        # Adiciona o Entry ao frame
        self.entry = ttk.Entry(row_frame, width=width, textvariable=self.entry_var)
        self.entry.grid(row=0, column=1, padx=(0, 5))  # Organizando o entry no grid

        row_frame.columnconfigure(
            1, weight=1
        )  # Permitindo que a coluna do entry expanda

        # Adiciona um trace para salvar automaticamente ao alterar o valor
        self.entry_var.trace_add("write", self.on_entry_change)

    def on_entry_change(self, *args):
        """Callback para salvar automaticamente quando o valor do Entry muda."""
        Config.set(self.section, self.key, self.entry_var.get())
        Config.save()

    def get_value(self):
        """Retorna o valor atual do campo de entrada."""
        return self.entry_var.get()

    def set_value(self, value):
        """Define o valor do campo de entrada e salva automaticamente no Config."""
        self.entry_var.set(value)
