import tkinter as tk
from tkinter import ttk

from ui import ClientesFrame, ConsultasFrame, EstoqueFrame, LaudosFrame


class App:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Gerenciamento de Loja")
        self.root.geometry("900x600")
        self.root.minsize(700, 450)
        self._build_notebook()

    def _build_notebook(self):
        nb = ttk.Notebook(self.root)
        self._frames = {
            "clientes":  ClientesFrame(nb),
            "consultas": ConsultasFrame(nb),
            "estoque":   EstoqueFrame(nb),
            "laudos":    LaudosFrame(nb),
        }
        nb.add(self._frames["clientes"],  text="  Clientes  ")
        nb.add(self._frames["consultas"], text="  Consultas  ")
        nb.add(self._frames["estoque"],   text="  Estoque  ")
        nb.add(self._frames["laudos"],    text="  Laudos  ")
        nb.pack(fill="both", expand=True)
        nb.bind("<<NotebookTabChanged>>", self._on_tab_change)

    def _on_tab_change(self, event):
        nb = event.widget
        frame = nb.nametowidget(nb.select())
        if hasattr(frame, "refresh"):
            frame.refresh()
