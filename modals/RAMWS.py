import requests
import tkinter as tk
from tkinter import ttk
from lib.config import Config
from .BaseModal import BaseModal

class ModalRAMWSSettings(BaseModal):
    def __init__(self, root):
        super().__init__(root, width=500, height="AUTO", title="RAM Webserver Settings", resizeable=False, section_name="RAMWS")
        # Call "<CLASS>.open" to run the Modal in a button. It will build the widgets defined in "<CLASS>._widgets"
        
    def _widgets(self, parent):
        PADX=0
        PADY=1
        
        self.make_ui_entry(padx=PADX, pady=PADY, parent=parent, label="Webserver URL", info="URL on which the Roblox Account Manager webserver is running.", key="ramws_url")
        self.make_ui_entry(padx=PADX, pady=PADY, parent=parent, label="Webserver Port", info="Port on which the Roblox Account Manager webserver is running.", key="ramws_port")
        self.make_ui_toggleable_entry(padx=PADX, pady=PADY, parent=parent, label="Webserver Password", info="Password on which your Roblox Account Manager webserver is authenticated with.\nThis is only needed if you check the \"Every Request Requires Password\" box.", key="ramws_password")
                