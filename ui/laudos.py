import re
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

import data
from ui.base import BaseFrame


class LaudosFrame(BaseFrame):
    def _build(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        paned = ttk.PanedWindow(self, orient="horizontal")
        paned.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)

        # ── Painel esquerdo: lista de templates ──────────────────────────
        left = ttk.Frame(paned)
        paned.add(left, weight=1)
        left.rowconfigure(1, weight=1)
        left.columnconfigure(0, weight=1)

        ttk.Label(left, text="Templates", font=("", 10, "bold")).grid(row=0, column=0, sticky="w", pady=(0, 4))

        list_frame = ttk.Frame(left)
        list_frame.grid(row=1, column=0, sticky="nsew")
        list_frame.rowconfigure(0, weight=1)
        list_frame.columnconfigure(0, weight=1)

        self._listbox = tk.Listbox(list_frame, selectmode="single", activestyle="dotbox", width=28)
        vsb = ttk.Scrollbar(list_frame, orient="vertical", command=self._listbox.yview)
        self._listbox.configure(yscrollcommand=vsb.set)
        self._listbox.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        self._listbox.bind("<<ListboxSelect>>", self._on_select)

        left_btn = ttk.Frame(left)
        left_btn.grid(row=2, column=0, sticky="ew", pady=(6, 0))
        ttk.Button(left_btn, text="Novo",    command=self._on_novo).pack(side="left", padx=2)
        ttk.Button(left_btn, text="Excluir", command=self._on_excluir).pack(side="left", padx=2)

        # ── Painel direito: editor ────────────────────────────────────────
        right = ttk.Frame(paned)
        paned.add(right, weight=3)
        right.rowconfigure(1, weight=1)
        right.columnconfigure(0, weight=1)

        title_frame = ttk.Frame(right)
        title_frame.grid(row=0, column=0, sticky="ew", pady=(0, 4))
        ttk.Label(title_frame, text="Título:").pack(side="left")
        self._titulo_var = tk.StringVar()
        ttk.Entry(title_frame, textvariable=self._titulo_var, width=40).pack(side="left", padx=6)

        text_frame = ttk.Frame(right)
        text_frame.grid(row=1, column=0, sticky="nsew")
        text_frame.rowconfigure(0, weight=1)
        text_frame.columnconfigure(0, weight=1)

        self._text = tk.Text(text_frame, wrap="word", undo=True)
        vsb2 = ttk.Scrollbar(text_frame, orient="vertical", command=self._text.yview)
        self._text.configure(yscrollcommand=vsb2.set)
        self._text.grid(row=0, column=0, sticky="nsew")
        vsb2.grid(row=0, column=1, sticky="ns")

        right_btn = ttk.Frame(right)
        right_btn.grid(row=2, column=0, sticky="ew", pady=(6, 0))
        ttk.Button(right_btn, text="Salvar",       command=self._on_salvar).pack(side="left", padx=2)
        ttk.Button(right_btn, text="Exportar PDF", command=self._on_exportar).pack(side="left", padx=2)

        self._templates: list[dict] = []
        self._current_id: int | None = None

    def _load_data(self):
        self._templates = data.listar_templates()
        self._listbox.delete(0, "end")
        for t in self._templates:
            self._listbox.insert("end", t["titulo"])
        self._clear_editor()

    def _clear_editor(self):
        self._current_id = None
        self._titulo_var.set("")
        self._text.delete("1.0", "end")

    def _on_select(self, _event=None):
        sel = self._listbox.curselection()
        if not sel:
            return
        t = self._templates[sel[0]]
        self._current_id = t["id"]
        self._titulo_var.set(t["titulo"])
        self._text.delete("1.0", "end")
        self._text.insert("1.0", t["corpo"])

    def _on_novo(self):
        self._listbox.selection_clear(0, "end")
        self._clear_editor()
        self._titulo_var.set("Novo Template")
        self._text.focus_set()

    def _on_salvar(self):
        titulo = self._titulo_var.get().strip()
        corpo = self._text.get("1.0", "end-1c").strip()
        if not titulo:
            messagebox.showwarning("Atenção", "Informe um título.")
            return
        dados = {"titulo": titulo, "corpo": corpo}
        if self._current_id:
            dados["id"] = self._current_id
        new_id = data.salvar_template(dados)
        self._current_id = new_id
        self._load_data()
        for i, t in enumerate(self._templates):
            if t["id"] == new_id:
                self._listbox.selection_set(i)
                break

    def _on_excluir(self):
        if not self._current_id:
            messagebox.showinfo("Atenção", "Selecione um template.")
            return
        if messagebox.askyesno("Confirmar", "Excluir este template?"):
            data.excluir_template(self._current_id)
            self._load_data()

    def _on_exportar(self):
        titulo = self._titulo_var.get().strip()
        corpo = self._text.get("1.0", "end-1c")
        if not corpo.strip():
            messagebox.showwarning("Atenção", "O template está vazio.")
            return
        ExportarPDFDialog(self, titulo=titulo, corpo=corpo)


class ExportarPDFDialog(tk.Toplevel):
    _VAR_RE = re.compile(r"\{\{(\w+)\}\}")

    def __init__(self, parent, titulo: str, corpo: str):
        super().__init__(parent)
        self.title("Exportar PDF")
        self.resizable(False, False)
        self._titulo = titulo
        self._corpo = corpo
        self._vars: dict[str, tk.StringVar] = {}

        self._clientes = data.listar_clientes()
        self._cliente_var = tk.StringVar()
        self._dest_var = tk.StringVar(value=str(Path.home()))

        self._build()
        self.transient(parent)
        self.grab_set()
        x = parent.winfo_rootx() + (parent.winfo_width() - self.winfo_reqwidth()) // 2
        y = parent.winfo_rooty() + (parent.winfo_height() - self.winfo_reqheight()) // 2
        self.geometry(f"+{x}+{y}")
        parent.wait_window(self)

    def _build(self):
        frame = ttk.Frame(self, padding=12)
        frame.pack(fill="both", expand=True)

        # Cliente
        ttk.Label(frame, text="Cliente (opcional):").grid(row=0, column=0, sticky="w", pady=3)
        nomes = [""] + [c["nome"] for c in self._clientes]
        cb = ttk.Combobox(frame, textvariable=self._cliente_var, values=nomes, width=34)
        cb.grid(row=0, column=1, sticky="ew", pady=3, padx=(8, 0))

        # Variáveis detectadas no corpo
        varnames = list(dict.fromkeys(self._VAR_RE.findall(self._corpo)))
        if varnames:
            sep = ttk.Separator(frame, orient="horizontal")
            sep.grid(row=1, column=0, columnspan=2, sticky="ew", pady=8)
            ttk.Label(frame, text="Variáveis do template:", font=("", 9, "bold")).grid(
                row=2, column=0, columnspan=2, sticky="w"
            )
            for i, name in enumerate(varnames):
                var = tk.StringVar()
                self._vars[name] = var
                ttk.Label(frame, text=f"{{{{{name}}}}}").grid(row=3 + i, column=0, sticky="w", pady=2, padx=(0, 8))
                ttk.Entry(frame, textvariable=var, width=35).grid(row=3 + i, column=1, sticky="ew", pady=2)
            next_row = 3 + len(varnames) + 1
        else:
            next_row = 2

        sep2 = ttk.Separator(frame, orient="horizontal")
        sep2.grid(row=next_row, column=0, columnspan=2, sticky="ew", pady=8)

        ttk.Label(frame, text="Salvar em:").grid(row=next_row + 1, column=0, sticky="w", pady=3)
        dest_frame = ttk.Frame(frame)
        dest_frame.grid(row=next_row + 1, column=1, sticky="ew", pady=3, padx=(8, 0))
        ttk.Entry(dest_frame, textvariable=self._dest_var, width=26).pack(side="left")
        ttk.Button(dest_frame, text="...", width=3, command=self._choose_dest).pack(side="left", padx=(4, 0))

        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=next_row + 2, column=0, columnspan=2, sticky="e", pady=(12, 0))
        ttk.Button(btn_frame, text="Cancelar", command=self.destroy).pack(side="right")
        ttk.Button(btn_frame, text="Gerar PDF", command=self._on_gerar).pack(side="right", padx=(0, 6))

    def _choose_dest(self):
        folder = filedialog.askdirectory(title="Escolher pasta de destino")
        if folder:
            self._dest_var.set(folder)

    def _on_gerar(self):
        corpo = self._corpo
        for name, var in self._vars.items():
            corpo = corpo.replace(f"{{{{{name}}}}}", var.get())

        dest_dir = Path(self._dest_var.get())
        safe_title = re.sub(r'[^\w\s-]', '', self._titulo).strip().replace(" ", "_") or "laudo"
        dest_file = dest_dir / f"{safe_title}.pdf"

        try:
            from fpdf import FPDF
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Helvetica", "B", 14)
            pdf.cell(0, 10, self._titulo, ln=True, align="C")
            pdf.ln(4)
            pdf.set_font("Helvetica", size=11)
            for line in corpo.split("\n"):
                pdf.multi_cell(0, 7, line)
            pdf.output(str(dest_file))
        except Exception as e:
            messagebox.showerror("Erro ao gerar PDF", str(e))
            return

        if messagebox.askyesno("PDF gerado", f"Salvo em:\n{dest_file}\n\nAbrir agora?"):
            import os, sys, subprocess
            if sys.platform == "win32":
                os.startfile(str(dest_file))
            elif sys.platform == "darwin":
                subprocess.Popen(["open", str(dest_file)])
            else:
                subprocess.Popen(["xdg-open", str(dest_file)])
        self.destroy()
