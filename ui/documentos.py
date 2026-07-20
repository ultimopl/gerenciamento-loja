import os
import subprocess
import sys
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

import data


class DocumentosDialog(tk.Toplevel):
    def __init__(self, parent, cliente_id: int):
        super().__init__(parent)
        self._cliente_id = cliente_id
        cliente = data.obter_cliente(cliente_id)
        nome = cliente["nome"] if cliente else str(cliente_id)
        self.title(f"Documentos — {nome}")
        self.resizable(True, True)
        self.geometry("480x360")

        self._build()
        self._load()

        self.transient(parent)
        self.grab_set()
        x = parent.winfo_rootx() + (parent.winfo_width() - 480) // 2
        y = parent.winfo_rooty() + (parent.winfo_height() - 360) // 2
        self.geometry(f"480x360+{x}+{y}")
        parent.wait_window(self)

    def _build(self):
        frame = ttk.Frame(self, padding=10)
        frame.pack(fill="both", expand=True)
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)

        list_frame = ttk.Frame(frame)
        list_frame.grid(row=0, column=0, sticky="nsew")
        list_frame.rowconfigure(0, weight=1)
        list_frame.columnconfigure(0, weight=1)

        self._listbox = tk.Listbox(list_frame, selectmode="single", activestyle="dotbox")
        vsb = ttk.Scrollbar(list_frame, orient="vertical", command=self._listbox.yview)
        self._listbox.configure(yscrollcommand=vsb.set)
        self._listbox.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        self._listbox.bind("<Double-Button-1>", lambda _e: self._on_abrir())

        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=1, column=0, sticky="ew", pady=(8, 0))
        ttk.Button(btn_frame, text="Adicionar", command=self._on_adicionar).pack(side="left", padx=2)
        ttk.Button(btn_frame, text="Remover",   command=self._on_remover).pack(side="left", padx=2)
        ttk.Button(btn_frame, text="Abrir",     command=self._on_abrir).pack(side="left", padx=2)

        self._docs: list[dict] = []

    def _load(self):
        self._docs = data.listar_documentos(self._cliente_id)
        self._listbox.delete(0, "end")
        for doc in self._docs:
            self._listbox.insert("end", doc["nome"])

    def _selected_doc(self) -> dict | None:
        sel = self._listbox.curselection()
        return self._docs[sel[0]] if sel else None

    def _on_adicionar(self):
        path = filedialog.askopenfilename(
            title="Selecionar documento",
            filetypes=[("PDF", "*.pdf"), ("Imagens", "*.jpg *.jpeg *.png"), ("Todos", "*.*")],
        )
        if not path:
            return
        try:
            data.adicionar_documento(self._cliente_id, path)
            self._load()
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def _on_remover(self):
        doc = self._selected_doc()
        if not doc:
            messagebox.showinfo("Atenção", "Selecione um documento.")
            return
        if messagebox.askyesno("Confirmar", f"Remover '{doc['nome']}'?"):
            data.remover_documento(doc["id"])
            self._load()

    def _on_abrir(self):
        doc = self._selected_doc()
        if not doc:
            messagebox.showinfo("Atenção", "Selecione um documento.")
            return
        path = doc["caminho"]
        if not Path(path).exists():
            messagebox.showerror("Erro", "Arquivo não encontrado.")
            return
        if sys.platform == "win32":
            os.startfile(path)
        elif sys.platform == "darwin":
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])
