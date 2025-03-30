import tkinter as tk
import lib.ui.widgets as ui
import logging
from tkinter import ttk
from lib.config import Config
from lib.ramws import RAMWS


class MultiAccountPage(ttk.Frame):
    def __init__(self, parent, manager, padx=10, pady=5):
        super().__init__(parent)
        self.manager = manager
        self.padx = padx
        self.pady = pady
        self.parent = parent
        self.label_status = None
        self.ram_webserver_modal = None
        self.all_items = []

        self.RWS_ACCOUNTS_SECTION_PREFIX = "RWS_ACCOUNT_"

        self._create_widgets()

    def __getLogger(self, name):
        return logging.getLogger(f"mspr.App.MultiAccountPage.{name}")

    def _create_widgets(self):
        """Cria os widgets principais, mas não os frames de sucesso/erro."""
        frame = ttk.Frame(self, padding=(self.padx, self.pady))
        frame.pack(fill="both", expand=True)

        # Frame para conectar (erro/sucesso será gerenciado depois)
        self.frame = frame
        self.create_error_frame()
        self.create_success_frame()

        # Inicializa com a tela de erro
        self.switch_to_error()

    def create_error_frame(self):
        """Cria o frame de erro."""
        self.frame_error = ttk.Frame(self.frame)
        label_error = ttk.Label(
            self.frame_error,
            text=(
                "Failed to connect to Roblox Account Manager WebServer!\n"
                'Make sure the "Enable Web Server" option is enabled in the Roblox Account Manager, and check if the port and passwords are correct.\n\n'
                'The "Every Request Requires Password" must be enabled and you must set a password for the web server.\n'
                "Once everything is correct, click Retry."
            ),
            wraplength=400,
            justify="center",
        )
        label_error.pack(pady=10)

        btn_retry = ttk.Button(
            self.frame_error,
            text="Retry",
            command=self.start_connection,
            takefocus=False,
        )
        btn_retry.pack(side="left", padx=10, fill="x")

        self.ram_webserver_modal = ui.ModalRAMWSSettings(self.parent)
        btn_settings = ttk.Button(
            self.frame_error,
            text="Settings",
            command=self.ram_webserver_modal.open,
            takefocus=False,
        )
        btn_settings.pack(side="right", padx=10, fill="x")

    def create_success_frame(self):
        """Cria o frame de sucesso com Treeview e botão de ativar/desativar conta."""
        self.frame_success = ttk.Frame(self.frame)

        # Barra de pesquisa e botão de refresh
        search_frame = ttk.Frame(self.frame_success)
        search_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(search_frame, text="Search:").pack(side="left", padx=(0, 5))
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        search_entry.pack(side="left", fill="x", expand=True)
        search_entry.bind("<KeyRelease>", self.filter_tree)

        # Botão para re-fetch
        refresh_button = ttk.Button(
            search_frame,
            text="Fetch Accounts",
            command=self.fetch_accounts,
            takefocus=False,
        )
        refresh_button.pack(side="right", padx=10)

        # Definição das colunas do Treeview
        columns = ("Account", "Private Server URL", "Alternate Webhook URL")

        style = ttk.Style()
        style.configure(
            "Custom.Treeview",
            background="white",
            fieldbackground="white",
            borderwidth=0,
        )

        # Aqui você define apenas o fundo de seleção, mantendo o foreground original.
        style.map(
            "Custom.Treeview",
            background=[("selected", "#c7d7ff")],  # Cor suave para o item selecionado
        )

        self.tree_success = ttk.Treeview(
            self.frame_success,
            columns=columns,
            show="headings",
            style="Custom.Treeview",
        )
        
        self.tree_success.tag_configure("disabled", foreground="gray", background="#f0f0f0")

        for col in columns:
            self.tree_success.heading(col, text=col)
            self.tree_success.column(col, anchor="center", stretch=tk.YES)  # Deixe a coluna "stretchable"

        # Scrollbar para o Treeview
        tree_scroll = ttk.Scrollbar(
            self.frame_success, orient="vertical", command=self.tree_success.yview
        )
        self.tree_success.configure(yscrollcommand=tree_scroll.set)
        tree_scroll.pack(side="right", fill="y")

        # Dicionário para armazenar status das contas (Enabled/Disabled)
        self.account_status = {}
        
        # Lista para armazenar as referências dos itens no Treeview
        self.tree_items = {}

        # Chama a função fetch_accounts para popular os dados no Treeview
        self.fetch_accounts()  # Aqui você pode descomentar essa linha quando quiser buscar as contas reais.

        # Bind para duplo clique na coluna "Account" para ativar/desativar a conta
        self.tree_success.bind(
            "<Button-1>",
            lambda event: self.tree_success.selection_remove(
                self.tree_success.selection()
            ),
        )
        self.tree_success.bind("<Double-1>", self.on_double_click)

        # Empacotar o Treeview
        self.tree_success.pack(pady=10, fill="both", expand=True)
        self.frame_success.pack(fill="both", expand=True)
        
        # Criar o botão "Launch Accounts"
        launch_button = ttk.Button(
            self.frame_success,
            text="Launch Accounts",
            command=self.launch_all_accounts,
            takefocus=False,
        )
        launch_button.pack(pady=10)

        # Ajuste de largura das colunas após o carregamento inicial
        total_width = self.tree_success.winfo_width()
        self.tree_success.column("Account", width=int(total_width * 0.25))  # 25% da largura da janela
        self.tree_success.column("Private Server URL", width=int(total_width * 0.35))  # 35% da largura da janela
        self.tree_success.column("Alternate Webhook URL", width=int(total_width * 0.4))  # 40% da largura da janela


    def filter_tree(self, event=None):
        """Filtra o Treeview com base no texto de pesquisa em todos os campos da linha."""
        search_text = self.search_var.get().lower()

        # Limpa o Treeview
        for item in self.tree_success.get_children():
            self.tree_success.delete(item)

        # Se o filtro estiver vazio, reinserir todos os dados
        if not search_text:
            for data in self.all_data:
                account, server_url, webhook_url, enabled = data
                item_id = self.tree_success.insert(
                    "", "end", values=(account, server_url, webhook_url)
                )
                self.tree_items[item_id] = (account, server_url, webhook_url)
                self.account_status[item_id] = enabled
                if not enabled:
                    self.tree_success.item(item_id, tags=("disabled",))
            return

        # Se houver filtro, insere somente os itens que correspondem a qualquer campo
        for data in self.all_data:
            account, server_url, webhook_url, enabled = data
            # Verifica se o texto de pesquisa está em qualquer campo
            if (
                search_text in account.lower()
                or search_text in server_url.lower()
                or search_text in webhook_url.lower()
            ):
                item_id = self.tree_success.insert(
                    "", "end", values=(account, server_url, webhook_url)
                )
                self.tree_items[item_id] = (account, server_url, webhook_url)
                self.account_status[item_id] = enabled
                if not enabled:
                    self.tree_success.item(item_id, tags=("disabled",))





    def on_double_click(self, event):
        """Permite edição das células (exceto Account) ao dar um duplo clique e alterna o status na coluna Account."""
        item_id = self.tree_success.identify_row(event.y)
        if not item_id:
            return

        column_id = self.tree_success.identify_column(event.x)
        column_index = int(column_id[1:]) - 1  # Colunas começam em 1 no Treeview

        # Se for a coluna "Account", alterna o status (habilitar/desabilitar)
        if column_index == 0:  # A "Account" é a coluna de índice 0
            self.toggle_account(item_id)
        else:
            # Se for qualquer outra coluna, permite a edição
            self.on_edit(event)

    def toggle_account(self, item_id):
        """Ativa ou desativa uma conta e altera a aparência visual."""
        enable = not self.account_status.get(item_id, True)  # Alterna o estado
        self.account_status[item_id] = enable

        values = self.tree_success.item(item_id, "values")

        # Salva a mudança no arquivo de configuração
        account = values[0]
        section = f"{self.RWS_ACCOUNTS_SECTION_PREFIX}{account}"

        # Atualiza a configuração para a conta (salva o status de 'enabled')
        Config.set(section=section, key="enabled", value=str(enable))
        Config.save()

        # Atualiza o status visual no Treeview
        if enable:
            self.tree_success.item(
                item_id, values=values, tags=()
            )  # Remove efeito escuro
        else:
            self.tree_success.item(item_id, values=values, tags=("disabled",))

    def on_edit(self, event):
        """Permite edição das células (exceto Account) ao dar um duplo clique."""
        selected_item = self.tree_success.selection()
        if not selected_item:
            return

        column_id = self.tree_success.identify_column(event.x)
        column_index = int(column_id[1:]) - 1  # Colunas começam em 1 no Treeview

        # Se for a coluna "Account", impedir edição
        if column_index == 0:  # A "Account" é a coluna de índice 0
            return

        # Obter valores atuais da linha selecionada
        item = selected_item[0]
        values = list(self.tree_success.item(item, "values"))

        # Criar um Entry para edição
        entry = ttk.Entry(self.tree_success)
        entry.insert(0, values[column_index])
        entry.select_range(0, "end")
        entry.focus()

        # Posicionar o Entry sobre a célula clicada
        x, y, width, height = self.tree_success.bbox(item, column_index)
        entry.place(x=x, y=y, width=width, height=height)

        def save_edit(event):
            """Salva a edição, atualiza o Treeview e as configurações no Config."""
            # Atualiza o valor na linha do Treeview
            values[column_index] = entry.get()
            self.tree_success.item(item, values=values)
            self.tree_items[item] = tuple(values[:3])  # Atualiza os dados armazenados

            # Salvar a edição no Config
            account = values[0]  # "Account" é sempre o primeiro valor na linha
            account_section = f"{self.RWS_ACCOUNTS_SECTION_PREFIX}{account}"

            # Salva o novo valor na configuração
            if column_index == 1:  # Coluna 1: Server URL
                Config.set(section=account_section, key="server_url", value=entry.get())
            elif column_index == 2:  # Coluna 2: Webhook URL
                Config.set(
                    section=account_section, key="webhook_url", value=entry.get()
                )

            # Salvar o estado da conta (habilitado ou desabilitado)
            enabled = self.account_status.get(item, True)
            Config.set(section=account_section, key="enabled", value=enabled)

            # Confirma que a configuração foi salva
            Config.save()  # Se a sua Config tem um método de salvar, chame aqui

            # Destroi o entry após salvar
            entry.destroy()

        entry.bind("<Return>", save_edit)
        entry.bind("<FocusOut>", lambda e: entry.destroy())

    def switch_to_success(self):
        """Exibe o frame de sucesso e oculta o de erro."""
        self.frame_error.pack_forget()
        self.frame_success.pack(fill="both", expand=True)

    def switch_to_error(self):
        """Exibe o frame de erro e oculta o de sucesso."""
        self.frame_success.pack_forget()
        self.frame_error.pack(fill="both", expand=True)

    def on_connection_checked(self, result):
        """Callback chamado quando a verificação de conexão for concluída."""
        if result:
            self.switch_to_success()
        else:
            self.switch_to_error()

    def start_connection(self):
        """Inicia a tentativa de conexão e o monitoramento contínuo."""
        self.frame_success.pack_forget()
        self.frame_error.pack_forget()

        self.label_status = ttk.Label(
            self, text="Connecting to Roblox Account Manager WebServer..."
        )
        self.label_status.pack(pady=10)

        # Testa a conexão de forma assíncrona
        RAMWS.test_connection_async(
            lambda res: (
                self.label_status.pack_forget(),
                self.on_connection_checked(res),
            )
        )

        # Inicia o keepalive
        RAMWS.start_keepalive(self.on_connection_checked)

    def fetch_accounts(self):
        """Busca as contas novamente do RAMWS e atualiza o Treeview."""
        l = self.__getLogger("fetch_accounts")
        l.debug("Fetching accounts from RAMWS...")

        def update_treeview(accounts):
            """Atualiza o Treeview com as contas recebidas."""
            self.all_data = []  # Limpa os dados anteriores
            
            # Limpa os itens existentes no Treeview
            for item in self.tree_success.get_children():
                self.tree_success.delete(item)

            # Para cada conta, buscamos detalhes como o server_url e webhook_url
            for account in accounts:
                # Buscando configurações no Config para cada conta
                account_section = f"{self.RWS_ACCOUNTS_SECTION_PREFIX}{account}"
                account_status = Config.get(section=account_section, key="enabled", fallback=True)  # Assume que está habilitado se não encontrado
                account_status = account_status.lower() == "true"
                server_url = Config.get(
                    section=account_section, key="server_url", fallback=""
                )  # Nenhum valor encontrado, será None
                webhook_url = Config.get(
                    section=account_section, key="webhook_url", fallback=""
                )  # Nenhum valor encontrado, será None

                self.all_data.append((account, server_url, webhook_url, account_status))
                
                # Inserir a conta no Treeview
                item_id = self.tree_success.insert(
                    "", "end", values=(account, server_url, webhook_url)
                )
                self.tree_items[item_id] = (account, server_url, webhook_url)
                self.account_status[item_id] = (
                    account_status  # Define o status da conta conforme configurado
                )

                l.trace(
                    f"Account: {account}, Status: {account_status}, Typeof Status: {type(account_status)}"
                )
                # Atualiza a aparência dependendo do status da conta (habilitada/desabilitada)
                if not account_status:
                    l.info(f"Account: {account} is disabled.")
                    self.tree_success.item(item_id, values=self.tree_success.item(item_id, "values"), tags=("disabled",))

                self.all_items.append(
                    item_id
                )  # Adiciona o item à lista de todos os itens

        # Chama o método list_accounts do RAMWS
        RAMWS.list_accounts(update_treeview)
        
    def launch_all_accounts(self):
        """Inicia todas as contas habilitadas."""
        l = self.__getLogger("launch_all_accounts")
        l.info("Launching all accounts...")
        for item in self.tree_success.get_children():  # Pega todas as linhas do Treeview
            account = self.tree_success.item(item, "values")[0]  # Pega a conta
            is_enabled = Config.get(
                section=f"{self.RWS_ACCOUNTS_SECTION_PREFIX}{account}",
                key="enabled",
                fallback=True,
            )
            is_enabled = is_enabled.lower() == "true"
            
            server_url = Config.get(
                section=f"{self.RWS_ACCOUNTS_SECTION_PREFIX}{account}",
                key="server_url",
                fallback=False,
            )
            
            webhook_url = Config.get(
                section=f"{self.RWS_ACCOUNTS_SECTION_PREFIX}{account}",
                key="webhook_url",
                fallback=False,
            )
            
            if not is_enabled:
                l.warn(f"Skipping account {account} as it is disabled.")
                continue  # Pula para a próxima iteração se a conta não está habilitada
            
            l.info(f"Launching account: {account}")
            
            def on_success(data):
                l.info(f"Account {account} launched successfully.")
                pass
            
            def on_fail(data):
                l.error(f"Failed to launch account {account}: {data['error']}")
                pass
            
            RAMWS.launch_account(account=account, placeid="15532962292", jobid=server_url, join_vip=True, callback=lambda data: on_success(data) if data["success"] else on_fail(data))
            
