import tkinter as tk
from tkinter import messagebox, ttk

import data
from ui.base import BaseDialog, BaseFrame, FieldGroup, SearchBar, TableView
from ui.documentos import DocumentosDialog

_COLUMNS = [
    {"id": "nome",       "label": "Nome",        "width": 200},
    {"id": "cpf",        "label": "CPF",         "width": 130},
    {"id": "nascimento", "label": "Nascimento",  "width": 100},
    {"id": "telefone",   "label": "Telefone",    "width": 120},
]


class ClientesFrame(BaseFrame):
    def _build(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        top = ttk.Frame(self)
        top.grid(row=0, column=0, sticky="ew", padx=8, pady=6)
        ttk.Label(top, text="Clientes", font=("", 12, "bold")).pack(side="left")
        self._search = SearchBar(top, on_search=self._load_data)
        self._search.pack(side="right")

        self._table = TableView(self, columns=_COLUMNS)
        self._table.grid(row=1, column=0, sticky="nsew", padx=8)

        btn = ttk.Frame(self)
        btn.grid(row=2, column=0, sticky="ew", padx=8, pady=6)
        ttk.Button(btn, text="Novo",       command=self._on_novo).pack(side="left", padx=2)
        ttk.Button(btn, text="Editar",     command=self._on_editar).pack(side="left", padx=2)
        ttk.Button(btn, text="Excluir",    command=self._on_excluir).pack(side="left", padx=2)
        ttk.Button(btn, text="Documentos", command=self._on_documentos).pack(side="left", padx=2)

    def _load_data(self, busca: str = ""):
        rows = data.listar_clientes(busca)
        self._table.load(rows)

    def _on_novo(self):
        ClienteDialog(self)
        self._load_data()

    def _on_editar(self):
        id_ = self._table.selected_id()
        if not id_:
            messagebox.showinfo("Atenção", "Selecione um cliente.")
            return
        cliente = data.obter_cliente(id_)
        ClienteDialog(self, data=cliente)
        self._load_data()

    def _on_excluir(self):
        id_ = self._table.selected_id()
        if not id_:
            messagebox.showinfo("Atenção", "Selecione um cliente.")
            return
        if messagebox.askyesno("Confirmar", "Excluir este cliente e todos os seus documentos?"):
            data.excluir_cliente(id_)
            self._load_data()

    def _on_documentos(self):
        id_ = self._table.selected_id()
        if not id_:
            messagebox.showinfo("Atenção", "Selecione um cliente.")
            return
        DocumentosDialog(self, cliente_id=id_)


class ClienteDialog(BaseDialog):
    def __init__(self, parent, data: dict | None = None):
        self._nome = tk.StringVar(value=(data or {}).get("nome", ""))
        self._cpf  = tk.StringVar(value=(data or {}).get("cpf", ""))
        self._nasc = tk.StringVar(value=(data or {}).get("nascimento", ""))
        self._tel  = tk.StringVar(value=(data or {}).get("telefone", ""))
        title = "Editar Cliente" if data and data.get("id") else "Novo Cliente"
        super().__init__(parent, title=title, data=data)

    def _build_fields(self, frame: ttk.Frame):
        self._group = FieldGroup(frame, text="Dados do cliente")
        self._group.pack(fill="both", expand=True)
        self._group.add_entry("Nome *",          self._nome, row=0, width=35)
        self._group.add_entry("CPF",             self._cpf,  row=1, width=35)
        self._group.add_entry("Data nascimento", self._nasc, row=2, width=35)
        self._group.add_entry("Telefone",        self._tel,  row=3, width=35)

        self._err = ttk.Label(frame, text="", foreground="red")
        self._err.pack(pady=(4, 0))

    def _on_save(self):
        nome = self._nome.get().strip()
        if len(nome) < 2:
            self._err.config(text="Nome deve ter ao menos 2 caracteres.")
            return
        dados = {
            "nome":       nome,
            "cpf":        self._cpf.get().strip() or None,
            "nascimento": self._nasc.get().strip() or None,
            "telefone":   self._tel.get().strip() or None,
        }
        if self._data.get("id"):
            dados["id"] = self._data["id"]
        try:
            import data as db
            db.salvar_cliente(dados)
        except Exception as e:
            self._err.config(text=str(e))
            return
        self.result = dados
        self.destroy()
