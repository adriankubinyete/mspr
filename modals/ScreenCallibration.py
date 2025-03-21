import tkinter as tk
from tkinter import ttk
from .BaseModal import BaseModal

class ModalScreenCallibration(BaseModal):
    def __init__(self, root):
        super().__init__(root, width=600, height="AUTO", title="Calibration Settings", resizeable=False, section_name="ScreenCalibration")
        # Call "<CLASS>.open" to run the Modal in a button. It will build the widgets defined in "<CLASS>._widgets"
        
    def _widgets(self, parent):
        PADX=0
        PADY=1
        
        self.make_ui_click_assign(padx=PADX, pady=PADY, parent=self.frame, label="Start", info="Button that starts the game. The one you have to press once you join a new server.", key="button_start")
        self.make_ui_click_assign(padx=PADX, pady=PADY, parent=self.frame, label="Inventory", info="Button that opens the inventory menu.", key="button_inventory")
        self.make_ui_click_assign(padx=PADX, pady=PADY, parent=self.frame, label="Inventory: Items", info="Button in inventory that opens the items menu.", key="button_inventory_items")
        self.make_ui_click_assign(padx=PADX, pady=PADY, parent=self.frame, label="Inventory: Gears", info="Button in inventory that opens the gears menu.", key="button_inventory_gears")
        self.make_ui_click_assign(padx=PADX, pady=PADY, parent=self.frame, label="Inventory: Search bar", info="Button in inventory that lets you search for items.", key="button_inventory_searchbar")
        self.make_ui_click_assign(padx=PADX, pady=PADY, parent=self.frame, label="Inventory: First item slot", info="The first item that appears in your item inventory.\nMake sure to be fully scrolled up before selecting this position.", key="button_inventory_firstitem")
        self.make_ui_click_assign(padx=PADX, pady=PADY, parent=self.frame, label="Inventory: Item use amount", info="Field in inventory which lets you write the item use amount.", key="button_inventory_useamount")
        self.make_ui_click_assign(padx=PADX, pady=PADY, parent=self.frame, label="Inventory: Item use button", info="Button in inventory that lets you use an item.", key="button_inventory_usebutton")
        
        # # === TEST BOXASSIGN
        # self.make_ui_box_assign(parent=self.frame, label="Current biome area", key="box_biome", info="This should be a box around the current biome interface element.\nMake sure to make this bigger than the current biome, because biome names varies in length.\n\nOnce you click assign, HOLD AND DRAG to form a box around the area of interest.")
        
    