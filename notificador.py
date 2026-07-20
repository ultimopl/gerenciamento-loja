import subprocess
import threading
import time

import data

_INTERVALO_SEG = 5 * 60   # checa a cada 5 minutos
_ANTECEDENCIA  = 30        # notifica 30 min antes
_notificadas: set[int] = set()


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
        subprocess.Popen(
            ["notify-send", "--urgency=normal", "--icon=appointment-new",
             "Consulta em 30 minutos", msg],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )


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
