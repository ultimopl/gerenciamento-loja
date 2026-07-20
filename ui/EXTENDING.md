# Adicionando uma nova aba

## 1. Criar o módulo

Crie `ui/<modulo>.py`. Todo frame de aba herda de `BaseFrame`:

```python
# ui/financeiro.py
import tkinter as tk
from tkinter import ttk
import data
from ui.base import BaseFrame, SearchBar, TableView

class FinanceiroFrame(BaseFrame):
    def _build(self):
        # monte seus widgets aqui
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        ttk.Label(self, text="Financeiro").grid(row=0, column=0, sticky="w", padx=8, pady=6)

    def _load_data(self, busca: str = ""):
        # carregue dados do banco aqui
        pass
```

`BaseFrame` chama `_build()` e `_load_data()` no `__init__` automaticamente.  
`refresh()` (chamado ao trocar de aba) re-executa `_load_data()` — não precisa sobrescrever.

---

## 2. Registrar no pacote

Em `ui/__init__.py`, adicione a importação:

```python
from .financeiro import FinanceiroFrame
```

---

## 3. Adicionar a aba na janela principal

Em `app.py`, dentro de `_build_notebook`:

```python
self._frames["financeiro"] = FinanceiroFrame(nb)
nb.add(self._frames["financeiro"], text="  Financeiro  ")
```

---

## 4. Adicionar dados ao banco (se necessário)

Em `data.py`:
- Adicione o `CREATE TABLE IF NOT EXISTS` dentro de `init_db()`
- Adicione as funções CRUD seguindo o padrão existente (`listar_`, `salvar_`, `excluir_`)

---

## Componentes reutilizáveis de `base.py`

| Classe | Uso |
|---|---|
| `BaseFrame` | herdar para qualquer frame de aba |
| `BaseDialog` | herdar para formulários modais; implemente `_build_fields` e `_on_save`; `self.result` contém o retorno |
| `SearchBar` | campo de busca com debounce de 300ms; recebe `on_search: Callable[[str], None]` |
| `TableView` | Treeview com scrollbars; recebe `columns=[{"id","label","width"}]`; use `.load(rows)` e `.selected_id()` |
| `FieldGroup` | LabelFrame com grid alinhado; use `.add_entry()`, `.add_spinbox()`, `.add_combobox()` |

---

## Exemplo mínimo completo com dialog

```python
class ItemDialog(BaseDialog):
    def __init__(self, parent, data=None):
        self._nome = tk.StringVar(value=(data or {}).get("nome", ""))
        title = "Editar" if data and data.get("id") else "Novo"
        super().__init__(parent, title=title, data=data)

    def _build_fields(self, frame):
        group = FieldGroup(frame, text="Dados")
        group.pack(fill="both", expand=True)
        group.add_entry("Nome *", self._nome, row=0)
        self._err = ttk.Label(frame, text="", foreground="red")
        self._err.pack()

    def _on_save(self):
        nome = self._nome.get().strip()
        if not nome:
            self._err.config(text="Nome obrigatório.")
            return
        import data as db
        dados = {"nome": nome}
        if self._data.get("id"):
            dados["id"] = self._data["id"]
        db.salvar_item(dados)      # função que você criou em data.py
        self.result = dados
        self.destroy()
```
