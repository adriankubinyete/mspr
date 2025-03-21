import tkinter as tk
from tkinter import ttk
from .BaseModal import BaseModal

class ModalDebug(BaseModal):
    def __init__(self, root):
        super().__init__(root, width=600, height="AUTO", title="Debug Page", resizeable=False, section_name="Debug")
        # Call "<CLASS>.open" to run the Modal in a button. It will build the widgets defined in "<CLASS>._widgets"
        self.SAVE_BUTTON=False
        
    def _widgets(self, parent):
        label = ttk.Label(parent, text="Debug Page")
        label.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
    