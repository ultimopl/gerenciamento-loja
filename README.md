# Gerenciamento de Loja

Aplicativo desktop para gerenciamento de loja, desenvolvido em Python com interface tkinter.

## Funcionalidades

- **Clientes** — cadastro com CPF, data de nascimento, telefone e documentos anexados
- **Consultas** — agendamento de consultas por cliente com status (Agendada / Realizada / Cancelada)
- **Estoque** — controle de produtos com quantidade, unidade e preço
- **Laudos** — templates de laudos com geração em PDF

## Requisitos

- Python 3.14+
- [uv](https://github.com/astral-sh/uv)

## Como rodar

```bash
uv run main.py
```

## Estrutura

```
main.py        # entrypoint
app.py         # janela principal e notebook de abas
data.py        # acesso ao banco SQLite (loja.db)
ui/
  base.py      # componentes reutilizáveis (BaseFrame, BaseDialog, TableView, …)
  clientes.py
  consultas.py
  estoque.py
  laudos.py
  EXTENDING.md # guia para adicionar novas abas
```
