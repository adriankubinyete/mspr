import tkinter as tk
from tkinter import ttk, messagebox
from lib.config import Config  # Importando seu ConfigManager

class MultiAccountApp:
    def __init__(self, root):
        self.previous_global_webhook = ''
        
        self.root = root
        self.root.title("Account Manager")
        self.root.geometry("750x450")

        # 🔹 Frame para alinhar os elementos na mesma linha
        self.top_frame = tk.Frame(root)
        self.top_frame.pack(pady=5, padx=10, fill="x")

        # 🔹 Label Webhook Global
        tk.Label(self.top_frame, text="Discord Webhook Global:").pack(side="left", padx=5)

        # 🔹 Campo de entrada do Webhook Global
        self.entry_global_webhook = tk.Entry(self.top_frame, width=40)
        self.entry_global_webhook.pack(side="left", padx=5)

        # 🔹 Botão para salvar o Webhook Global
        self.btn_save_webhook = tk.Button(self.top_frame, text="Save Global Webhook", command=self.save_global_webhook)
        self.btn_save_webhook.pack(side="left", padx=5)

        # 🔹 Outro botão que vai fazer outra coisa
        self.btn_other_action = tk.Button(self.top_frame, text="Import RAM Accounts", command=self.other_action)
        self.btn_other_action.pack(side="left", padx=5)

        # Carrega o Webhook Global do Config
        self.entry_global_webhook.insert(0, Config.get("General", "url_webhook", fallback=""))

        # 🔹 Criando a Treeview
        self.tree = ttk.Treeview(root, columns=("Account Name", "Private Server URL", "Discord Webhook URL"), show="headings")

        # Definição de cabeçalhos
        self.tree.heading("Account Name", text="Account Name", anchor="center")
        self.tree.heading("Private Server URL", text="Private Server URL", anchor="center")
        self.tree.heading("Discord Webhook URL", text="Discord Webhook URL", anchor="center")

        # Ajustando tamanho das colunas
        self.tree.column("Account Name", width=150, anchor="center")
        self.tree.column("Private Server URL", width=200, anchor="center")
        self.tree.column("Discord Webhook URL", width=200, anchor="center")

        self.load_accounts()
        self.tree.pack(pady=10, fill="both", expand=True)

        # 🔹 Criando menu de contexto (botão direito)
        self.menu = tk.Menu(self.root, tearoff=0)
        self.menu.add_command(label="Add new", command=self.add_account)
        self.menu.add_command(label="Edit", command=self.edit_selected)
        self.menu.add_command(label="Remove", command=self.remove_selected)

        # Vinculando clique direito ao Treeview
        self.tree.bind("<Button-3>", self.show_context_menu)

    def other_action(self):
        print(f"bop")
        pass

    def save_global_webhook(self):
        """Salva o webhook global e atualiza todas as contas que o utilizavam."""
        new_webhook = self.entry_global_webhook.get().strip()
        
        if not new_webhook:
            messagebox.showerror("Erro", "O Webhook Global não pode estar vazio!")
            return

        # Atualiza o Webhook Global no ConfigManager
        Config.set("General", "url_webhook", new_webhook)
        Config.save()

        # Atualiza as contas que estavam usando o Webhook Global
        updated_accounts = 0
        for section in Config.get_sections():
            if section.startswith("RAM_"):
                print(f"Verificando se a seção {section} utiliza o Webhook Global...")
                section_webhook = Config.get(section, "discord_webhook_url", fallback=None)
                if section_webhook and section_webhook != new_webhook:
                    Config.set(section, "discord_webhook_url", new_webhook)
                    updated_accounts += 1


        if updated_accounts > 0:
            Config.save()
            self.refresh_tree()  # Atualiza a Treeview para refletir as mudanças

        # Atualiza o valor armazenado do Webhook Global anterior
        self.previous_global_webhook = new_webhook

        messagebox.showinfo("Sucesso", f"Webhook Global atualizado!\n{updated_accounts} contas foram modificadas.")

    def refresh_tree(self):
        """Recarrega a Treeview com os dados atualizados."""
        self.tree.delete(*self.tree.get_children())  # Limpa todos os itens
        self.load_accounts()  # Recarrega os dados do ConfigManager para a Treeview


    def load_accounts(self):
        """Carrega as contas do ConfigManager para a Treeview."""
        for section in Config.get_sections():
            if section.startswith("RAM_"):
                account_name = section[4:]  # Remove o prefixo "RAM_"
                private_url = Config.get(section, "private_server_url", fallback="")
                webhook_url = Config.get(section, "discord_webhook_url", fallback="")
                self.tree.insert("", "end", values=(account_name, private_url, webhook_url))

    def show_context_menu(self, event):
        """Exibe o menu de contexto no local do clique."""
        selected_item = self.tree.identify_row(event.y)
        self.tree.selection_set(selected_item)

        # Ativa ou desativa opções conforme há item selecionado
        self.menu.entryconfig("Edit", state="normal" if selected_item else "disabled")
        self.menu.entryconfig("Remove", state="normal" if selected_item else "disabled")

        self.menu.post(event.x_root, event.y_root)  # Exibe o menu no mouse

    def open_account_modal(self, old_name=None, default_private_url="", default_webhook=""):
        """Abre um modal para adicionar ou editar uma conta."""
        modal = tk.Toplevel(self.root)
        modal.title("Add/Edit Account")
        modal.geometry("400x300")
        modal.transient(self.root)
        modal.grab_set()

        tk.Label(modal, text="Account Name:").pack(pady=5)
        entry_name = tk.Entry(modal)
        entry_name.insert(0, old_name if old_name else "")
        entry_name.pack()

        tk.Label(modal, text="Private Server URL:").pack(pady=5)
        entry_private_url = tk.Entry(modal)
        entry_private_url.insert(0, default_private_url)
        entry_private_url.pack()

        tk.Label(modal, text="Discord Webhook URL:").pack(pady=5)
        entry_webhook = tk.Entry(modal)
        entry_webhook.insert(0, default_webhook)
        entry_webhook.pack()

        # 🔹 Checkbox para usar o Webhook Global
        use_global_var = tk.BooleanVar()
        checkbox_use_global = tk.Checkbutton(modal, text="Use Global Webhook?", variable=use_global_var)
        checkbox_use_global.pack(pady=5)

        def save():
            name = entry_name.get().strip()
            private_url = entry_private_url.get().strip()
            webhook_url = self.entry_global_webhook.get().strip() if use_global_var.get() else entry_webhook.get().strip()

            if not name or not private_url or not webhook_url:
                messagebox.showerror("Erro", "Todos os campos são obrigatórios!")
                return

            section = f"RAM_{name}"

            if old_name is None:
                # Adiciona nova conta
                Config.set(section, "private_server_url", private_url)
                Config.set(section, "discord_webhook_url", webhook_url)
                Config.save()
                self.tree.insert("", "end", values=(name, private_url, webhook_url))
            else:
                # Atualiza conta existente
                old_section = f"RAM_{old_name}"
                if old_section != section:
                    Config.config[section] = Config.config.pop(old_section)  # Renomeia a seção
                
                Config.set(section, "private_server_url", private_url)
                Config.set(section, "discord_webhook_url", webhook_url)
                Config.save()

                for item in self.tree.get_children():
                    values = self.tree.item(item, "values")
                    if values and values[0] == old_name:
                        self.tree.item(item, values=(name, private_url, webhook_url))
                        break

            modal.destroy()

        tk.Button(modal, text="Save", command=save).pack(pady=10)

    def add_account(self):
        """Abre o modal para adicionar uma nova conta."""
        self.open_account_modal()

    def edit_selected(self):
        """Abre o modal para editar a conta selecionada."""
        selected_item = self.tree.selection()
        if not selected_item:
            return

        item_values = self.tree.item(selected_item, "values")
        name, private_url, webhook_url = item_values
        self.open_account_modal(name, private_url, webhook_url)

    def remove_selected(self):
        """Remove a conta selecionada."""
        selected_item = self.tree.selection()
        if selected_item:
            item_values = self.tree.item(selected_item, "values")
            name = item_values[0]

            self.tree.delete(selected_item)
            Config.config.remove_section(f"RAM_{name}")
            Config.save()

if __name__ == "__main__":
    root = tk.Tk()
    app = MultiAccountApp(root)
    root.mainloop()
