import tkinter as tk
from tkinter import ttk
from .BaseModal import BaseModal
import lib.ui.widgets as ui


class ModalScreenCallibration(BaseModal):
    def __init__(self, root):
        super().__init__(
            root,
            width=600,
            height="AUTO",
            title="Calibration Settings",
            resizeable=False,
            section_name="ScreenCalibration",
        )
        # Call "<CLASS>.open" to run the Modal in a button. It will build the widgets defined in "<CLASS>._widgets"
        self.SAVE_BUTTON = False

    def _widgets(self, parent):
        PADX = 0
        PADY = 1

        self.button_start = ui.ClickAssign(
            parent=parent,
            section=self.section_name,
            key="button_start",
            label="Start",
            info="Button that starts the game. The one you have to press once you join a new server.",
            autosave=False,
        )

        self.button_inventory = ui.ClickAssign(
            parent=parent,
            section=self.section_name,
            key="button_inventory",
            label="Inventory",
            info="Button that opens the inventory menu.",
            autosave=False,
        )

        self.button_inventory_items = ui.ClickAssign(
            parent=parent,
            section=self.section_name,
            key="button_inventory_items",
            label="Inventory: Items",
            info="Button in inventory that opens the items menu.",
            autosave=False,
        )

        self.button_inventory_gears = ui.ClickAssign(
            parent=parent,
            section=self.section_name,
            key="button_inventory_gears",
            label="Inventory: Gears",
            info="Button in inventory that opens the gears menu.",
            autosave=False,
        )

        self.button_inventory_searchbar = ui.ClickAssign(
            parent=parent,
            section=self.section_name,
            key="button_inventory_searchbar",
            label="Inventory: Search bar",
            info="Button in inventory that lets you search for items.",
            autosave=False,
        )

        self.button_inventory_firstitem = ui.ClickAssign(
            parent=parent,
            section=self.section_name,
            key="button_inventory_firstitem",
            label="Inventory: First item slot",
            info="The first item that appears in your item inventory.\nMake sure to be fully scrolled up before selecting this position.",
            autosave=False,
        )

        self.button_inventory_useamount = ui.ClickAssign(
            parent=parent,
            section=self.section_name,
            key="button_inventory_useamount",
            label="Inventory: Item use amount",
            info="Field in inventory which lets you write the item use amount.",
            autosave=False,
        )

        self.button_inventory_usebutton = ui.ClickAssign(
            parent=parent,
            section=self.section_name,
            key="button_inventory_usebutton",
            label="Inventory: Item use button",
            info="Button in inventory that lets you use an item.",
            autosave=False,
        )

        self.save_button = ttk.Button(
            parent,
            text="Save",
            command=self.save_and_close,
            takefocus=False,
        )

        self.button_start.pack()
        self.button_inventory.pack()
        self.button_inventory_items.pack()
        self.button_inventory_gears.pack()
        self.button_inventory_searchbar.pack()
        self.button_inventory_firstitem.pack()
        self.button_inventory_useamount.pack()
        self.button_inventory_usebutton.pack()
        self.save_button.pack(fill="x", padx=PADX, pady=(10 + PADY, PADY))

        # # === TEST BOXASSIGN
        # self.make_ui_box_assign(parent=self.frame, label="Current biome area", key="box_biome", info="This should be a box around the current biome interface element.\nMake sure to make this bigger than the current biome, because biome names varies in length.\n\nOnce you click assign, HOLD AND DRAG to form a box around the area of interest.")

    def save_and_close(self):
        self.button_start.save()
        self.button_inventory.save()
        self.button_inventory_items.save()
        self.button_inventory_gears.save()
        self.button_inventory_searchbar.save()
        self.button_inventory_firstitem.save()
        self.button_inventory_useamount.save()
        self.button_inventory_usebutton.save()
        self.close()
