import tkinter as tk
from tkinter import ttk

def style_break_tab_focus(root):
    style = ttk.Style(root)
    style.layout("TNotebook.Tab", [
        ('Notebook.tab', {
            'sticky': 'nswe',
            'children': [
                ('Notebook.padding', {
                    'side': 'top',
                    'sticky': 'nswe',
                    'children': [
                        # Removendo o foco
                        ('Notebook.label', {'side': 'top', 'sticky': ''})
                    ]
                })
            ]
        })
    ])