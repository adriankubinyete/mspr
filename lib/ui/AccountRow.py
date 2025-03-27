import tkinter as tk
from tkinter import ttk
import lib.ui.widgets as ui
from lib.config import Config  # Para salvar as configurações

class AccountRow(ttk.Frame):
    def __init__(self, parent, manager, username, server_link, webhook, button_callback=None, padx=10, pady=5):
        """
        Cria uma linha de conta de jogador com 3 Entries e 1 botão de remoção.

        :param parent: Widget pai.
        :param manager: O AccountManager que gerencia as linhas.
        :param username: O nome de usuário da conta.
        :param server_link: O link do servidor.
        :param webhook: O webhook alternativo.
        :param button_callback: Função a ser chamada quando o botão for pressionado.
        :param padx: Padding horizontal.
        :param pady: Padding vertical.
        """
        super().__init__(parent)
        
        self.manager = manager  # Referência ao AccountManager
        self.pack(fill="x", pady=pady, padx=padx, anchor="w")
        
        # Linha de elementos
        row_frame = ttk.Frame(self)
        row_frame.pack(fill="x", padx=5, pady=5)
        
        # Entry do username
        self.entry_username = ui.Entry(row_frame, section=f"ACCOUNT_{username}", key="username", fallback=username, show_label=False)
        self.entry_username.grid(row=0, column=0, padx=(0, 10), sticky="w")

        # Entry do link do servidor
        self.entry_server = ui.Entry(row_frame, section=f"ACCOUNT_{username}", key="server_link", fallback=server_link, show_label=False)
        self.entry_server.grid(row=0, column=1, padx=(0, 10), sticky="w")

        # Entry do webhook alternativo
        self.entry_webhook = ui.Entry(row_frame, section=f"ACCOUNT_{username}", key="webhook", fallback=webhook, show_label=False)
        self.entry_webhook.grid(row=0, column=2, padx=(0, 10), sticky="w")

        # Botão de remover
        self.button = ttk.Button(row_frame, text="Remove", command=self.remove_account)
        self.button.grid(row=0, column=3, padx=5, pady=5)

    def remove_account(self):
        """Remove a conta e a linha do widget."""
        # Remove as configurações associadas à conta (usando o username como referência)
        username = self.entry_username.get_value()  # Obtém o valor do campo de username
        Config.set(f"ACCOUNT_{username}", "username", "")  # Limpa o valor do username
        Config.set(f"ACCOUNT_{username}", "server_link", "")  # Limpa o valor do server_link
        Config.set(f"ACCOUNT_{username}", "webhook", "")  # Limpa o valor do webhook
        Config.save()  # Salva as alterações no arquivo de configuração
        
        # Remove o próprio widget AccountRow
        self.manager.remove_row(self)  # Chama o método do manager para remover a linha
        self.destroy()  # Destrói o widget AccountRow da interface


class AccountManager(ttk.Frame):
    def __init__(self, parent):
        """
        Gerencia as contas dos jogadores, adicionando e removendo AccountRows.
        """
        super().__init__(parent)
        self.pack(fill="both", expand=True)
        
        self.rows = []  # Lista para armazenar as instâncias de AccountRow

        # Botão para adicionar nova conta
        self.btn_add = ttk.Button(self, text="Add Account", command=self.add_account)
        self.btn_add.pack(padx=10, pady=10)

        # Botão para salvar todas as contas
        self.btn_save = ttk.Button(self, text="Save", command=self.save_all)
        self.btn_save.pack(padx=10, pady=10)

    def add_account(self):
        """Adiciona uma nova linha de conta."""
        # Adiciona uma nova linha de conta com valores de exemplo
        account_row = AccountRow(self, self, username="new_user", server_link="http://example.com", webhook="http://webhook.com")
        self.rows.append(account_row)  # Adiciona a linha à lista de linhas

    def save_all(self):
        """Salva as configurações de todas as contas."""
        for row in self.rows:
            # Salva as configurações para cada AccountRow
            username = row.entry_username.get_value()
            server_link = row.entry_server.get_value()
            webhook = row.entry_webhook.get_value()

            # Salva cada campo de configuração
            Config.set(f"ACCOUNT_{username}", "username", username)
            Config.set(f"ACCOUNT_{username}", "server_link", server_link)
            Config.set(f"ACCOUNT_{username}", "webhook", webhook)

        Config.save()  # Salva todas as configurações

    def remove_row(self, account_row):
        """Remove a linha de conta da lista de AccountRows."""
        if account_row in self.rows:
            self.rows.remove(account_row)
