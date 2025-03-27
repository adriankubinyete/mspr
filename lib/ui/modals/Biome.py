import tkinter as tk
from tkinter import ttk
from .BaseModal import BaseModal
from lib.config import Config
import lib.ui.widgets as ui


class ModalBiomeManager(BaseModal):
    def __init__(self, root, biomes):
        super().__init__(
            root,
            width=300,
            height="AUTO",
            title="Choose a biome",
            resizeable=False,
            section_name="BiomeSettings",
        )
        # Call "<CLASS>.open" to run the Modal in a button. It will build the widgets defined in "<CLASS>._widgets"
        self.SAVE_BUTTON = False
        self.biomes = biomes

    def _widgets(self, parent):
        for biome in self.biomes:
            modalbiome = ModalBiomeConfig(self.modal, biome)
            button = ttk.Button(
                parent, text=biome, command=modalbiome.open, takefocus=False
            )
            button.pack(fill="x", pady=2)


class ModalBiomeConfig(BaseModal):
    def __init__(self, root, biome):
        super().__init__(
            root,
            width=400,
            height="AUTO",
            title=f"Configuration for [{biome}]",
            resizeable=False,
            section_name=biome,
        )
        l = self._getLogger("__init__")
        self.SAVE_BUTTON = False
        self.biome = biome
        # Call "<CLASS>.open" to run the Modal in a button. It will build the widgets defined in "<CLASS>._widgets"

        RARE_BIOMES = ["GLITCHED", "DREAM SPACE"]
        if biome not in Config.get_sections() or len(Config.get(biome)) == 0:
            l.info(f"Biome [{biome}] not found in config, pre-generating...")
            Config.set(biome, "send_message", "1")
            Config.set(biome, "send_ping", "1" if biome in RARE_BIOMES else "0")
            Config.set(
                biome, "wait_until_finished", "1" if biome in RARE_BIOMES else "0"
            )
            Config.set(biome, "custom_ping", "")
            Config.set(biome, "custom_ping_enabled", "0")
            Config.set(biome, "custom_webhook_url", "")
            Config.set(biome, "custom_webhook_url_enabled", "0")
            Config.save()

    def _widgets(self, parent):
        PADX = 0
        PADY = 1

        self.send_message = ui.Checkbox(
            parent=parent,
            section=self.section_name,
            key="send_message",
            label="Send Message",
            info="Send a notification message to webhook.",
            autosave=False,
        )
        self.send_ping = ui.Checkbox(
            parent=parent,
            section=self.section_name,
            key="send_ping",
            label="Send Ping",
            info="Send both message and ping to webhook.",
            autosave=False,
        )

        self.wait_biome = ui.Checkbox(
            parent=parent,
            section=self.section_name,
            key="wait_until_finished",
            label="Wait Biome",
            info="Do not rejoin until [{self.biome}] biome ends.",
            autosave=False,
        )

        self.custom_pings = ui.ToggleableEntry(
            parent=parent,
            section=self.section_name,
            key="custom_ping",
            label="Custom Ping",
            info='If Send Ping is enabled, ID will we ping?\nUse "@<id>" to ping a user, and "&<id>" to ping a role.\nYou can specificy multiple users/roles by separating them with a comma, no spaces.\nExample: @123456789012345678,&123456789012345678',
            autosave=False,
        )

        self.custom_webhook = ui.ToggleableEntry(
            parent=parent,
            section=self.section_name,
            key="custom_webhook_url",
            label="Custom Webhook",
            info="If you want to specify a custom webhook for [{self.biome}] biome, enter it here.\nYou can specify multiple webhooks by separating them with a comma, no spaces",
            autosave=False,
        )

        self.save_button = ttk.Button(
            parent,
            text="Save",
            command=self.save_and_close,
            takefocus=False,
        )

        self.send_message.pack(fill="x", padx=PADX, pady=PADY)
        self.send_ping.pack(fill="x", padx=PADX, pady=PADY)
        self.wait_biome.pack(fill="x", padx=PADX, pady=PADY)
        self.custom_pings.pack(fill="x", padx=PADX, pady=PADY)
        self.custom_webhook.pack(fill="x", padx=PADX, pady=PADY)
        self.save_button.pack(fill="x", padx=PADX, pady=(10 + PADY, PADY))

    def save_and_close(self):
        self.send_message.save()
        self.send_ping.save()
        self.wait_biome.save()
        self.custom_pings.save()
        self.custom_webhook.save()
        self.close()
