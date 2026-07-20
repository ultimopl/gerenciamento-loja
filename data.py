import shutil
import sqlite3
from pathlib import Path

_DB_PATH = Path(__file__).parent / "loja.db"
_DOCS_DIR = Path(__file__).parent / "documentos"


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(_DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    _DOCS_DIR.mkdir(exist_ok=True)
    with _connect() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS clientes (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                nome       TEXT NOT NULL,
                cpf        TEXT UNIQUE,
                nascimento TEXT,
                telefone   TEXT
            );
            CREATE TABLE IF NOT EXISTS documentos (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                cliente_id INTEGER REFERENCES clientes(id) ON DELETE CASCADE,
                nome       TEXT NOT NULL,
                caminho    TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS produtos (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                nome       TEXT NOT NULL,
                quantidade INTEGER DEFAULT 0,
                unidade    TEXT DEFAULT 'un',
                preco      REAL DEFAULT 0.0
            );
            CREATE TABLE IF NOT EXISTS laudos_templates (
                id     INTEGER PRIMARY KEY AUTOINCREMENT,
                titulo TEXT NOT NULL,
                corpo  TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS consultas (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                cliente_id INTEGER REFERENCES clientes(id) ON DELETE CASCADE,
                data_hora  TEXT NOT NULL,
                motivo     TEXT,
                status     TEXT DEFAULT 'Agendada'
            );
        """)


# ── Clientes ────────────────────────────────────────────────────────────────

def listar_clientes(busca: str = "") -> list[dict]:
    with _connect() as conn:
        if busca:
            like = f"%{busca}%"
            rows = conn.execute(
                "SELECT * FROM clientes WHERE nome LIKE ? OR cpf LIKE ? ORDER BY nome",
                (like, like),
            ).fetchall()
        else:
            rows = conn.execute("SELECT * FROM clientes ORDER BY nome").fetchall()
    return [dict(r) for r in rows]


def obter_cliente(id: int) -> dict | None:
    with _connect() as conn:
        row = conn.execute("SELECT * FROM clientes WHERE id = ?", (id,)).fetchone()
    return dict(row) if row else None


def salvar_cliente(dados: dict) -> int:
    with _connect() as conn:
        if dados.get("id"):
            conn.execute(
                "UPDATE clientes SET nome=?, cpf=?, nascimento=?, telefone=? WHERE id=?",
                (dados["nome"], dados.get("cpf"), dados.get("nascimento"), dados.get("telefone"), dados["id"]),
            )
            return dados["id"]
        else:
            cur = conn.execute(
                "INSERT INTO clientes (nome, cpf, nascimento, telefone) VALUES (?,?,?,?)",
                (dados["nome"], dados.get("cpf"), dados.get("nascimento"), dados.get("telefone")),
            )
            return cur.lastrowid


def excluir_cliente(id: int):
    with _connect() as conn:
        conn.execute("DELETE FROM clientes WHERE id=?", (id,))


# ── Documentos ──────────────────────────────────────────────────────────────

def listar_documentos(cliente_id: int) -> list[dict]:
    with _connect() as conn:
        rows = conn.execute(
            "SELECT * FROM documentos WHERE cliente_id=? ORDER BY nome", (cliente_id,)
        ).fetchall()
    return [dict(r) for r in rows]


def adicionar_documento(cliente_id: int, caminho_origem: str, nome: str | None = None) -> int:
    origem = Path(caminho_origem)
    dest_dir = _DOCS_DIR / str(cliente_id)
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / origem.name
    shutil.copy2(origem, dest)
    nome = nome or origem.name
    with _connect() as conn:
        cur = conn.execute(
            "INSERT INTO documentos (cliente_id, nome, caminho) VALUES (?,?,?)",
            (cliente_id, nome, str(dest.resolve())),
        )
        return cur.lastrowid


def remover_documento(id: int):
    with _connect() as conn:
        row = conn.execute("SELECT caminho FROM documentos WHERE id=?", (id,)).fetchone()
        if row:
            p = Path(row["caminho"])
            if p.exists():
                p.unlink()
        conn.execute("DELETE FROM documentos WHERE id=?", (id,))


# ── Estoque ─────────────────────────────────────────────────────────────────

def listar_produtos(busca: str = "") -> list[dict]:
    with _connect() as conn:
        if busca:
            rows = conn.execute(
                "SELECT * FROM produtos WHERE nome LIKE ? ORDER BY nome", (f"%{busca}%",)
            ).fetchall()
        else:
            rows = conn.execute("SELECT * FROM produtos ORDER BY nome").fetchall()
    return [dict(r) for r in rows]


def salvar_produto(dados: dict) -> int:
    with _connect() as conn:
        if dados.get("id"):
            conn.execute(
                "UPDATE produtos SET nome=?, quantidade=?, unidade=?, preco=? WHERE id=?",
                (dados["nome"], dados.get("quantidade", 0), dados.get("unidade", "un"), dados.get("preco", 0.0), dados["id"]),
            )
            return dados["id"]
        else:
            cur = conn.execute(
                "INSERT INTO produtos (nome, quantidade, unidade, preco) VALUES (?,?,?,?)",
                (dados["nome"], dados.get("quantidade", 0), dados.get("unidade", "un"), dados.get("preco", 0.0)),
            )
            return cur.lastrowid


def excluir_produto(id: int):
    with _connect() as conn:
        conn.execute("DELETE FROM produtos WHERE id=?", (id,))


def ajustar_estoque(id: int, delta: int):
    with _connect() as conn:
        conn.execute(
            "UPDATE produtos SET quantidade = MAX(0, quantidade + ?) WHERE id=?", (delta, id)
        )


# ── Laudos / Templates ──────────────────────────────────────────────────────

def listar_templates() -> list[dict]:
    with _connect() as conn:
        rows = conn.execute("SELECT * FROM laudos_templates ORDER BY titulo").fetchall()
    return [dict(r) for r in rows]


def salvar_template(dados: dict) -> int:
    with _connect() as conn:
        if dados.get("id"):
            conn.execute(
                "UPDATE laudos_templates SET titulo=?, corpo=? WHERE id=?",
                (dados["titulo"], dados["corpo"], dados["id"]),
            )
            return dados["id"]
        else:
            cur = conn.execute(
                "INSERT INTO laudos_templates (titulo, corpo) VALUES (?,?)",
                (dados["titulo"], dados["corpo"]),
            )
            return cur.lastrowid


def excluir_template(id: int):
    with _connect() as conn:
        conn.execute("DELETE FROM laudos_templates WHERE id=?", (id,))


# ── Consultas ────────────────────────────────────────────────────────────────

def listar_consultas(busca: str = "") -> list[dict]:
    with _connect() as conn:
        if busca:
            like = f"%{busca}%"
            rows = conn.execute(
                """SELECT c.*, cl.nome AS cliente_nome
                   FROM consultas c
                   JOIN clientes cl ON cl.id = c.cliente_id
                   WHERE cl.nome LIKE ? OR c.motivo LIKE ? OR c.data_hora LIKE ?
                   ORDER BY c.data_hora""",
                (like, like, like),
            ).fetchall()
        else:
            rows = conn.execute(
                """SELECT c.*, cl.nome AS cliente_nome
                   FROM consultas c
                   JOIN clientes cl ON cl.id = c.cliente_id
                   ORDER BY c.data_hora"""
            ).fetchall()
    return [dict(r) for r in rows]


def obter_consulta(id: int) -> dict | None:
    with _connect() as conn:
        row = conn.execute(
            """SELECT c.*, cl.nome AS cliente_nome
               FROM consultas c
               JOIN clientes cl ON cl.id = c.cliente_id
               WHERE c.id = ?""",
            (id,),
        ).fetchone()
    return dict(row) if row else None


def salvar_consulta(dados: dict) -> int:
    with _connect() as conn:
        if dados.get("id"):
            conn.execute(
                "UPDATE consultas SET cliente_id=?, data_hora=?, motivo=?, status=? WHERE id=?",
                (dados["cliente_id"], dados["data_hora"], dados.get("motivo"), dados.get("status", "Agendada"), dados["id"]),
            )
            return dados["id"]
        else:
            cur = conn.execute(
                "INSERT INTO consultas (cliente_id, data_hora, motivo, status) VALUES (?,?,?,?)",
                (dados["cliente_id"], dados["data_hora"], dados.get("motivo"), dados.get("status", "Agendada")),
            )
            return cur.lastrowid


def excluir_consulta(id: int):
    with _connect() as conn:
        conn.execute("DELETE FROM consultas WHERE id=?", (id,))
