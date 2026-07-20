# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running

```bash
uv run main.py
```

## Architecture

Desktop GUI app (tkinter) for store management. Three layers:

- **`main.py`** — entry point; calls `data.init_db()` then starts tkinter loop
- **`data.py`** — all SQLite access; functions follow naming: `listar_*`, `salvar_*`, `excluir_*`; uses `loja.db` file and copies uploaded files to `documentos/<cliente_id>/`
- **`app.py`** — `App` class; builds `ttk.Notebook` with one tab per frame; calls `frame.refresh()` on tab change
- **`ui/`** — one file per tab (`clientes.py`, `estoque.py`, `laudos.py`); `base.py` has shared widgets

## UI base classes (`ui/base.py`)

| Class | Purpose |
|---|---|
| `BaseFrame` | Inherit for any tab frame; implement `_build()` and `_load_data()` |
| `BaseDialog` | Modal form; implement `_build_fields()` and `_on_save()`; result in `self.result` |
| `SearchBar` | Search field with 300ms debounce; takes `on_search: Callable[[str], None]` |
| `TableView` | Treeview with scrollbars; `.load(rows)` and `.selected_id()` |
| `FieldGroup` | LabelFrame with grid; `.add_entry()`, `.add_spinbox()`, `.add_combobox()` |

## Adding a new tab

See `ui/EXTENDING.md` for full walkthrough. Short version:
1. Create `ui/<module>.py` with class inheriting `BaseFrame`
2. Export from `ui/__init__.py`
3. Register in `app.py` `_build_notebook()`
4. Add schema + CRUD functions to `data.py` `init_db()`

## Dependencies

`fpdf2` (PDF generation), `matplotlib` (charts). Managed with `uv`.
