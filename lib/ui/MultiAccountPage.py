import tkinter as tk
import lib.ui.widgets as ui
import logging
from collections import defaultdict
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
        return logging.getLogger(f"mpsr.page:MultiAccount.{name}")

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

    # failed to connect to ramws
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

    # connected to ramws
    def create_success_frame(self):
        """Creates the success frame with a search bar, Treeview, and launch button."""

        # Main container frame
        self.frame_success = tk.Frame(self.frame)
        self.frame_success.pack(fill="both", expand=True)

        # --- Test Frame (first things, just testing. control panel)        
        test_frame = tk.Frame(self.frame_success, background="blue", borderwidth=1)
        test_frame.pack(fill="x", pady=5, padx=5)
        
        # > "keep-alive checkbox"

        # --- Search Frame (top)
        search_frame = tk.Frame(self.frame_success)
        search_frame.pack(fill="x", pady=(5, 5))

        # > "Search" label
        ttk.Label(search_frame, text="Search:").pack(side="left", padx=(0, 5), pady=5)

        # > Search entry field
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        search_entry.pack(side="left", fill="x", expand=True, pady=5)
        search_entry.bind("<KeyRelease>", self.filter_tree)

        # > Fetch Accounts button
        refresh_button = ttk.Button(
            search_frame,
            text="Fetch Accounts",
            command=self.fetch_accounts,
            takefocus=False,
        )
        refresh_button_info = ui.InfoButton(
            search_frame,
            info="The \"Fetch Accounts\" will fetch accounts from the Roblox Account Manager and display them in the table below.\n\nClick this button if you have added or removed accounts from the Roblox Account Manager.\n\nIf you have not added or removed accounts, you can ignore this button.",
        )
        
        refresh_button_info.pack(side="right", padx=(5, 0), pady=5)
        refresh_button.pack(side="right", padx=(10, 0), pady=5)
        

        # --- Treeview Frame (middle, expandable)
        treeview_frame = tk.Frame(self.frame_success)
        treeview_frame.pack(fill="both", expand=True, pady=5)
        
        treeview_frame.pack_propagate(False)

        # > Treeview style configuration
        style = ttk.Style()
        style.configure(
            "Custom.Treeview",
            background="white",
            fieldbackground="white",
            borderwidth=0,
        )
        # style.map(
        #     "Custom.Treeview",
        #     background=[("selected", "#c7d7ff")],
        # )

        # > Define treeview columns
        columns = ("Account", "Private Server URL", "Alternate Webhook URL")
        self.accounts_treeview = ttk.Treeview(
            treeview_frame,
            columns=columns,
            show="headings",
            style="Custom.Treeview",
        )
        self.accounts_treeview.tag_configure("disabled", foreground="#441520", background="#eebbc1")
        self.accounts_treeview.tag_configure("selected", foreground="#3691ff")

        for col in columns:
            self.accounts_treeview.heading(col, text=col)
            self.accounts_treeview.column(col, anchor="center", stretch=tk.YES)

        # > Vertical scrollbar for Treeview
        tree_scroll = ttk.Scrollbar(
            treeview_frame, orient="vertical", command=self.accounts_treeview.yview
        )
        self.accounts_treeview.configure(yscrollcommand=tree_scroll.set)

        # Place Treeview and Scrollbar
        tree_scroll.pack(side="right", fill="y")
        self.accounts_treeview.pack(side="left", fill="both", expand=True)

        # > Track account states and item references
        self.account_status = {}
        self.tree_items = {}

        # > Treeview interaction bindings
        # 1 lclick: select
        # ~ should work through tagging for style. only changes foreground
        
        # 2 lclick on field: edit field
        # 2 lclick on account column: toggle account (enabled/disabled)
        # ~ should work through tagging for style. changes both foreground and background. overriden by select
        
        # 1 rclick: [NOT IMPLEMENTED] context menu 
        self.accounts_treeview.bind(
            "<Button-1>",
            lambda event: self.accounts_treeview.selection_remove(
                self.accounts_treeview.selection()
            ),
        )
        self.accounts_treeview.bind("<Double-1>", self.on_double_click)
        
        # > Treeview Context menu
        self.accounts_treeview.bind("<Button-3>", self.treeview_context_menu)
        self.treeview_menu = tk.Menu(self.accounts_treeview, tearoff=0)
        self.treeview_menu.add_command(label="Launch account", command=self.context_launch_account)
        self.treeview_menu.add_command(label="Debuginfo", command=self.context_debug_info)

        # > Populate treeview
        self.fetch_accounts()

        # --- Footer Frame (bottom, always visible)
        footer_frame = tk.Frame(self.frame_success)
        footer_frame.pack(fill="x", pady=(5, 10))

        # > Launch Accounts button
        launch_button = ttk.Button(
            footer_frame,
            text="Launch Accounts",
            command=self.launch_all_accounts,
            takefocus=False,
        )
        launch_button.pack()

        # > Adjust column widths after initial layout
        self.frame_success.update_idletasks()
        total_width = self.accounts_treeview.winfo_width()
        self.accounts_treeview.column("Account", width=int(total_width * 0.25))
        self.accounts_treeview.column("Private Server URL", width=int(total_width * 0.35))
        self.accounts_treeview.column("Alternate Webhook URL", width=int(total_width * 0.4))


    def filter_tree(self, event=None):
        """Filtra o Treeview com base no texto de pesquisa em todos os campos da linha."""
        search_text = self.search_var.get().lower()

        # Limpa o Treeview
        for item in self.accounts_treeview.get_children():
            self.accounts_treeview.delete(item)

        # Se o filtro estiver vazio, reinserir todos os dados
        if not search_text:
            for data in self.all_data:
                account, server_url, webhook_url, enabled = data
                item_id = self.accounts_treeview.insert(
                    "", "end", values=(account, server_url, webhook_url)
                )
                self.tree_items[item_id] = (account, server_url, webhook_url)
                self.account_status[item_id] = enabled
                if not enabled:
                    self.accounts_treeview.item(item_id, tags=("disabled",))
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
                item_id = self.accounts_treeview.insert(
                    "", "end", values=(account, server_url, webhook_url)
                )
                self.tree_items[item_id] = (account, server_url, webhook_url)
                self.account_status[item_id] = enabled
                if not enabled:
                    self.accounts_treeview.item(item_id, tags=("disabled",))

    def on_double_click(self, event):
        """Permite edição das células (exceto Account) ao dar um duplo clique e alterna o status na coluna Account."""
        item_id = self.accounts_treeview.identify_row(event.y)
        if not item_id:
            return

        column_id = self.accounts_treeview.identify_column(event.x)
        column_index = int(column_id[1:]) - 1  # Colunas começam em 1 no Treeview

        # Se for a coluna "Account", alterna o status (habilitar/desabilitar)
        if column_index == 0:  # A "Account" é a coluna de índice 0
            self.toggle_account(item_id)
            self.accounts_treeview.selection_remove(
                self.accounts_treeview.selection()
            ),
        else:
            # Se for qualquer outra coluna, permite a edição
            self.on_edit(event)

    def treeview_context_menu(self, event):
        region = self.accounts_treeview.identify("region", event.x, event.y)
        if region != "cell": return  # click was not on a cell

        row_id = self.accounts_treeview.identify_row(event.y)
        if not row_id: return  # clicked on empty space

        self.accounts_treeview.selection_set(row_id) # set row as selection

        # show menu
        try:
            self.treeview_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.treeview_menu.grab_release()

    
    def toggle_account(self, item_id):
        """Ativa ou desativa uma conta, atualiza aparência visual e `self.all_data`."""
        enable = not self.account_status.get(item_id, True)  # Alterna o estado
        self.account_status[item_id] = enable

        values = list(self.accounts_treeview.item(item_id, "values"))
        account = values[0]  # "Account" é sempre o primeiro valor na linha
        section = f"{self.RWS_ACCOUNTS_SECTION_PREFIX}{account}"

        # Atualiza `self.all_data`
        for i, data in enumerate(self.all_data):
            if data[:3] == tuple(values[:3]):  # Match pelos 3 primeiros campos
                self.all_data[i] = (data[0], data[1], data[2], enable)
                break

        # Atualiza a configuração para a conta
        Config.set(section=section, key="enabled", value=str(enable))
        Config.save()

        # Atualiza o status visual no Treeview
        if enable:
            self.accounts_treeview.item(item_id, values=values, tags=())  # Remove efeito escuro
        else:
            self.accounts_treeview.item(item_id, values=values, tags=("disabled",))

    def on_edit(self, event):
        """Permite edição das células (exceto Account) ao dar um duplo clique e atualiza `self.all_data` corretamente."""
        selected_item = self.accounts_treeview.selection()
        if not selected_item:
            return

        column_id = self.accounts_treeview.identify_column(event.x)
        column_index = int(column_id[1:]) - 1  # Colunas começam em 1 no Treeview

        # Se for a coluna "Account", impedir edição
        if column_index == 0:
            return

        # Obter valores atuais da linha selecionada
        item = selected_item[0]
        values = list(self.accounts_treeview.item(item, "values"))

        # Criar um Entry para edição
        entry = ttk.Entry(self.accounts_treeview)
        entry.insert(0, values[column_index])
        entry.select_range(0, "end")
        entry.focus()

        # Posicionar o Entry sobre a célula clicada
        x, y, width, height = self.accounts_treeview.bbox(item, column_index)
        entry.place(x=x, y=y, width=width, height=height)

        def save_edit(event):
            """Salva a edição e atualiza Treeview, self.all_data e Config."""
            new_value = entry.get().strip()
            entry.destroy()

            if new_value == values[column_index]:
                return  # Nenhuma mudança foi feita

            # Atualiza o valor na linha do Treeview
            values[column_index] = new_value
            self.accounts_treeview.item(item, values=values)

            # Atualiza `self.all_data`
            for i, data in enumerate(self.all_data):
                if data[:3] == tuple(values[:3]):  # Match pelos 3 primeiros campos
                    updated_data = list(data)
                    updated_data[column_index] = new_value
                    self.all_data[i] = tuple(updated_data)
                    break

            # Salvar a edição no Config
            account = values[0]  # "Account" é sempre o primeiro valor na linha
            account_section = f"{self.RWS_ACCOUNTS_SECTION_PREFIX}{account}"

            if column_index == 1:  # Coluna 1: Server URL
                Config.set(section=account_section, key="server_url", value=new_value)
            elif column_index == 2:  # Coluna 2: Webhook URL
                Config.set(section=account_section, key="webhook_url", value=new_value)

            # Salvar o estado da conta no Config
            enabled = self.account_status.get(item, True)
            Config.set(section=account_section, key="enabled", value=str(enabled))
            Config.save()

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
        RAMWS.start_connection_checker(self.on_connection_checked)

    def fetch_accounts(self):
        """Busca as contas novamente do RAMWS e atualiza o Treeview."""
        l = self.__getLogger("fetch_accounts")
        l.debug("Fetching accounts from RAMWS...")

        def update_treeview(accounts):
            """Atualiza o Treeview com as contas recebidas."""
            self.all_data = []  # Limpa os dados anteriores
            
            # Limpa os itens existentes no Treeview
            for item in self.accounts_treeview.get_children():
                self.accounts_treeview.delete(item)

            # Para cada conta, buscamos detalhes como o server_url e webhook_url
            for account in accounts:
                # Buscando configurações no Config para cada conta
                account_section = f"{self.RWS_ACCOUNTS_SECTION_PREFIX}{account}"
                l.trace(f"Fetching config for account: {account}")
                account_status = Config.get(section=account_section, key="enabled", fallback=True)  # Assume que está habilitado se não encontrado
                l.trace(f"Account status: {account_status}")
                account_status = str(account_status).lower() == "true"
                server_url = Config.get(
                    section=account_section, key="server_url", fallback=""
                )  # Nenhum valor encontrado, será None
                webhook_url = Config.get(
                    section=account_section, key="webhook_url", fallback=""
                )  # Nenhum valor encontrado, será None

                self.all_data.append((account, server_url, webhook_url, account_status))
                
                # Inserir a conta no Treeview
                item_id = self.accounts_treeview.insert(
                    "", "end", values=(account, server_url, webhook_url)
                )
                self.tree_items[item_id] = (account, server_url, webhook_url)
                self.account_status[item_id] = (
                    account_status  # Define o status da conta conforme configurado
                )

                l.debug(
                    f"Account: {account}, Status: {account_status}, Typeof Status: {type(account_status)}"
                )
                # Atualiza a aparência dependendo do status da conta (habilitada/desabilitada)
                if not account_status:
                    l.info(f"Account: {account} is disabled.")
                    self.accounts_treeview.item(item_id, values=self.accounts_treeview.item(item_id, "values"), tags=("disabled",))

                self.all_items.append(
                    item_id
                )  # Adiciona o item à lista de todos os itens

        # Chama o método list_accounts do RAMWS
        RAMWS.list_accounts(update_treeview)
        
    def context_launch_account(self):
        selected = self.accounts_treeview.selection()
        for item_id in selected:
            account = self.accounts_treeview.item(item_id, "values")[0]
            self.launch_single_account(account)

    def context_debug_info(self):
        l = self.__getLogger("context_debug_info")
        selected = self.accounts_treeview.selection()
        for item_id in selected:
            account = self.accounts_treeview.item(item_id, "values")[0]
            
            l.debug(f"[DEBUG-CONTEXT] CSRF Token: {RAMWS.get_csrf_token(account)}")
            

    def get_account_config(self, account_name):
        """Returns a dictionary containing the configuration for the given account.

        Args:
            account_name (string): The name of the account.

        Returns:
            dict: A dictionary containing the configuration for the given account.
        """
        l = self.__getLogger("get_account_config")
        d = defaultdict(dict)
        try:
            account_section = f"{self.RWS_ACCOUNTS_SECTION_PREFIX}{account_name}"
            if not Config.has_section(account_section):
                l.error(f"Section {account_section} does not exist.")
                return d
            
            d["account_name"] = account_name
            d["is_enabled"] = str(Config.get(section=account_section, key="enabled", fallback=False).lower()) == "true"
            d["server_url"] = Config.get(section=account_section, key="server_url", fallback="")
            d["webhook_url"] = Config.get(section=account_section, key="webhook_url", fallback="")
        except Exception as e:
            l.error(f"Failed to get account config for {account_name}. Error: {e}")
            
        return d
    
    def launch_single_account(self, account_name):
        l = self.__getLogger("launch_single_account")
        try:
            account_data = self.get_account_config(account_name)
            if not account_data["is_enabled"]:
                l.warn(f"Account {account_name} is disabled.")
                return
                
            def on_success(data):
                l.info(f"Account {account_name} launched successfully.")
                l.info(f"Data: {data}")
                
            def on_fail(data):
                l.error(f"Account {account_name} failed to launch.")
                l.info(f"Data: {data}")
                
            l.trace(f"Calling RAMWS.launch_account with {account_name}")
            RAMWS.launch_account(account=account_name, placeid="15532962292", jobid=account_data["server_url"], join_vip=True, callback=lambda data: on_success(data) if data["success"] else on_fail(data))
                
        except Exception as e:
            l.error(f"Failed to launch account: {account_name}. Error: {e}")
            pass

    def launch_all_accounts(self):
        """Inicia todas as contas habilitadas."""
        l = self.__getLogger("launch_all_accounts")
        l.info("Launching all accounts...")
        for item in self.accounts_treeview.get_children():  # Pega todas as linhas do Treeview
            account = self.accounts_treeview.item(item, "values")[0]  # Pega a conta
            account_data = self.get_account_config(account)
            
            if not account_data["is_enabled"]:
                l.warn(f"Skipping account {account} as it is disabled.")
                continue  # Pula para a próxima iteração se a conta não está habilitada
            
            l.info(f"Launching account: {account}")
            
            def on_success(data):
                l.info(f"Account {account} launched successfully.")
                pass
            
            def on_fail(data):
                l.error(f"Failed to launch account {account}: {data['error']}")
                pass
            
            RAMWS.launch_account(account=account, placeid="15532962292", jobid=account_data["server_url"], join_vip=True, callback=lambda data: on_success(data) if data["success"] else on_fail(data))
            
