import tkinter as tk
from tkinter import ttk
from lib.widgets.Entry import UIEntry
from lib.widgets.ToggleableEntry import UIToggleableEntry
from lib.widgets.Checkbox import UICheckbox
from lib.widgets.Radio import UIRadio
from lib.widgets.ClickAssign import UIClickAssign
from lib.widgets.BoxAssign import UIBoxAssign
from lib.config import Config

# Criando a janela principal
root = tk.Tk()
root.title("Teste dos Widgets")
root.geometry("500x400")
root.focus_force()

# Criando um frame para organizar os elementos
frame = ttk.Frame(root, padding=10)
frame.pack(fill="both", expand=True)

# Seção usada no config
CONFIG_SECTION = "TestSection"

# Criando os widgets
entry = UIEntry(frame, label="Teste Label", section=CONFIG_SECTION, key="text_entry")
toggle_entry = UIToggleableEntry(frame, CONFIG_SECTION, "toggle_text", "Entrada com Toggle")
checkbox = UICheckbox(frame, CONFIG_SECTION, "check_option", "Habilitar Opção")
radio = UIRadio(frame, CONFIG_SECTION, "radio_choice", "Escolha uma opção",
                options=[("op1", "Opção 1"), ("op2", "Opção 2"), ("op3", "Opção 3"), ("op4", "Opção 4"), ("op5", "Opção 5"), ("op6", "Opção 6"), ("op7", "Opção 7"), ("op8", "Opção 8"), ("op9", "Opção 9")], info="radio info")
click_assign = UIClickAssign(frame, CONFIG_SECTION, "click_position", "Definir Posição",
                             info="Clique em 'Assign' e depois na tela para capturar a posição.")
box_assign = UIBoxAssign(frame, CONFIG_SECTION, "box_position", "Definir Posição da Caixa", "isso é um info")

# Rodando o loop principal
root.mainloop()
