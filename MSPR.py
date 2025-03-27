import logging
import tkinter as tk
from tkinter import ttk
from collections import defaultdict

# interface
import lib.ui.widgets as ui
from lib.ui.utils import *
# from lib.ui.modals.ScreenCallibration import ModalScreenCallibration
# from lib.ui.modals.Biome import ModalBiomeManager


class Application:
    def __init__(
        self, title="App", width=400, height=250, exceptionHandler=lambda *args: None
    ):
        # --- APP VARIABLES
        self.APP_IS_RUNNING = False
        self.APPLICATION_NAME = title
        self.APPLICATION_WIDTH = width
        self.APPLICATION_HEIGHT = height
        self.BIOMES = [
            "GLITCHED",
            "DREAM SPACE",
            "GRAVEYARD",
            "PUMPKIN MOON",
            "NULL",
            "SAND STORM",
            "CORRUPTION",
            "STARFALL",
            "HELL",
            "RAINY",
            "SNOWY",
            "WINDY",
        ]

        # --- TK STUFF
        self.root = tk.Tk()
        style_break_tab_focus(self.root)  # remove annoying focus from notebooks
        self.root.title(self.APPLICATION_NAME)
        self.root.geometry(f"{self.APPLICATION_WIDTH}x{self.APPLICATION_HEIGHT}")
        self.root.minsize(480, 280)
        self.root.report_callback_exception = exceptionHandler

        # --- WIDGETS
        self._create_notebook()
        self._create_notebook_pages()

    def __getLogger(self, name):
        return logging.getLogger(f"mspr.App.{name}")

    def _create_notebook(self):
        """
        Initializes the main notebook
        """
        l = self.__getLogger("setup:create_notebok")
        l.info("Called")

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True)

        # disable tab change
        self.notebook.bind("<Left>", "break")
        self.notebook.bind("<Right>", "break")

    def _create_notebook_pages(self):
        """
        Dinamically adds pages to the notebook
        """
        l = self.__getLogger("setup:create_notebook_pages")
        l.info("Called")

        pages = {
            # page_name: callback_function --> will be called with frame as argument
            "Main": self.page_main,
            "Single Accounts": self.page_single_account,
            "Multi Accounts": self.page_multi_account,
        }
        self.page_frames = defaultdict()

        for name, callback in pages.items():
            frame = ttk.Frame(self.notebook)
            self.notebook.add(frame, text=f"  {name}  ")  # XD
            self.page_frames[name] = frame
            callback(frame)

    def page_main(self, page):
        l = self.__getLogger("page:main")
        l.info("Called")

        frame = ttk.Frame(page, padding=10)
        frame.pack(fill="both", expand=True)

        l.trace("ModalBiomeManager...")
        self.biome_manager = ui.ModalBiomeManager(self.root, self.BIOMES)
        self.btn_biome_settings = ttk.Button(
            frame,
            text="Biome settings",
            command=self.biome_manager.open,
            takefocus=False,
        )

        l.trace("ModalScreenCallibration...")
        self.callibration_modal = ui.ModalScreenCallibration(self.root)
        self.btn_screen_settings = ttk.Button(
            frame,
            text="Screen settings",
            command=self.callibration_modal.open,
            takefocus=False,
        )
        
        # ----------------
        self.btn_biome_settings.pack(side="top", fill="x")
        self.btn_screen_settings.pack(side="top", fill="x")
        # ram settings
        

    def page_single_account(self, page):
        l = self.__getLogger("page:single_account")
        l.info("Called")
        # private server
        # discord webhook
        # start/stop

    def page_multi_account(self, page):
        l = self.__getLogger("page:multi_account")
        l.info("Called")
        # check if ram ws is running.
        # if not, make a simple page saying "enable your ram ws and click here to connect"

        # add/remove accounts from ram
