import tkinter as tk
from tkinter import messagebox, ttk

import data
from ui.base import BaseDialog, BaseFrame, FieldGroup, SearchBar, TableView

_COLUMNS = [
    {"id": "data_hora",     "label": "Data/Hora",    "width": 140},
    {"id": "cliente_nome",  "label": "Cliente",      "width": 180},
    {"id": "profissional",  "label": "Profissional", "width": 150},
    {"id": "motivo",        "label": "Motivo",       "width": 180},
    {"id": "compareceu",    "label": "Compareceu",   "width": 90},
    {"id": "status",        "label": "Status",       "width": 90},
]

_STATUS_OPS      = ["Agendada", "Realizada", "Cancelada", "Remarcada"]
_COMPARECEU_OPS  = {"—": None, "Sim": 1, "Não": 0}
_COMPARECEU_LABEL = {None: "—", 1: "Sim", 0: "Não"}


def _fmt_row(r: dict) -> dict:
    r = dict(r)
    r["compareceu"] = _COMPARECEU_LABEL.get(r.get("compareceu"))
    return r


class ConsultasFrame(BaseFrame):
    def _build(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        top = ttk.Frame(self)
        top.grid(row=0, column=0, sticky="ew", padx=8, pady=6)
        ttk.Label(top, text="Consultas", font=("", 12, "bold")).pack(side="left")
        self._search = SearchBar(top, on_search=self._load_data)
        self._search.pack(side="right")

        self._table = TableView(self, columns=_COLUMNS)
        self._table.grid(row=1, column=0, sticky="nsew", padx=8)

        btn = ttk.Frame(self)
        btn.grid(row=2, column=0, sticky="ew", padx=8, pady=6)
        ttk.Button(btn, text="Nova",      command=self._on_nova).pack(side="left", padx=2)
        ttk.Button(btn, text="Editar",    command=self._on_editar).pack(side="left", padx=2)
        ttk.Button(btn, text="Remarcar",  command=self._on_remarcar).pack(side="left", padx=2)
        ttk.Button(btn, text="Excluir",   command=self._on_excluir).pack(side="left", padx=2)

    def _load_data(self, busca: str = ""):
        rows = [_fmt_row(r) for r in data.listar_consultas(busca)]
        self._table.load(rows)

    def _on_nova(self):
        ConsultaDialog(self)
        self._load_data()

    def _on_editar(self):
        id_ = self._table.selected_id()
        if not id_:
            messagebox.showinfo("Atenção", "Selecione uma consulta.")
            return
        ConsultaDialog(self, data=data.obter_consulta(id_))
        self._load_data()

    def _on_remarcar(self):
        id_ = self._table.selected_id()
        if not id_:
            messagebox.showinfo("Atenção", "Selecione uma consulta.")
            return
        original = data.obter_consulta(id_)
        if original["status"] in ("Cancelada", "Remarcada"):
            messagebox.showinfo("Atenção", "Consulta já está cancelada ou remarcada.")
            return
        RemarcarDialog(self, original=original)
        self._load_data()

    def _on_excluir(self):
        id_ = self._table.selected_id()
        if not id_:
            messagebox.showinfo("Atenção", "Selecione uma consulta.")
            return
        if messagebox.askyesno("Confirmar", "Excluir esta consulta?"):
            data.excluir_consulta(id_)
            self._load_data()


class ConsultaDialog(BaseDialog):
    def __init__(self, parent, data: dict | None = None):
        self._data_hora    = tk.StringVar(value=(data or {}).get("data_hora", ""))
        self._profissional = tk.StringVar(value=(data or {}).get("profissional", ""))
        self._motivo       = tk.StringVar(value=(data or {}).get("motivo", ""))
        self._status       = tk.StringVar(value=(data or {}).get("status", "Agendada"))
        comp_raw = (data or {}).get("compareceu")
        self._compareceu   = tk.StringVar(value=_COMPARECEU_LABEL.get(comp_raw, "—"))
        self._cliente_id: int | None = (data or {}).get("cliente_id")
        self._cliente_nome = tk.StringVar(value=(data or {}).get("cliente_nome", ""))
        title = "Editar Consulta" if data and data.get("id") else "Nova Consulta"
        super().__init__(parent, title=title, data=data)

    def _build_fields(self, frame: ttk.Frame):
        group = FieldGroup(frame, text="Dados da consulta")
        group.pack(fill="both", expand=True)

        group._label("Cliente *", row=0)
        cf = ttk.Frame(group)
        cf.grid(row=0, column=1, sticky="ew", pady=3)
        ttk.Entry(cf, textvariable=self._cliente_nome, state="readonly", width=28).pack(side="left")
        ttk.Button(cf, text="…", width=3, command=self._pick_cliente).pack(side="left", padx=(4, 0))

        group.add_entry("Profissional", self._profissional, row=1, width=35)
        group.add_entry("Data/Hora *",  self._data_hora,    row=2, width=35)
        ttk.Label(group, text="(AAAA-MM-DD HH:MM)", foreground="gray").grid(row=2, column=2, sticky="w", padx=4)
        group.add_entry("Motivo",       self._motivo,       row=3, width=35)
        group.add_combobox("Compareceu", self._compareceu, list(_COMPARECEU_OPS.keys()), row=4)
        group.add_combobox("Status",     self._status,     _STATUS_OPS,                  row=5)

        self._err = ttk.Label(frame, text="", foreground="red")
        self._err.pack(pady=(4, 0))

    def _pick_cliente(self):
        picker = _ClientePicker(self)
        if picker.result:
            self._cliente_id = picker.result["id"]
            self._cliente_nome.set(picker.result["nome"])

    def _on_save(self):
        if not self._cliente_id:
            self._err.config(text="Selecione um cliente.")
            return
        data_hora = self._data_hora.get().strip()
        if not data_hora:
            self._err.config(text="Data/Hora obrigatória.")
            return
        dados = {
            "cliente_id":   self._cliente_id,
            "profissional": self._profissional.get().strip() or None,
            "data_hora":    data_hora,
            "motivo":       self._motivo.get().strip() or None,
            "compareceu":   _COMPARECEU_OPS[self._compareceu.get()],
            "status":       self._status.get(),
        }
        if self._data.get("id"):
            dados["id"] = self._data["id"]
        try:
            import data as db
            db.salvar_consulta(dados)
        except Exception as e:
            self._err.config(text=str(e))
            return
        self.result = dados
        self.destroy()


class RemarcarDialog(BaseDialog):
    def __init__(self, parent, original: dict):
        self._original     = original
        self._data_hora    = tk.StringVar()
        self._profissional = tk.StringVar(value=original.get("profissional", ""))
        self._motivo       = tk.StringVar(value=original.get("motivo", ""))
        super().__init__(parent, title="Remarcar Consulta", data=original)

    def _build_fields(self, frame: ttk.Frame):
        ttk.Label(frame, text=f"Cliente: {self._original['cliente_nome']}", font=("", 10, "bold")).pack(anchor="w", pady=(0, 6))
        ttk.Label(frame, text=f"Original: {self._original['data_hora']}", foreground="gray").pack(anchor="w", pady=(0, 8))

        group = FieldGroup(frame, text="Nova data")
        group.pack(fill="both", expand=True)
        group.add_entry("Data/Hora *",  self._data_hora,    row=0, width=35)
        ttk.Label(group, text="(AAAA-MM-DD HH:MM)", foreground="gray").grid(row=0, column=2, sticky="w", padx=4)
        group.add_entry("Profissional", self._profissional, row=1, width=35)
        group.add_entry("Motivo",       self._motivo,       row=2, width=35)

        self._err = ttk.Label(frame, text="", foreground="red")
        self._err.pack(pady=(4, 0))

    def _on_save(self):
        data_hora = self._data_hora.get().strip()
        if not data_hora:
            self._err.config(text="Data/Hora obrigatória.")
            return
        nova = {
            "cliente_id":   self._original["cliente_id"],
            "profissional": self._profissional.get().strip() or None,
            "data_hora":    data_hora,
            "motivo":       self._motivo.get().strip() or None,
        }
        try:
            import data as db
            db.remarcar_consulta(self._original["id"], nova)
        except Exception as e:
            self._err.config(text=str(e))
            return
        self.result = nova
        self.destroy()


class _ClientePicker(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Selecionar Cliente")
        self.resizable(False, False)
        self.result: dict | None = None

        self._var = tk.StringVar()
        self._var.trace_add("write", self._on_search)

        top = ttk.Frame(self, padding=8)
        top.pack(fill="x")
        ttk.Entry(top, textvariable=self._var, width=40).pack(fill="x")

        cols = [
            {"id": "nome",     "label": "Nome",     "width": 200},
            {"id": "telefone", "label": "Telefone", "width": 120},
        ]
        self._table = TableView(self, columns=cols)
        self._table.pack(fill="both", expand=True, padx=8, pady=4)
        self._table.tree.bind("<Double-1>", lambda _: self._select())

        btn = ttk.Frame(self, padding=(8, 4))
        btn.pack(fill="x")
        ttk.Button(btn, text="Selecionar", command=self._select).pack(side="right")
        ttk.Button(btn, text="Cancelar",   command=self.destroy).pack(side="right", padx=4)

        self._after_id = None
        self._load("")
        self.transient(parent)
        self.grab_set()
        self.update_idletasks()
        x = parent.winfo_rootx() + (parent.winfo_width() - self.winfo_width()) // 2
        y = parent.winfo_rooty() + (parent.winfo_height() - self.winfo_height()) // 2
        self.geometry(f"+{x}+{y}")
        parent.wait_window(self)

    def _on_search(self, *_):
        if self._after_id:
            self.after_cancel(self._after_id)
        self._after_id = self.after(300, lambda: self._load(self._var.get()))

    def _load(self, busca: str):
        rows = data.listar_clientes(busca)
        self._table.load(rows)

    def _select(self):
        id_ = self._table.selected_id()
        if not id_:
            return
        cliente = data.obter_cliente(id_)
        if cliente:
            self.result = cliente
        self.destroy()
