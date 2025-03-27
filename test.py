import tkinter as tk
from tkinter import ttk
from lib.config import Config
from lib.ui.AccountRow import AccountManager


def main():
    # Cria a janela principal
    root = tk.Tk()
    root.title("Gerenciador de Contas")
    root.geometry("800x600")

    # Instancia o AccountManager
    account_manager = AccountManager(root)

    # Inicia a interface
    root.mainloop()


if __name__ == "__main__":
    main()
