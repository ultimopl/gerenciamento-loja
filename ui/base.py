import tkinter as tk
from tkinter import ttk
from typing import Callable


class BaseFrame(ttk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self._build()
        self._load_data()

    def _build(self):
        raise NotImplementedError

    def _load_data(self):
        raise NotImplementedError

    def refresh(self):
        self._load_data()


class SearchBar(ttk.Frame):
    def __init__(self, parent, on_search: Callable[[str], None], placeholder: str = "Buscar...", **kwargs):
        super().__init__(parent, **kwargs)
        self._on_search = on_search
        self._after_id = None

        self._var = tk.StringVar()
        self._var.trace_add("write", self._schedule)

        entry = ttk.Entry(self, textvariable=self._var, width=40)
        entry.pack(side="left", padx=(0, 4))
        ttk.Button(self, text="✕", width=3, command=self.clear).pack(side="left")

    def _schedule(self, *_):
        if self._after_id:
            self.after_cancel(self._after_id)
        self._after_id = self.after(300, lambda: self._on_search(self._var.get()))

    def clear(self):
        self._var.set("")


class TableView(ttk.Frame):
    def __init__(self, parent, columns: list[dict], on_select: Callable | None = None, **kwargs):
        super().__init__(parent, **kwargs)
        self._col_ids = [c["id"] for c in columns]

        self.tree = ttk.Treeview(self, columns=self._col_ids, show="headings", selectmode="browse")
        vsb = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(self, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        for col in columns:
            self.tree.heading(col["id"], text=col["label"])
            self.tree.column(col["id"], width=col.get("width", 120), anchor=col.get("anchor", "w"))

        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        if on_select:
            self.tree.bind("<<TreeviewSelect>>", lambda _e: on_select())

    def load(self, rows: list[dict]):
        self.tree.delete(*self.tree.get_children())
        for row in rows:
            values = [row.get(c, "") for c in self._col_ids]
            self.tree.insert("", "end", iid=str(row.get("id", "")), values=values)

    def selected_id(self) -> int | None:
        sel = self.tree.selection()
        return int(sel[0]) if sel else None

    def clear(self):
        self.tree.delete(*self.tree.get_children())


class BaseDialog(tk.Toplevel):
    def __init__(self, parent, title: str, data: dict | None = None):
        super().__init__(parent)
        self.title(title)
        self.resizable(False, False)
        self.result: dict | None = None
        self._data = data or {}

        main = ttk.Frame(self, padding=12)
        main.pack(fill="both", expand=True)

        fields_frame = ttk.Frame(main)
        fields_frame.pack(fill="both", expand=True, pady=(0, 12))
        self._build_fields(fields_frame)

        btn_frame = ttk.Frame(main)
        btn_frame.pack(fill="x")
        ttk.Button(btn_frame, text="Salvar", command=self._on_save).pack(side="right", padx=(4, 0))
        ttk.Button(btn_frame, text="Cancelar", command=self._close).pack(side="right")

        self.transient(parent)
        self.grab_set()
        self.update_idletasks()
        x = parent.winfo_rootx() + (parent.winfo_width() - self.winfo_width()) // 2
        y = parent.winfo_rooty() + (parent.winfo_height() - self.winfo_height()) // 2
        self.geometry(f"+{x}+{y}")
        parent.wait_window(self)

    def _build_fields(self, frame: ttk.Frame):
        raise NotImplementedError

    def _on_save(self):
        raise NotImplementedError

    def _close(self):
        self.destroy()


class FieldGroup(ttk.LabelFrame):
    def __init__(self, parent, text: str = "", **kwargs):
        super().__init__(parent, text=text, padding=8, **kwargs)
        self.columnconfigure(1, weight=1)

    def _label(self, text: str, row: int):
        ttk.Label(self, text=text).grid(row=row, column=0, sticky="w", padx=(0, 8), pady=3)

    def add_entry(self, label: str, var: tk.StringVar, row: int, **kwargs) -> ttk.Entry:
        self._label(label, row)
        e = ttk.Entry(self, textvariable=var, **kwargs)
        e.grid(row=row, column=1, sticky="ew", pady=3)
        return e

    def add_spinbox(self, label: str, var: tk.IntVar, row: int, **kwargs) -> ttk.Spinbox:
        self._label(label, row)
        s = ttk.Spinbox(self, textvariable=var, **kwargs)
        s.grid(row=row, column=1, sticky="ew", pady=3)
        return s

    def add_combobox(self, label: str, var: tk.StringVar, values: list, row: int) -> ttk.Combobox:
        self._label(label, row)
        c = ttk.Combobox(self, textvariable=var, values=values, state="readonly")
        c.grid(row=row, column=1, sticky="ew", pady=3)
        return c
