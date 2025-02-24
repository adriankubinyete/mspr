import tkinter as tk
from tkinter import ttk
import configparser
from pynput import mouse


class CalibrationSettingsManager:
    def __init__(self, root, config, save_config, section_name="Calibragem"):
        self.root = root
        self.config = config
        self.save_config = save_config
        self.section_name = section_name
        self.calibration_window = None  # Referência à janela
        self.position_options = [  # Define todas as opções fixas aqui
            ("Inventory button", "inventory_button"),
            ("Items button", "items_button"),
            ("Gears button", "gears_button"),
            ("Inventory search bar", "inventory_search"),
            ("First item", "first_item"),
            ("Item use amount", "item_quantity"),
            ("Item use button", "use_button"),
        ]

        if self.section_name not in self.config:
            self.config[self.section_name] = {}

    def open_calibration_config(self):
        """ Abre o modal de configuração de calibragem. """
        if self.calibration_window is not None and tk.Toplevel.winfo_exists(self.calibration_window):
            return  # Se a janela já estiver aberta, não cria outra

        self.calibration_window = tk.Toplevel(self.root)
        self.calibration_window.title("Screen Calibration Settings")
        self.calibration_window.geometry("350x400")  # Aumentei um pouco para caber o botão de Save
        self.calibration_window.resizable(False, False)
        self.calibration_window.grab_set()

        self.frame = ttk.Frame(self.calibration_window, padding=10)
        self.frame.pack(fill="both", expand=True)

        # Criar os botões de posição ao abrir a janela
        for display_name, internal_name in self.position_options:
            self._create_position_button(display_name, internal_name)

        # Adicionar botão de salvar no final
        save_button = ttk.Button(self.calibration_window, text="Save", command=self.save_and_close, takefocus=False)
        save_button.pack(fill="x", padx=10, pady=5)  # Adiciona um espaço abaixo dos botões

    def _create_position_button(self, display_name, internal_name):
        """ Cria um botão para captura de posição dentro da janela aberta. """
        row = ttk.Frame(self.frame)
        row.pack(fill="x", pady=2)

        ttk.Label(row, text=display_name).pack(side="left")

        coords = self.config[self.section_name].get(internal_name, "<Unset>")
        label_coords = ttk.Label(row, text=coords, width=12)
        label_coords.pack(side="left", padx=5)

        btn_capture = ttk.Button(row, text="Grab position", takefocus=False)
        btn_capture.pack(side="right")
        btn_capture.config(command=lambda: self.capture_position(internal_name, label_coords, btn_capture))

    def capture_position(self, option, label, button):
        """ Captura a posição do mouse ao clicar. """
        button.config(text="Click...", state="disabled", takefocus=False)

        def on_click(x, y, button_pressed, pressed):
            if pressed:  # Captura apenas no pressionamento do botão
                label.config(text=f"{x}, {y}")
                self.config[self.section_name][option] = f"{x},{y}"
                listener.stop()  # Para o listener
                button.config(text="Grab position", state="normal", takefocus=False)

        listener = mouse.Listener(on_click=on_click)
        listener.start()

    def save_and_close(self):
        """ Salva a configuração e fecha a janela. """
        self.save_config()
        if self.calibration_window:
            self.calibration_window.destroy()
            self.calibration_window = None
