import logging
import time
import tkinter as tk

from tkinter import ttk

import autoit
import pyautogui
import pygetwindow as gw


def press(key: str, hold: int = 0):
    """
    Pressiona uma tecla usando pyautoit.

    :param key: Nome da tecla (ex: 'space', 'enter', 'a', etc).
    :param hold: Tempo em milissegundos para manter a tecla pressionada.
    """
    special_keys = {
        "space": "SPACE",
        "enter": "ENTER",
        "ctrl": "CTRL",
        "shift": "SHIFT",
        "alt": "ALT",
        "tab": "TAB",
        "esc": "ESCAPE",
        "delete": "DELETE",
        "backspace": "BACKSPACE",
        "up": "UP",
        "down": "DOWN",
        "left": "LEFT",
        "right": "RIGHT",
    }

    autoit_key = special_keys.get(key.lower(), key.upper())

    if hold > 0:
        autoit.send(f"{{{autoit_key} down}}")
        time.sleep(hold / 1000)
        autoit.send(f"{{{autoit_key} up}}")
    else:
        autoit.send(f"{{{autoit_key}}}")


class TabManagerPage(ttk.Frame):
    def __init__(self, root, padx=10, pady=5):
        super().__init__(root)
        self.root = root
        self.padx = padx
        self.pady = pady

        self.TABMANAGER_SECTION = "CONFIG_TABMANAGER"

        self._create_widgets()

    def __getLogger(self, name):
        return logging.getLogger(f"mpsr.page:TabManager.{name}")

    def _create_widgets(self):
        """Cria os widgets principais, mas não os frames de sucesso/erro."""
        frame = ttk.Frame(self, padding=(self.padx, self.pady))
        frame.pack(fill="both", expand=True)

        tk.Label(
            frame, text="⚠️ THIS PAGE IS IN DEVELOPMENT! ⚠️", font=("Arial", 16)
        ).pack(pady=(10, 0))

        # Frame para os campos de entrada (Gap X, Gap Y, Delay Clicks e botões)
        input_frame = ttk.Frame(frame)
        input_frame.pack(pady=10)

        # Gap X
        gapx_frame = ttk.Frame(input_frame)
        gapx_frame.pack(side="left", padx=10)
        tk.Label(gapx_frame, text="Gap X:").pack()
        self.entry_gapx = tk.Entry(gapx_frame, width=5)
        self.entry_gapx.insert(0, "100")
        self.entry_gapx.pack()

        # Gap Y
        gapy_frame = ttk.Frame(input_frame)
        gapy_frame.pack(side="left", padx=10)
        tk.Label(gapy_frame, text="Gap Y:").pack()
        self.entry_gapy = tk.Entry(gapy_frame, width=5)
        self.entry_gapy.insert(0, "100")
        self.entry_gapy.pack()

        # Delay Clicks
        delay_frame = ttk.Frame(input_frame)
        delay_frame.pack(side="left", padx=10)
        tk.Label(delay_frame, text="Delay Clicks:").pack()
        self.entry_delay = tk.Entry(delay_frame, width=5)
        self.entry_delay.insert(0, "250")
        self.entry_delay.pack()

        # Botão: Atualizar
        update_button = ttk.Button(
            input_frame, text="Update Apps", command=self.update_window_list
        )
        update_button.pack(side="left", padx=10, pady=(13, 0))  # padding top p alinhar

        # Botão: Organizar
        tile_button = ttk.Button(
            input_frame, text="Tile my windows!", command=self.tile_windows
        )
        tile_button.pack(side="left", padx=10, pady=(13, 0))

        # Lista de janelas
        self.window_listbox = tk.Listbox(
            frame, selectmode=tk.MULTIPLE, width=60, height=10
        )
        self.window_listbox.pack(pady=5)

        debug_frame = ttk.Frame(frame)
        debug_frame.pack(fill="x")

        self.entry_delay_start = tk.Entry(debug_frame, width=5)
        tk.Label(debug_frame, text="Delay Start:").pack(side="left", padx=5)
        self.entry_delay_start.pack(side="left", padx=5)
        self.entry_delay_start.insert(0, "0")

        self.entry_key = tk.Entry(debug_frame, width=5)
        tk.Label(debug_frame, text="Key:").pack(side="left", padx=5)
        self.entry_key.pack(side="left")
        self.entry_key.insert(0, "space")

        self.entry_hold = tk.Entry(debug_frame, width=5)
        tk.Label(debug_frame, text="Hold (ms):").pack(side="left", padx=5)
        self.entry_hold.pack(side="left", padx=5)
        self.entry_hold.insert(0, "250")

    # --- funcs

    def get_window_list(self):
        return [
            (window, window.title)
            for window in gw.getWindowsWithTitle("")
            if window.title.strip()
        ]

    def update_window_list(self):
        self.window_listbox.delete(0, tk.END)
        windows = [
            (window, window.title.strip())
            for window in gw.getWindowsWithTitle("")
            if window.title.strip()
        ]
        self.windows = sorted(
            windows, key=lambda item: item[1].lower()
        )  # ordena por título

        for _, title in self.windows:
            self.window_listbox.insert(tk.END, title)

    def tile_windows(self):
        """Organiza as janelas de acordo com o padrão solicitado."""
        try:
            selected_indices = self.window_listbox.curselection()
            selected_windows = [self.windows[i][0] for i in selected_indices]

            if not selected_windows:
                print("No window selected.")
                return

            # Obtém o tamanho do monitor
            screen_width, _ = pyautogui.size()
            gap_x = int(self.entry_gapx.get())
            gap_y = int(self.entry_gapy.get())
            delay_between_clicks = int(self.entry_delay.get())

            # debug, remove this
            delay_start = int(self.entry_delay_start.get())
            hold_duration = int(self.entry_hold.get())
            key = self.entry_key.get()

            print(f"delay_start: {delay_start}")
            time.sleep(delay_start)

            # Configurações iniciais
            x, y = 20, 20
            max_x = screen_width  # Apenas verifica o limite da tela

            # for window in selected_windows:
            for i in range(len(selected_windows)):
                window = selected_windows[i]

                try:
                    if window.isMaximized:
                        window.restore()  # Sai do full screen

                    # 🔹 Força a janela para 800x600 antes de organizar
                    window.resizeTo(800, 600)

                    # Move a janela para a posição calculada
                    window.moveTo(x, y)
                    window.activate()  # Traz a janela para o topo

                    # keep-alive
                    press(key, hold=hold_duration)  # 250ms ideal value

                    # Atualiza X para a próxima janela
                    x += gap_x

                    # Se não couber mais na linha, desce GAP_Y pixels e reinicia X
                    if x > max_x:
                        x = 20
                        y += gap_y

                except Exception as e:
                    print(f"Error moving window {window.title}: {e}")

                # if its not the last window, wait a bit
                print(f"Iteration {i + 1} of {len(selected_windows)}")
                if i < len(selected_windows) - 1:
                    print("Sleeping")
                    time.sleep(delay_between_clicks / 1000)  # Delay em segundos

            print("Windows tiled!")
        except Exception as e:
            print(f"Error trying to tile windows. :: {e}")
