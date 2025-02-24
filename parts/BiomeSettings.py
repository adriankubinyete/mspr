import tkinter as tk
from tkinter import ttk
import configparser

class BiomeSettingsManager:
    def __init__(self, root, config, save_config, biomes):
        self.root = root
        self.config = config
        self.save_config = save_config
        self.biomes = biomes
        self.biome_window = None  # Janela principal de biomas

    def open_biome_config(self):
        """ Abre a janela principal de configuração de biomas. """
        if self.biome_window and tk.Toplevel.winfo_exists(self.biome_window):
            return  # Se já estiver aberta, não cria outra

        self.biome_window = tk.Toplevel(self.root)
        self.biome_window.title("Biome Settings")
        self.biome_window.geometry("300x400")
        self.biome_window.resizable(False, False)
        self.biome_window.grab_set()

        frame = ttk.Frame(self.biome_window, padding=10)
        frame.pack(fill="both", expand=True)

        for biome in self.biomes:
            ttk.Button(
                frame, text=biome,
                command=lambda b=biome: self.open_biome_settings(b),
                takefocus=False
            ).pack(fill="x", pady=2)

    def open_biome_settings(self, biome):
        """ Abre a janela de configuração específica de um bioma. """
        biome_section = biome.upper()
        if biome_section not in self.config:
            self.config[biome_section] = {}

        settings_window = tk.Toplevel(self.root)
        settings_window.title(f"Settings: {biome}")
        settings_window.geometry("300x300")
        settings_window.resizable(False, False)
        settings_window.grab_set()

        frame = ttk.Frame(settings_window, padding=10)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        check_vars = {}
        input_fields = {}

        def add_checkbox(label, key):
            """ Adiciona um checkbox e armazena sua variável """
            var = tk.IntVar(value=int(self.config[biome_section].get(key, "0")))
            check_vars[key] = var
            chk = ttk.Checkbutton(frame, takefocus=False, text=label, variable=var)
            chk.pack(anchor="w")

        def add_input(label, key, depends_on=None):
            """ Adiciona um input opcional, dependendo de um checkbox """
            entry = ttk.Entry(frame, takefocus=False, state="normal" if not depends_on or check_vars[depends_on].get() else "disabled")
            entry.insert(0, self.config[biome_section].get(key, ""))
            entry.pack(fill="x", padx=10, pady=2)
            input_fields[key] = entry

            if depends_on:
                def toggle_entry(*_):
                    entry.config(state="normal" if check_vars[depends_on].get() else "disabled")
                check_vars[depends_on].trace_add("write", toggle_entry)

        # Criando os elementos
        add_checkbox("Send Message", "send_message")
        add_checkbox("Send Ping", "send_ping")
        add_checkbox("Wait Until Finished", "wait_until_finished")
        add_checkbox("Custom Ping", "custom_ping")
        add_input("Ping Value", "ping_value", "custom_ping")
        add_checkbox("Custom Webhook", "custom_webhook")
        add_input("Webhook URL", "webhook_value", "custom_webhook")

        def save_biome_settings():
            """ Salva todas as configurações e fecha a janela """
            for key, var in check_vars.items():
                self.config[biome_section][key] = str(var.get())
            for key, entry in input_fields.items():
                self.config[biome_section][key] = entry.get()

            self.save_config()
            settings_window.destroy()
            self.biome_window.grab_set()

        ttk.Button(frame, text="Save", command=save_biome_settings, takefocus=False).pack(fill="x", pady=10)
        settings_window.protocol("WM_DELETE_WINDOW", lambda: (settings_window.destroy(), self.biome_window.grab_set()))
