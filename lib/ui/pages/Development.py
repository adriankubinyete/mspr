import logging
import tkinter as tk

from tkinter import ttk

from lib.SolsBiomeNotifier import SolsBiomeNotifier


class DevelopmentPage(ttk.Frame):
    def __init__(self, root, padx=10, pady=5):
        super().__init__(root)
        self.root = root
        self.padx = padx
        self.pady = pady

        self.CONFIG_SECTION_NAME = "__DEV"

        self._create_widgets()

    def __getLogger(self, name):
        return logging.getLogger(f"mpsr.page:Dev.{name}")

    def _create_widgets(self):
        """Main widgets"""
        frame = ttk.Frame(self, padding=(self.padx, self.pady))
        frame.pack(fill="both", expand=True)

        tk.Label(
            frame, text="Development page, please ignore!", font=("Arial", 16)
        ).pack(pady=(10, 0))

        # Lista de configurações e nomes para cada botão
        buttons_config = [
            {
                "text": "wwwwwwwwwwwwwwwwwwww",
                "name": "btn_1",
                "config": {"command": lambda: None},
            },
            {
                "text": "Button 2",
                "name": "btn_2",
                "config": {"command": SolsBiomeNotifier.test},
            },
            {"text": "Button 3", "name": "btn_3", "config": {"command": lambda: None}},
            {"text": "Button 4", "name": "btn_4", "config": {"command": lambda: None}},
            {"text": "Button 5", "name": "btn_5", "config": {"command": lambda: None}},
            {"text": "Button 6", "name": "btn_6", "config": {"command": lambda: None}},
            {"text": "Button 7", "name": "btn_7", "config": {"command": lambda: None}},
            {"text": "Button 8", "name": "btn_8", "config": {"command": lambda: None}},
            {"text": "Button 9", "name": "btn_9", "config": {"command": lambda: None}},
        ]

        button_frame = None
        for i, button in enumerate(buttons_config):
            if i % 3 == 0:
                if button_frame:
                    button_frame.pack()
                button_frame = ttk.Frame(frame)
            button_widget = ttk.Button(
                button_frame,
                width=10,
                text=button["text"],
                **button["config"],
                takefocus=False,
            )
            button_widget.pack(side="left", padx=5, pady=5)
        if button_frame:
            button_frame.pack()

    # --- funcs
