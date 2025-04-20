import tkinter as tk
import logging
from tkinter import ttk
from pynput import mouse
from lib.config import Config

class BaseModal:
    def __init__(self, root, width, height, title, resizeable=False, section_name="debug"):
        # === Menu initialization
        self.root = root 
        self.modal = None # the modal window
        self.section_name = section_name
        
        # === Menu customization parameters
        self.LOG_NAME = f"mpsr.Modal.{self.section_name}" # dont forget to name your log.
        self.WINDOW_TITLE =  title
        self.WINDOW_IS_RESIZABLE = resizeable
        self.WINDOW_WIDTH = width
        self.WINDOW_HEIGHT = height
        self.SYMBOL_LABEL_INFO = "❓"
        self.SAVE_BUTTON = True # Should the save button be created? Generally yes. Useful for intermediate of submodals.
        # ===
        
        # === CLICKASSIGN // make_ui_click_assign
        self.active_overlays = {} # dict to store multiple overlays
        self.active_timers = {} # dict to store IDs of timers
        self.HIGHLIGHT_SQUARE_SIZE = 10
        self.HIGHLIGHT_SQUARE_THICKNESS = 2

        # === ENTRY // make_ui_entry
        self.entries_to_save = {} # dict to store multiple entries

        # if not Config.has_section(self.section_name):
        #     Config.add_section(self.section_name)

    def _getLogger(self, name):
        return logging.getLogger(f"{self.LOG_NAME}.{name}")

    def __on_window_closed_manually(self):
        """ Cancels overlays and timers, and close the window (without saving). """
        self._click_assign_remove_all_highlights()
        self.modal.destroy()
        self.modal = None

    def _widgets(self, parent):
        """ Method that needs to be overwritten with actual widgets. """
        raise NotImplementedError("This method needs to be overwritten. You should build your interface here. The first argument is the parent frame on which your interface will be built.")
    
    def open(self):
        """ Starts this modal. """
        l = self._getLogger('open')
        l.trace('Reading configuration file')
        Config.load()
        if hasattr(self, 'modal_root') and self.modal and tk.Toplevel.winfo_exists(self.modal):
            return  
        
        self.modal = tk.Toplevel(self.root)
        self.modal.title(self.WINDOW_TITLE)
        self.modal.resizable(self.WINDOW_IS_RESIZABLE, self.WINDOW_IS_RESIZABLE)
        self.modal.grab_set()
        self.modal.protocol("WM_DELETE_WINDOW", self.__on_window_closed_manually)  # window closed manually
        # self.modal.configure(bg="blue")

        self.frame = ttk.Frame(self.modal, padding=10)
        self.frame.pack(fill="both", expand=True)
        
        # do we pass frame or modal? lol
        self._widgets(self.frame)
        
        # # === 🔥TEST ENTRY
        # ui_entry_section = ttk.LabelFrame(self.frame, text="Webhook URL", padding=0)
        # ui_entry_section.pack(fill="both", expand=True)
        
        # ui_entry_frame = ttk.Frame(ui_entry_section)
        # ui_entry_frame.pack(fill="both", expand=True, padx=5, pady=6)
        
        # self.make_ui_entry(parent=ui_entry_frame, label="Batata:", key="batata", info="This is just an example.")
        # self.make_ui_entry(parent=ui_entry_frame, label="Frita:", key="frita", info="This is just an example.")
        
        # # === 🔥TEST ENTRY
        # self.make_ui_toggleable_entry(padx=PADX_MUI, pady=(15, PADY_MUI), parent=self.frame, label="Webhook URL:", key="webhook_url", info="Discord webhook to send notifications to.\nYou can set multiple webhooks by separating them with a comma, no spaces.")
        # self.make_ui_toggleable_entry(padx=PADX_MUI, pady=PADY_MUI, parent=self.frame, label="Private Server:", key="username", info="The URL to your private server. It can be a privateServerLinkCode or a share link, both works.")
        
        # # === TEST CHECKBOX
        # self.make_ui_checkbox(parent=self.frame, label="Pop heavenlies?", key="should_pop_heavenly", info="If you should pop all your heavenly potions.")
        
        
        if self.SAVE_BUTTON:
            save_button = ttk.Button(self.modal, text="Save", command=self.save_and_close, takefocus=False)
            save_button.pack(fill="x", padx=10, pady=5)  
        else:
            l.debug("The save button won't be created.")

        
        
        # automatic height
        if str(self.WINDOW_HEIGHT).lower().upper() == "AUTO":
            self.modal.geometry(f"{self.WINDOW_WIDTH}x1")  # Altura mínima inicial
            self.modal.update_idletasks()  # Atualiza para calcular o tamanho correto
            self.modal.geometry(f"{self.WINDOW_WIDTH}x{self.modal.winfo_reqheight()}")  # Ajusta para altura necessária
        else:
            self.modal.geometry(f"{self.WINDOW_WIDTH}x{self.WINDOW_HEIGHT}")

    def save_and_close(self):
        """ Cancels overlays and timers, saves the configuration and closes the window. """
        self._click_assign_remove_all_highlights()

        # here we need to get every user data that was entered in the UI, and send them to the config object.
        self._extract_values_from_entries() # get values from entries and put them into Config
        
        # here we will save the config object to file
        Config.save()
        self.modal.destroy()
        self.modal = None
        
        # Verifica se há outro modal ativo para restaurar o foco
        if isinstance(self.root, tk.Toplevel):  
            self.root.grab_set()  # Mantém o foco no modal pai
            self.root.focus_set()
        else:
            self.root.focus_set()  # Se não for modal, volta o foco pro principal
    
    def close(self):
        """ Cancels overlays and timers, and close the window (without saving). """
        self._click_assign_remove_all_highlights()
        self.modal.destroy()
        self.modal = None

        # Verifica se há outro modal ativo para restaurar o foco
        if isinstance(self.root, tk.Toplevel):
            self.root.grab_set()  # Mantém o foco no modal pai
            self.root.focus_set()
        else:
            self.root.focus_set()  # Se não for modal, volta o foco pro principal
    
    # === INPUT BUILDER CORE ===
    
    def _add_tooltip(self, widget, text):
        """
        Adds a tooltip to widget when hovered.
        Example:
            info_button = ttk.Label(row_frame, text="[hover me]", foreground="blue", cursor="hand2")
            info_button.pack()
            self._add_tooltip(info_button, "Hello, tooltip world!")
        """
        tooltip = tk.Toplevel(widget)
        tooltip.withdraw()  # Esconde por padrão
        tooltip.overrideredirect(True)  # Remove bordas da janela
        tooltip.geometry("+0+0")
        label = ttk.Label(tooltip, text=text, relief="solid", borderwidth=1, font=("Arial", 9))
        label.pack(ipadx=5, ipady=2)

        def show_tooltip(event):
            x = widget.winfo_rootx() + 20
            y = widget.winfo_rooty() + 20
            tooltip.geometry(f"+{x}+{y}")
            tooltip.deiconify()

        def hide_tooltip(event):
            tooltip.withdraw()

        widget.bind("<Enter>", show_tooltip)
        widget.bind("<Leave>", hide_tooltip)

    def _click_assign_remove_all_highlights(self):
        """ Related to 'make_ui_click_assign'. Remove every overlay and timer from clickassign. """
        for option in list(self.active_overlays.keys()):
            self.active_overlays[option].destroy()
        self.active_overlays.clear()
        
        for option in list(self.active_timers.keys()):
            self.root.after_cancel(self.active_timers[option])
        self.active_timers.clear()
    
    def _click_assign_remove_highlight(self, option):
        """ Related to 'make_ui_click_assign'. Remove a specific overlay and timer from clickassign. """
        if option in self.active_overlays:
            self.active_overlays[option].destroy()
            del self.active_overlays[option]

        if option in self.active_timers:
            self.root.after_cancel(self.active_timers[option])
            del self.active_timers[option]
    
    def _click_assign_show_position_highlight(self, option, duration=5000):
        """ Shows a red square at the saved position for DURATION miliseconds. """
        
        coords = Config.get(self.section_name, option, fallback=None)
        if not coords or coords == "<Unset>":
            return
        
        # check if the overlay is already active
        if option in self.active_overlays:
            self._click_assign_remove_highlight(option)            

        try:
            x, y = map(int, coords.split(","))
        except ValueError:
            return

        size = self.HIGHLIGHT_SQUARE_SIZE
        border_thickness = self.HIGHLIGHT_SQUARE_THICKNESS
        offset = size // 2  # centers the square

        # Criando a janela do overlay
        overlay = tk.Toplevel(self.root)
        overlay.overrideredirect(True)
        overlay.geometry(f"{size}x{size}+{x-offset}+{y-offset}")

        # make window transparent
        overlay.attributes("-transparentcolor", "black")

        # black transparent hole
        overlay.configure(bg="black")

        # border alongside the hole
        border_frame = tk.Frame(overlay, bg="red", width=size, height=size)
        border_frame.place(x=0, y=0)

        # internal hole to simulate border
        inner_frame = tk.Frame(
            overlay,
            bg="black",
            width=size - (2 * border_thickness),
            height=size - (2 * border_thickness)
        )
        inner_frame.place(x=border_thickness, y=border_thickness)

        # register overlay
        self.active_overlays[option] = overlay
        # timer to remove after duration
        self.active_timers[option] = self.root.after(duration, lambda: self._click_assign_remove_highlight(option))
    
    def _click_assign_capture_position(self, option, spin_x, spin_y, btn_assign):
        """ Related to 'make_ui_click_assign'. Captures a position on click. """
        self._click_assign_remove_highlight(option)
        btn_assign.config(text="Click...", state="disabled", takefocus=False)
        original_title = self.modal.title()
        self.modal.title(f"{original_title} - Click to assign position")

        def on_click(x, y, button_pressed, pressed):
            if pressed:  
                spin_x.set(x)
                spin_y.set(y)
                Config.set(self.section_name, option, f"{x},{y}")
                listener.stop()  
                btn_assign.config(text="Assign", state="normal", takefocus=False)
                self.modal.title(original_title)
                # self._click_assign_show_position_highlight(option, duration=3000) # this doesnt work. why?

        listener = mouse.Listener(on_click=on_click)
        listener.start()
    
    def _extract_values_from_entries(self):
        """ Saves all entries in the config file. """
        for key, entry_var in self.entries_to_save.items():
            if isinstance(entry_var, tk.BooleanVar):
                # Se for um checkbox, converte para string
                Config.set(self.section_name, key, str(int(entry_var.get())))
            elif isinstance(entry_var, tuple) and all(isinstance(var, tk.IntVar) for var in entry_var):  
                # Se for um Box Assign (x, y, w, h), salva como string "x,y,w,h"
                Config.set(self.section_name, key, ",".join(str(var.get()) for var in entry_var))
            else:
                Config.set(self.section_name, key, entry_var.get())
    
    #  ==== USER INPUT BUILDERS ====
    
    def make_ui_click_assign(self, parent, label, info, key, padx=0, pady=0):
        """ Makes a position selector, with all its utilitaries (show selection, assign new, etc). """
        l = self._getLogger('make_ui_click_assign')

        # entire section padding
        PADDING_X = padx
        PADDING_Y = pady
        
        # internal paddings
        SPACING_BETWEEN_ELEMENTS = 0
        SPACING_BETWEEN_SPINBOXES = 5
        SPACING_BETWEEN_BUTTONS = 2
        INTERNAL_SPACING = 5

        # === Seção principal que envolve tudo ===
        section = ttk.LabelFrame(parent, text=label)  # Usa o próprio label como título da seção
        section.pack(fill="x", pady=PADDING_Y, padx=PADDING_X, anchor="w")

        # === Linha única: X, Y, Info, Show e Assign ===
        row_frame = ttk.Frame(section)
        row_frame.pack(fill="x", padx=INTERNAL_SPACING, pady=(0, INTERNAL_SPACING))

        # Label X e Spinbox X
        ttk.Label(row_frame, text="X :").pack(side="left", padx=(0, SPACING_BETWEEN_ELEMENTS))
        spin_x = ttk.Spinbox(row_frame, from_=0, to=9999, width=5)
        spin_x.pack(side="left", padx=(0, SPACING_BETWEEN_SPINBOXES))

        # Label Y e Spinbox Y
        ttk.Label(row_frame, text="Y :").pack(side="left", padx=(0, SPACING_BETWEEN_ELEMENTS))
        spin_y = ttk.Spinbox(row_frame, from_=0, to=9999, width=5)
        spin_y.pack(side="left")
        
        # Botão de Info (ⓘ) good: ❓❔
        info_button = ttk.Label(row_frame, text=self.SYMBOL_LABEL_INFO, foreground="blue", cursor="hand2")
        info_button.pack(side="right", padx=SPACING_BETWEEN_ELEMENTS)
        self._add_tooltip(info_button, info)

        # Botão Assign
        btn_assign = ttk.Button(row_frame, text="Assign", takefocus=False)
        btn_assign.pack(side="right")
        btn_assign.config(command=lambda: self._click_assign_capture_position(key, spin_x, spin_y, btn_assign))
        
        # Botão Show
        btn_show = ttk.Button(row_frame, text="Show", takefocus=False)
        btn_show.pack(side="right", padx=SPACING_BETWEEN_BUTTONS)
        btn_show.config(command=lambda: self._click_assign_show_position_highlight(key))
        
        # Pega valores do config.ini
        coords = Config.get(self.section_name, key, "0,0")
        # l.trace(f"{self.section_name} {key}: {coords}")
        x, y = map(int, coords.split(","))
        spin_x.set(x)
        spin_y.set(y)
        
    def make_ui_entry(self, parent, label, key, info=None, padx=0, pady=0):
        """Cria um campo de input com uma label fixa à esquerda e um campo de entrada à direita (50% do espaço)."""

        # Configuração de paddings
        PADDING_X = padx
        PADDING_Y = pady
        SPACING_BETWEEN_ELEMENTS = 5  # Espaço entre info, label e input
        INPUT_WIDTH_PERCENTAGE = 0.5  # 50% do espaço horizontal

        # Seção principal
        section = ttk.Frame(parent)
        section.pack(fill="x", pady=PADDING_Y, padx=PADDING_X, anchor="w")

        # Linha única para Info (opcional), Label e Entry
        row_frame = ttk.Frame(section)
        row_frame.pack(fill="x")

        # Botão de Info (se fornecido)
        if info:
            info_button = ttk.Label(row_frame, text=self.SYMBOL_LABEL_INFO, foreground="blue", cursor="hand2")
            info_button.pack(side="right", padx=(0, SPACING_BETWEEN_ELEMENTS))
            self._add_tooltip(info_button, info)

        # Label fixa à esquerda
        ttk.Label(row_frame, text=label).pack(side="left", padx=(0, SPACING_BETWEEN_ELEMENTS))

        # Campo de entrada (input)
        entry_var = tk.StringVar()
        entry = ttk.Entry(row_frame, width=35, textvariable=entry_var)
        entry.pack(side="right", padx=(0, SPACING_BETWEEN_ELEMENTS))
        
        # Define largura baseada na porcentagem do espaço total
        row_frame.columnconfigure(1, weight=1)  # Permite expansão do input

        # Carrega o valor do config.ini (se existir)
        entry_var.set(Config.get(self.section_name, key, ""))
        
        self.entries_to_save[key] = entry_var  # add to the list of things that will be saved if you press the save button
        return entry_var # not really used

    def make_ui_toggleable_entry(self, parent, label, key, info=None, padx=0, pady=0):
        """Cria um campo de input com um checkbox à esquerda para ativar/desativar a entrada."""

        # Configuração de paddings
        PADDING_X = padx
        PADDING_Y = pady
        SPACING_BETWEEN_ELEMENTS = 5  # Espaço entre elementos
        INPUT_WIDTH_PERCENTAGE = 0.5  # 50% do espaço horizontal

        # Seção principal
        section = ttk.Frame(parent)
        section.pack(fill="x", pady=PADDING_Y, padx=PADDING_X, anchor="w")

        # Linha única para Checkbox, Info (opcional), Label e Entry
        row_frame = ttk.Frame(section)
        row_frame.pack(fill="x")

        # Variável da checkbox (ativa/desativa o input)
        toggle_var = tk.BooleanVar(value=int(Config.get(self.section_name, f"{key}_enabled", "1")))  # Pega do config, padrão ativado

        # Checkbox para ativar/desativar o campo
        toggle_button = ttk.Checkbutton(row_frame, variable=toggle_var, takefocus=False)
        toggle_button.pack(side="left", padx=(0, SPACING_BETWEEN_ELEMENTS))

        # Botão de Info (se fornecido)
        if info:
            info_button = ttk.Label(row_frame, text=self.SYMBOL_LABEL_INFO, foreground="blue", cursor="hand2")
            info_button.pack(side="right", padx=(0, SPACING_BETWEEN_ELEMENTS))
            self._add_tooltip(info_button, info)

        # Label fixa à esquerda
        ttk.Label(row_frame, text=label).pack(side="left", padx=(0, SPACING_BETWEEN_ELEMENTS))

        # Campo de entrada (input)
        entry_var = tk.StringVar()
        entry = ttk.Entry(row_frame, width=35, textvariable=entry_var)
        entry.pack(side="right", padx=(0, SPACING_BETWEEN_ELEMENTS))

        # Define largura baseada na porcentagem do espaço total
        row_frame.columnconfigure(1, weight=1)  # Permite expansão do input

        # Carrega o valor do config.ini (se existir)
        entry_var.set(Config.get(self.section_name, key, ""))

        # Define o estado inicial baseado na checkbox
        entry_state = "normal" if toggle_var.get() else "disabled"
        entry.config(state=entry_state)

        # Atualiza o estado do entry quando a checkbox for clicada
        def toggle_entry():
            entry.config(state="normal" if toggle_var.get() else "disabled")

        toggle_button.config(command=toggle_entry)

        # Adiciona ao dicionário de entradas a serem salvas
        self.entries_to_save[key] = entry_var
        self.entries_to_save[f"{key}_enabled"] = toggle_var  # Salva o estado do toggle também

        return entry_var
    
    def make_ui_checkbox(self, parent, label, key, info=None, padx=0, pady=0):
        """Cria um checkbox com uma label à direita e um botão de info opcional."""

        # Configuração de paddings
        PADDING_X = padx
        PADDING_Y = pady
        SPACING_BETWEEN_ELEMENTS = 5  # Espaço entre info, checkbox e label

        # Seção principal
        section = ttk.Frame(parent)
        section.pack(fill="x", pady=PADDING_Y, padx=PADDING_X, anchor="w")

        # Variável do checkbox
        checkbox_var = tk.BooleanVar(value=Config.get(self.section_name, key, "0") == "1")

        # Linha única para Checkbox, Info e Label
        row_frame = ttk.Frame(section)
        row_frame.pack(fill="x")

        # Checkbox
        checkbox = ttk.Checkbutton(row_frame, variable=checkbox_var, takefocus=False)
        checkbox.pack(side="left", padx=(0, SPACING_BETWEEN_ELEMENTS))

        # Botão de Info (se fornecido)
        if info:
            info_button = ttk.Label(row_frame, text=self.SYMBOL_LABEL_INFO, foreground="blue", cursor="hand2")
            info_button.pack(side="right", padx=(0, SPACING_BETWEEN_ELEMENTS))
            self._add_tooltip(info_button, info)

        # Label à direita do checkbox
        ttk.Label(row_frame, text=label).pack(side="left", padx=(0, SPACING_BETWEEN_ELEMENTS))

        # Salva no dicionário para extração posterior
        self.entries_to_save[key] = checkbox_var

        return checkbox_var  # Retorna a variável para acesso posterior

    def make_ui_box_assign(self, parent, label, key, info=None, padx=0, pady=0):
        """Cria um botão para selecionar uma área da tela e exibe X, Y, W, H em spinboxes, com opção de mostrar a área."""
        
        # Criar um LabelFrame para organizar tudo
        section = ttk.LabelFrame(parent, text=label)
        section.pack(fill="x", pady=pady, padx=padx, anchor="w")

        # Frame para manter tudo em uma linha
        row_frame = ttk.Frame(section)
        row_frame.pack(fill="x", padx=5, pady=5)

        # Recupera valores salvos ou usa 0 como padrão
        default_values = Config.get(self.section_name, key, "0,0,0,0").split(",")
        x_var = tk.IntVar(value=int(default_values[0]))
        y_var = tk.IntVar(value=int(default_values[1]))
        w_var = tk.IntVar(value=int(default_values[2]))
        h_var = tk.IntVar(value=int(default_values[3]))

        # Criar os Spinboxes com os labels inline (X: <spinbox>, Y: <spinbox> etc.)
        def create_spinbox(parent, text, var):
            ttk.Label(parent, text=f"{text}:", takefocus=False).pack(side="left", padx=2)
            spinbox = ttk.Spinbox(parent, from_=0, to=9999, textvariable=var, width=5, takefocus=False)
            spinbox.pack(side="left", padx=2)
            return spinbox

        create_spinbox(row_frame, "X", x_var)
        create_spinbox(row_frame, "Y", y_var)
        create_spinbox(row_frame, "W", w_var)
        create_spinbox(row_frame, "H", h_var)

        # Botão de Info (se fornecido)
        if info:
            info_button = ttk.Label(row_frame, text=self.SYMBOL_LABEL_INFO, foreground="blue", cursor="hand2", takefocus=False)
            info_button.pack(side="right", padx=5)
            self._add_tooltip(info_button, info)
        
        # Botão para capturar a área
        btn_assign = ttk.Button(row_frame, text="📷 Assign", command=lambda: assign_box(), takefocus=False)
        btn_assign.pack(side="right", padx=5)

        # Botão para mostrar a área
        btn_show = ttk.Button(row_frame, text="Show", command=lambda: show_box(), takefocus=False)
        btn_show.pack(side="right", padx=5)


        def assign_box():
            """Cria uma overlay fullscreen para capturar a seleção da bounding box."""
            
            # Salva a janela ativa antes de abrir a overlay (menu de opções)
            parent_window = parent.winfo_toplevel()
            
            overlay = tk.Toplevel()
            overlay.attributes("-fullscreen", True)
            overlay.attributes("-alpha", 0.3)  # Tela escurecida
            overlay.config(bg="black")
            overlay.overrideredirect(True)
            overlay.lift()  # Sempre no topo

            canvas = tk.Canvas(overlay, bg="black", highlightthickness=0, takefocus=False)
            canvas.pack(fill="both", expand=True)

            start_x = start_y = None
            rect_id = None

            def on_press(event):
                """Inicia a seleção."""
                nonlocal start_x, start_y, rect_id
                start_x, start_y = event.x, event.y
                rect_id = canvas.create_rectangle(start_x, start_y, start_x, start_y, outline="red", width=2)

            def on_drag(event):
                """Atualiza o tamanho da seleção."""
                canvas.coords(rect_id, start_x, start_y, event.x, event.y)

            def on_release(event):
                """Finaliza a seleção, salva e fecha."""
                end_x, end_y = event.x, event.y
                x, y = min(start_x, end_x), min(start_y, end_y)
                width, height = abs(end_x - start_x), abs(end_y - start_y)

                x_root = overlay.winfo_rootx() + x
                y_root = overlay.winfo_rooty() + y

                x_var.set(x_root)
                y_var.set(y_root)
                w_var.set(width)
                h_var.set(height)

                overlay.destroy()  # Fecha a seleção
                
                # **🔥 Mantém o menu de opções como modal após fechar a seleção 🔥**
                parent_window.grab_set()
                parent_window.focus_force()  

            # Bind dos eventos do mouse
            canvas.bind("<ButtonPress-1>", on_press)
            canvas.bind("<B1-Motion>", on_drag)
            canvas.bind("<ButtonRelease-1>", on_release)

            overlay.grab_set()  # Bloqueia interação com outras janelas enquanto a seleção está ativa

        def show_box():
            """Mostra a bounding box na tela."""
            overlay = tk.Toplevel()
            overlay.attributes("-topmost", True)
            overlay.attributes("-alpha", 0.3)
            overlay.overrideredirect(True)
            overlay.geometry(f"{w_var.get()}x{h_var.get()}+{x_var.get()}+{y_var.get()}")
            overlay.config(bg="red")

            overlay.after(1000, overlay.destroy)  # Some após 1s

        # Salva para extração futura
        self.entries_to_save[key] = (x_var, y_var, w_var, h_var)
        return x_var, y_var, w_var, h_var
