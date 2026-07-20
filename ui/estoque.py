import tkinter as tk
from tkinter import messagebox, ttk

import data
from ui.base import BaseDialog, BaseFrame, FieldGroup, SearchBar, TableView

_COLUMNS = [
    {"id": "nome",       "label": "Produto",    "width": 220},
    {"id": "quantidade", "label": "Qtd",        "width": 70, "anchor": "e"},
    {"id": "unidade",    "label": "Unidade",    "width": 80},
    {"id": "preco",      "label": "Preço (R$)", "width": 100, "anchor": "e"},
]

_UNIDADES = ["un", "kg", "g", "cx", "L", "mL", "m", "pç"]


class EstoqueFrame(BaseFrame):
    def _build(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        top = ttk.Frame(self)
        top.grid(row=0, column=0, sticky="ew", padx=8, pady=6)
        ttk.Label(top, text="Estoque", font=("", 12, "bold")).pack(side="left")
        self._search = SearchBar(top, on_search=self._load_data)
        self._search.pack(side="right")

        self._table = TableView(self, columns=_COLUMNS)
        self._table.grid(row=1, column=0, sticky="nsew", padx=8)

        btn = ttk.Frame(self)
        btn.grid(row=2, column=0, sticky="ew", padx=8, pady=6)
        ttk.Button(btn, text="Novo",        command=self._on_novo).pack(side="left", padx=2)
        ttk.Button(btn, text="Editar",      command=self._on_editar).pack(side="left", padx=2)
        ttk.Button(btn, text="Excluir",     command=self._on_excluir).pack(side="left", padx=2)
        ttk.Button(btn, text="Ajustar Qtd", command=self._on_ajustar).pack(side="left", padx=2)

    def _load_data(self, busca: str = ""):
        rows = data.listar_produtos(busca)
        for r in rows:
            r["preco"] = f"{r['preco']:.2f}"
        self._table.load(rows)

    def _on_novo(self):
        ProdutoDialog(self)
        self._load_data()

    def _on_editar(self):
        id_ = self._table.selected_id()
        if not id_:
            messagebox.showinfo("Atenção", "Selecione um produto.")
            return
        produtos = data.listar_produtos()
        produto = next((p for p in produtos if p["id"] == id_), None)
        ProdutoDialog(self, data=produto)
        self._load_data()

    def _on_excluir(self):
        id_ = self._table.selected_id()
        if not id_:
            messagebox.showinfo("Atenção", "Selecione um produto.")
            return
        if messagebox.askyesno("Confirmar", "Excluir este produto?"):
            data.excluir_produto(id_)
            self._load_data()

    def _on_ajustar(self):
        id_ = self._table.selected_id()
        if not id_:
            messagebox.showinfo("Atenção", "Selecione um produto.")
            return
        AjusteEstoqueDialog(self, produto_id=id_)
        self._load_data()


class ProdutoDialog(BaseDialog):
    def __init__(self, parent, data: dict | None = None):
        self._nome  = tk.StringVar(value=(data or {}).get("nome", ""))
        self._qtd   = tk.IntVar(value=(data or {}).get("quantidade", 0))
        self._unid  = tk.StringVar(value=(data or {}).get("unidade", "un"))
        self._preco = tk.StringVar(value=str((data or {}).get("preco", "0.00")))
        title = "Editar Produto" if data and data.get("id") else "Novo Produto"
        super().__init__(parent, title=title, data=data)

    def _build_fields(self, frame: ttk.Frame):
        self._group = FieldGroup(frame, text="Dados do produto")
        self._group.pack(fill="both", expand=True)
        self._group.add_entry("Nome *",      self._nome,  row=0, width=30)
        self._group.add_spinbox("Quantidade", self._qtd,   row=1, from_=0, to=999999, width=12)
        self._group.add_combobox("Unidade",   self._unid,  _UNIDADES, row=2)
        self._group.add_entry("Preço (R$)",  self._preco, row=3, width=15)

        self._err = ttk.Label(frame, text="", foreground="red")
        self._err.pack(pady=(4, 0))

    def _on_save(self):
        nome = self._nome.get().strip()
        if not nome:
            self._err.config(text="Nome é obrigatório.")
            return
        try:
            preco = float(self._preco.get().replace(",", "."))
        except ValueError:
            self._err.config(text="Preço inválido.")
            return
        dados = {
            "nome":       nome,
            "quantidade": self._qtd.get(),
            "unidade":    self._unid.get(),
            "preco":      preco,
        }
        if self._data.get("id"):
            dados["id"] = self._data["id"]
        import data as db
        db.salvar_produto(dados)
        self.result = dados
        self.destroy()


class AjusteEstoqueDialog(BaseDialog):
    def __init__(self, parent, produto_id: int):
        self._produto_id = produto_id
        self._tipo  = tk.StringVar(value="entrada")
        self._delta = tk.IntVar(value=1)
        self._obs   = tk.StringVar()
        super().__init__(parent, title="Ajustar Estoque", data={"id": produto_id})

    def _build_fields(self, frame: ttk.Frame):
        self._group = FieldGroup(frame, text="Ajuste")
        self._group.pack(fill="both", expand=True)

        ttk.Label(self._group, text="Tipo").grid(row=0, column=0, sticky="w", padx=(0, 8), pady=3)
        radio_frame = ttk.Frame(self._group)
        radio_frame.grid(row=0, column=1, sticky="w", pady=3)
        ttk.Radiobutton(radio_frame, text="Entrada", variable=self._tipo, value="entrada").pack(side="left")
        ttk.Radiobutton(radio_frame, text="Saída",   variable=self._tipo, value="saida").pack(side="left", padx=8)

        self._group.add_spinbox("Quantidade", self._delta, row=1, from_=1, to=999999, width=12)
        self._group.add_entry("Observação", self._obs, row=2, width=30)

        self._err = ttk.Label(frame, text="", foreground="red")
        self._err.pack(pady=(4, 0))

    def _on_save(self):
        delta = self._delta.get()
        if self._tipo.get() == "saida":
            delta = -delta
        import data as db
        db.ajustar_estoque(self._produto_id, delta)
        self.result = {"delta": delta}
        self.destroy()
