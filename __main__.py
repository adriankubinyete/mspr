import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import configparser
# from modals.BiomeSettings import BiomeSettingsManager
from modals.Debug import ModalDebug
from modals.ScreenCallibration import ModalScreenCallibration
from modals.Biome import ModalBiomeManager
from modals.RAMWS import ModalRAMWSSettings
from utils.tkutils import style_break_tab_focus
from lib.discord import Discord
from lib.system import System
from lib.roblox import RobloxApplication
from lib.config import Config
from lib.ramws import RAMWS
import logging
from lib.logutils import file_handler, console_handler
import copy # to validate cache of config
import asyncio
import threading

class App:
    def __init__(self):
        self.is_running = False
        self.loop = None                      # steaming async mess
        self.loop_started = threading.Event() # steaming async mess

        self.biomes = [
            "GLITCHED", "DREAM SPACE", "GRAVEYARD", "PUMPKIN MOON", "NULL", "SAND STORM",
            "CORRUPTION", "STARFALL", "HELL", "RAINY", "SNOWY", "WINDY"
        ]

        # make main window
        self.root = tk.Tk()
        self.root.title("MSPR: Masutty's Private Server Resetter")
        self.root.geometry("400x250")
        self.root.minsize(480, 280)
        self.root.report_callback_exception = self.handle_exception
        style_break_tab_focus(self.root) # remove the damn notebook.tab focus borders

        self.create_widgets()
        self.root.mainloop()

    def __getLogger(self, name):
        return logging.getLogger(f"mspr.App.{name}")

    def _start_event_loop(self):
        """Starts an event loop for running async tasks."""
        l = self.__getLogger('start_event_loop')
        l.info("Starting event loop.")
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop_started.set()
        self.loop.run_forever()
        l.info("Event loop started.")
        
    def _start_asyncio_thread(self):
        """Starts a new thread for running async tasks."""
        l = self.__getLogger('start_asyncio_thread')
        l.info("Starting asyncio thread.")
        self.thread = threading.Thread(target=self._start_event_loop, daemon=True)
        self.thread.start()
        self.loop_started.wait()
        l.info("Asyncio thread started.")

    def create_widgets(self):
        """Makes every interface element."""
        
        self.notebook = ttk.Notebook(self.root, takefocus="NO")
        self.notebook.pack(fill="both", expand=True)
        
        # self.notebook pages
        self.page_main = ttk.Frame(self.notebook)
        self.page_single_account = ttk.Frame(self.notebook)
        self.page_ram_multiple_accounts = ttk.Frame(self.notebook)
        
        self.notebook.add(self.page_main, text="Main")
        self.notebook.add(self.page_single_account, text="Single account")
        self.notebook.add(self.page_ram_multiple_accounts, text="Multi account")
        self.notebook.bind("<Left>", lambda event: "break")
        self.notebook.bind("<Right>", lambda event: "break")
        
        self.create_main_page(self.page_main)
        self.create_single_account_page(self.page_single_account)
        self.create_ram_multiple_accounts_page(self.page_ram_multiple_accounts)
    
    def create_main_page(self, page):
        """Creates the main page."""
        l = self.__getLogger('create_main_page')
        l.info("Creating main page.")
        
        frame = ttk.Frame(page, padding=10)
        frame.pack(fill="both", expand=True)

        # Entrada do Webhook
        row_webhook = ttk.Frame(frame)
        row_webhook.pack(fill="x", pady=2)
        ttk.Label(row_webhook, text="Discord Webhook : ").pack(side="left")
        self.entry_webhook = ttk.Entry(row_webhook)
        webhook_value = Config.get("General", "url_webhook", fallback="")
        self.entry_webhook.insert(0, webhook_value)
        self.entry_webhook.pack(side="right", fill="x", expand=True)

        # Entrada do Private Server
        row_pvt = ttk.Frame(frame)
        row_pvt.pack(fill="x", pady=2)
        ttk.Label(row_pvt, text="Private Server Link : ").pack(side="left")
        self.entry_pvt = ttk.Entry(row_pvt)
        pvt_value = Config.get("General", "url_private_server", fallback="")
        self.entry_pvt.insert(0, pvt_value)
        self.entry_pvt.pack(side="right", fill="x", expand=True)

        # Botões de Configuração
        row_config = ttk.Frame(frame)
        row_config.pack(fill="x", pady=10)

        self.biome_manager = ModalBiomeManager(self.root, self.biomes)
        self.btn_biome_settings = ttk.Button(row_config, text="Biome settings", command=self.biome_manager.open, takefocus=False)
        self.btn_biome_settings.pack(side="top", fill="x")

        self.callibration_modal = ModalScreenCallibration(self.root)
        self.btn_screen_settings = ttk.Button(row_config, text="Screen settings", command=self.callibration_modal.open, takefocus=False)
        self.btn_screen_settings.pack(side="top", fill="x")
        
        self.debug_modal = ModalDebug(self.root)
        self.btn_debug_menu = ttk.Button(row_config, text="Debug menu", command=self.debug_modal.open, takefocus=False)
        self.btn_debug_menu.pack(side="top", fill="x")

        # # Botões Iniciar e Parar
        # row_start_stop = ttk.Frame(frame)
        # row_start_stop.pack(fill="x", side="bottom", pady=5)

        # self.btn_start = ttk.Button(row_start_stop, text="Start", style="Primary.TButton", command=self.start_app, takefocus=False)
        # self.btn_start.pack(side="left", fill="x", expand=True)

        # self.btn_stop = ttk.Button(row_start_stop, text="Stop", style="Danger.TButton", command=self.stop_app, state="disabled", takefocus=False)
        # self.btn_stop.pack(side="right", fill="x", expand=True)

        # Seção RAM Webserver
        self.ram_webserver_modal = ModalRAMWSSettings(self.root)

        ram_section = ttk.LabelFrame(frame, text="RWS", padding=5)
        ram_section.pack(fill="x", pady=5)

        self.btn_ramws_menu = ttk.Button(ram_section, text="RAM Webserver Settings", command=self.ram_webserver_modal.open, takefocus=False)
        self.btn_ramws_testconn = ttk.Button(ram_section, text="Test Connection", command=self.check_ramws_connection, takefocus=False)

        # Label de status com largura fixa para evitar mudanças no layout
        self.lbl_ramws_status = ttk.Label(ram_section, text="", foreground="gray", width=6, anchor="center")

        # Empacotando os widgets
        self.btn_ramws_menu.pack(side="left", fill="x", expand=True)
        self.btn_ramws_testconn.pack(side="left", padx=5, fill="x", expand=True)
        self.lbl_ramws_status.pack(side="left", padx=10)


    def create_single_account_page(self, page):
        """Creates the single account page."""
        l = self.__getLogger('create_single_account_page')
        l.info("Creating single account page.")
        
    def create_ram_multiple_accounts_page(self, page):
        """Creates the RAM multiple accounts page."""
        l = self.__getLogger('create_ram_multiple_accounts_page')
        l.info("Creating RAM multiple accounts page.")

    def check_ramws_connection(self):
        """Testa a conexão e atualiza a label de status."""
        connected = RAMWS.test_connection()
        
        if connected:
            self.lbl_ramws_status.config(text="OK", foreground="green")
        else:
            self.lbl_ramws_status.config(text="ERROR", foreground="red")


    def toggle_controls(self, state: bool):
        """Enables/disables menu buttons. Mainly to stop changes while app is running. True means enabled buttons, False means disabled buttons"""
        l = self.__getLogger('toggle_controls')
        l.trace(f"Toggling controls to {state}")
        new_state = "normal" if state else "disabled"

        self.entry_webhook.config(state=new_state)
        self.entry_pvt.config(state=new_state)
        self.btn_start.config(state=new_state)
        self.btn_stop.config(state="normal" if not state else "disabled")
        self.btn_biome_settings.config(state=new_state)
        self.btn_screen_settings.config(state=new_state)

    def handle_exception(self, exc, val, tb):
        """Captures Tkinter loop exceptions. Displays nicely."""
        l = self.__getLogger("ExceptionHandler")
        self.is_running = False
        
        l.critical("Unhandled exception in Tkinter", exc_info=(exc, val, tb))
        user_error_message = f"An unexpected error occurred. Please check the logs for more information. Your logs can be found at:\n{logging.LOG_FILE_PATH}\n\n --- error information ---\n{val}"
        messagebox.showerror("Error", user_error_message)
        
        self.root.quit()
        self.root.destroy()
        exit(1)

    def start_app(self):
        """This is what tkinter calls. We just async-ify it. Why async-ify? Because."""
        if not self.loop: self._start_asyncio_thread()
        future = asyncio.run_coroutine_threadsafe(self.async_start_app(), self.loop)
        
    async def async_start_app(self):
        """
        Main function of this application
        It should disable buttons and inputs so that the user can't change anything while the app is running.
        It should start monitoring the current biome, and do the appropriate actions when the biome changes.
        """
        l =  self.__getLogger('start_app')
        
        if not self.loop: self._start_asyncio_thread()
        
        l.debug("Starting app...")
        if self.is_running: l.warning("App is already running!"); return
        self.is_running = True
        self.toggle_controls(False)  # disable app controls
        
        # read values and save to config
        webhook = self.entry_webhook.get()
        pvt = self.entry_pvt.get()
        
        # ========= 
        # @TODO(Adrian): This should not be here. I want this to save automatically. If I edit webhook, and, without starting the app, I close it, it won't be saved.
        Config.set("General", "url_webhook", webhook)
        Config.set("General", "url_private_server", pvt)
        Config.save()
        # =========
        
        l.info("Application is now running!")
        Discord.setWebhook(webhook)
        Discord.send(embed=Discord.create_embed(footer="Application started", color="008a00", timestamp=True))
        # Discord.send(embed=Discord.create_embed(description=f"Active processes:\n{RobloxApplication.find_active_processes()}\nIs running? : {RobloxApplication.is_running()}", footer="Test", color="0000fa", timestamp=True))
        
        await RobloxApplication.join(
            forced=True, 
            url=Config.get("General", "url_private_server")
        )
        
    def stop_app(self):
        """This is what tkinter calls. We just async-ify it. Why async-ify? Because."""
        if not self.loop: self._start_asyncio_thread()
        future = asyncio.run_coroutine_threadsafe(self.async_stop_app(), self.loop)
        
    async def async_stop_app(self):
        """Stops the application and enables controls."""
        l = self.__getLogger('stop_app')
        if not self.is_running: l.warning("App is stopped!"); return
        self.is_running = False
        self.toggle_controls(True)  # Reativa os botões e inputs
        l.info("Application stopped!")
        Discord.send(embed=Discord.create_embed(footer="Application stopped", color="8a0000", timestamp=True))
        asyncio.run(await RobloxApplication._kill_lazy_processes())

# Executa o app
if __name__ == "__main__":
    logger = logging.getLogger("mspr")
    logger.setLevel(logging.TEST)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    App()
