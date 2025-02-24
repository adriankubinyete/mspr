import tkinter as tk
from tkinter import ttk
import configparser
from parts.BiomeSettings import BiomeSettingsManager
from parts.CalibrationSettings import CalibrationSettingsManager

class App:
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read("config.ini")

        self.biomes = [
            "GLITCHED", "DREAM SPACE", "GRAVEYARD", "PUMPKIN MOON", "NULL", "SAND STORM",
            "CORRUPTION", "STARFALL", "HELL", "RAINY", "SNOWY", "WINDY"
        ]

        # Criar a janela principal
        self.root = tk.Tk()
        self.root.title("MSPR: Masutty's Private Server Resetter")
        self.root.geometry("400x250")
        self.root.minsize(400, 250)

        self.create_widgets()
        self.root.mainloop()

    def create_widgets(self):
        """Cria todos os elementos da interface."""
        frame = ttk.Frame(self.root, padding=10)
        frame.pack(fill="both", expand=True)

        # Entrada do Webhook
        row_webhook = ttk.Frame(frame)
        row_webhook.pack(fill="x", pady=2)
        ttk.Label(row_webhook, text="Discord Webhook : ").pack(side="left")
        self.entry_webhook = ttk.Entry(row_webhook)
        self.entry_webhook.pack(side="right", fill="x", expand=True)

        # Entrada do Private Server
        row_pvt = ttk.Frame(frame)
        row_pvt.pack(fill="x", pady=2)
        ttk.Label(row_pvt, text="Private Server Link : ").pack(side="left")
        self.entry_pvt = ttk.Entry(row_pvt)
        self.entry_pvt.pack(side="right", fill="x", expand=True)

        # Botões de Configuração
        row_config = ttk.Frame(frame)
        row_config.pack(fill="x", pady=10)

        self.biome_manager = BiomeSettingsManager(self.root, self.config, self.save_config, self.biomes)
        self.btn_biome_settings = ttk.Button(row_config, text="Biome settings", command=self.biome_manager.open_biome_config, takefocus=False)
        self.btn_biome_settings.pack(side="top", fill="x")

        self.calibration_manager = CalibrationSettingsManager(self.root, self.config, self.save_config)
        self.btn_screen_settings = ttk.Button(row_config, text="Screen settings", command=self.calibration_manager.open_calibration_config, takefocus=False)
        self.btn_screen_settings.pack(side="top", fill="x")

        # Botões Iniciar e Parar
        row_start_stop = ttk.Frame(frame)
        row_start_stop.pack(fill="x", side="bottom", pady=5)

        self.btn_start = ttk.Button(row_start_stop, text="Start", style="Primary.TButton", command=self.start_app, takefocus=False)
        self.btn_start.pack(side="left", fill="x", expand=True)

        self.btn_stop = ttk.Button(row_start_stop, text="Stop", style="Danger.TButton", command=self.stop_app, takefocus=False)
        self.btn_stop.pack(side="right", fill="x", expand=True)

    def save_config(self):
        """Salva configurações no config.ini"""
        with open("config.ini", "w") as configfile:
            self.config.write(configfile)

    def toggle_controls(self, state: bool):
        """Ativa/desativa os controles para impedir mudanças enquanto o app está rodando."""
        new_state = "normal" if state else "disabled"

        self.entry_webhook.config(state=new_state)
        self.entry_pvt.config(state=new_state)
        self.btn_start.config(state=new_state)
        self.btn_biome_settings.config(state=new_state)
        self.btn_screen_settings.config(state=new_state)

    def start_app(self):
        """Inicia a execução e desativa os controles"""
        self.toggle_controls(False)  # Desativa os botões e inputs
        print("Aplicação iniciada!")  # Aqui você adiciona o que for necessário para rodar

    def stop_app(self):
        """Para a execução e reativa os controles"""
        self.toggle_controls(True)  # Reativa os botões e inputs
        print("Aplicação parada!")

# Executa o app
if __name__ == "__main__":
    App()
