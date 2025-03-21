import tkinter as tk
from tkinter import ttk
from .BaseModal import BaseModal
from lib.config import Config

class ModalBiomeManager(BaseModal):
    def __init__(self, root, biomes):
        super().__init__(root, width=300, height="AUTO", title="Choose a biome", resizeable=False, section_name="BiomeSettings")
        # Call "<CLASS>.open" to run the Modal in a button. It will build the widgets defined in "<CLASS>._widgets"
        self.SAVE_BUTTON=False
        self.biomes = biomes
        
    def _widgets(self, parent):
        for biome in self.biomes:
            modalbiome = ModalBiomeConfig(self.modal, biome)
            button = ttk.Button(parent, text=biome, command=modalbiome.open, takefocus=False)
            button.pack(fill="x", pady=2)
        
class ModalBiomeConfig(BaseModal):
    def __init__(self, root, biome):
        super().__init__(root, width=400, height="AUTO", title=f"Configuration for [{biome}]", resizeable=False, section_name=biome)
        l =  self._getLogger('__init__')
        self.biome = biome
        # Call "<CLASS>.open" to run the Modal in a button. It will build the widgets defined in "<CLASS>._widgets"
        
        RARE_BIOMES = ["GLITCHED", "DREAM SPACE"]
        if biome not in Config.get_sections() or len(Config.get(biome)) == 0:
            l.info(f"Biome [{biome}] not found in config, pre-generating...")
            # Config.set(biome, {
            #     "send_message": "1",
            #     "send_ping": "1" if biome in RARE_BIOMES else "0",
            #     "wait_until_finished": "1" if biome in RARE_BIOMES else "0",
            #     "custom_ping": "",
            #     "custom_ping_enabled": "0",
            #     "custom_webhook_url": "",
            #     "custom_webhook_url_enabled": "0",
            # })
             
            Config.set(biome, "send_message", "1")
            Config.set(biome, "send_ping", "1" if biome in RARE_BIOMES else "0")
            Config.set(biome, "wait_until_finished", "1" if biome in RARE_BIOMES else "0")
            Config.set(biome, "custom_ping", "")
            Config.set(biome, "custom_ping_enabled", "0")
            Config.set(biome, "custom_webhook_url", "")
            Config.set(biome, "custom_webhook_url_enabled", "0")
            Config.save()
        
    def _widgets(self, parent):
        PADX=0
        PADY=1
        self.make_ui_checkbox(padx=PADX, pady=PADY, parent=parent, label="Send Message", info="Send a notification message to webhook.", key="send_message")
        self.make_ui_checkbox(padx=PADX, pady=PADY, parent=parent, label="Send Ping", info="Send both message and ping to webhook.", key="send_ping")
        self.make_ui_checkbox(padx=PADX, pady=PADY, parent=parent, label="Wait Biome", info=f"Do not rejoin until [{self.biome}] biome ends.", key="wait_until_finished")
        self.make_ui_toggleable_entry(padx=PADX, pady=PADY, parent=parent, label="Custom Pings", info="If Send Ping is enabled, ID will we ping?\nUse \"@<id>\" to ping a user, and \"&<id>\" to ping a role.\nYou can specificy multiple users/roles by separating them with a comma, no spaces.\nExample: @123456789012345678,&123456789012345678", key="custom_ping")
        self.make_ui_toggleable_entry(padx=PADX, pady=PADY, parent=parent, label="Custom Webhook URL", info=f"If you want to specify a custom webhook for [{self.biome}] biome, enter it here.\nYou can specify multiple webhooks by separating them with a comma, no spaces.", key="custom_webhook_url")
    