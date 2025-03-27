import tkinter as tk
from tkinter import ttk
from lib.config import Config
from lib.ui.widget.Tooltip import UIToolTip
from pynput import mouse

class UIClickAssign(ttk.LabelFrame):
    active_overlays = {}  # Guarda overlays ativos
    active_timers = {}  # Guarda timers ativos
    HIGHLIGHT_SQUARE_SIZE = 10
    HIGHLIGHT_SQUARE_THICKNESS = 2

    def __init__(self, parent, section, key, label, info=None, padx=0, pady=0, autosave=False):
        """
        Cria um campo para selecionar uma posição clicando na tela.

        :param parent: Widget pai.
        :param section: Seção no config.ini.
        :param key: Chave no config.ini.
        :param label: Texto do grupo.
        :param info: Texto informativo opcional.
        :param padx: Padding horizontal.
        :param pady: Padding vertical.
        :param autosave: Define se o valor será salvo automaticamente ao mudar.
        """
        super().__init__(parent, text=label)
        self.section = section
        self.key = key
        self.root = parent.winfo_toplevel()  # Obtém a janela principal
        self.autosave = autosave

        self.pack(fill="x", pady=pady, padx=padx, anchor="w")

        # Linha de elementos
        row_frame = ttk.Frame(self)
        row_frame.pack(fill="x", padx=5, pady=5)

        # Label X e Spinbox X
        ttk.Label(row_frame, text="X:").pack(side="left")
        self.spin_x = ttk.Spinbox(row_frame, from_=0, to=9999, width=5, command=self._on_spin_change)
        self.spin_x.pack(side="left", padx=5)

        # Label Y e Spinbox Y
        ttk.Label(row_frame, text="Y:").pack(side="left")
        self.spin_y = ttk.Spinbox(row_frame, from_=0, to=9999, width=5, command=self._on_spin_change)
        self.spin_y.pack(side="left", padx=5)

        # Botão de Info (se fornecido)
        if info:
            info_button = ttk.Label(row_frame, text="ℹ", foreground="blue", cursor="hand2")
            info_button.pack(side="right", padx=5)
            UIToolTip(info_button, info)  # 🔹 Adicionando tooltip

        # Botões Assign e Show
        self.btn_assign = ttk.Button(row_frame, text="Assign", command=self._capture_position, takefocus=False)
        self.btn_assign.pack(side="right", padx=2)

        self.btn_show = ttk.Button(row_frame, text="Show", command=self._show_position_highlight, takefocus=False)
        self.btn_show.pack(side="right", padx=2)

        # Carrega valores do config.ini
        coords = Config.get(self.section, self.key, "0,0")
        x, y = map(int, coords.split(","))
        self.spin_x.set(x)
        self.spin_y.set(y)

    def _remove_all_highlights(self):
        """ Remove todos os overlays e timers ativos. """
        for key in list(self.active_overlays.keys()):
            self.active_overlays[key].destroy()
        self.active_overlays.clear()

        for key in list(self.active_timers.keys()):
            self.root.after_cancel(self.active_timers[key])
        self.active_timers.clear()

    def _remove_highlight(self):
        """ Remove o overlay e timer do próprio elemento. """
        if self.key in self.active_overlays:
            self.active_overlays[self.key].destroy()
            del self.active_overlays[self.key]

        if self.key in self.active_timers:
            self.root.after_cancel(self.active_timers[self.key])
            del self.active_timers[self.key]

    def _show_position_highlight(self, duration=5000):
        """ Exibe um quadrado vermelho na posição atual por DURATION ms. """
        try:
            x = int(self.spin_x.get())
            y = int(self.spin_y.get())
        except ValueError:
            return  # Sai silenciosamente se os valores forem inválidos

        self._remove_highlight()  # Remove overlay antigo se houver

        size = self.HIGHLIGHT_SQUARE_SIZE
        border = self.HIGHLIGHT_SQUARE_THICKNESS
        offset = size // 2  # Centraliza o quadrado

        # Criando a janela do overlay
        overlay = tk.Toplevel(self.root)
        overlay.overrideredirect(True)
        overlay.geometry(f"{size}x{size}+{x-offset}+{y-offset}")
        overlay.attributes("-transparentcolor", "black")
        overlay.configure(bg="black")

        # Criando a borda vermelha
        border_frame = tk.Frame(overlay, bg="red", width=size, height=size)
        border_frame.place(x=0, y=0)

        # Criando o buraco interno para simular a borda
        inner_frame = tk.Frame(
            overlay, bg="black",
            width=size - (2 * border),
            height=size - (2 * border)
        )
        inner_frame.place(x=border, y=border)

        # Registrando overlay e timer
        self.active_overlays[self.key] = overlay
        self.active_timers[self.key] = self.root.after(duration, self._remove_highlight)


    def _capture_position(self):
        """ Captura a posição do mouse ao clicar e salva. """
        self._remove_highlight()
        self.btn_assign.config(text="Click...", state="disabled")

        def on_click(x, y, button, pressed):
            if pressed:
                self.spin_x.set(x)
                self.spin_y.set(y)
                
                if self.autosave:
                    self.save()

                listener.stop()
                self.btn_assign.config(text="Assign", state="normal")

        listener = mouse.Listener(on_click=on_click)
        listener.start()

    def _on_spin_change(self):
        """ Callback para quando os valores dos spinboxes mudam. """
        if self.autosave:
            self.save()

    def save(self):
        """ Salva manualmente os valores no Config. """
        x = self.spin_x.get()
        y = self.spin_y.get()
        Config.set(self.section, self.key, f"{x},{y}")
        Config.save()
