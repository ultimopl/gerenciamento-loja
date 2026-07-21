import subprocess
import sys
import threading
import time

import data

_INTERVALO_SEG = 5 * 60
_ANTECEDENCIA  = 30
_notificadas: set[int] = set()


def _notificar(titulo: str, msg: str):
    if sys.platform == "win32":
        try:
            from ctypes import windll
            windll.user32.MessageBoxW(0, msg, titulo, 0x40)
        except Exception:
            pass
    else:
        subprocess.Popen(
            ["notify-send", "--urgency=normal", "--icon=appointment-new", titulo, msg],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )


def _checar():
    consultas = data.consultas_proximas(_ANTECEDENCIA)
    for c in consultas:
        if c["id"] in _notificadas:
            continue
        _notificadas.add(c["id"])
        msg = f"{c['data_hora']} — {c['cliente_nome']}"
        if c.get("profissional"):
            msg += f"\nProfissional: {c['profissional']}"
        if c.get("motivo"):
            msg += f"\nMotivo: {c['motivo']}"
        _notificar("Consulta em 30 minutos", msg)


def _loop():
    while True:
        try:
            _checar()
        except Exception:
            pass
        time.sleep(_INTERVALO_SEG)


def iniciar():
    t = threading.Thread(target=_loop, daemon=True)
    t.start()
