import tkinter as tk

import data
import notificador
from app import App


def main():
    data.init_db()
    notificador.iniciar()
    root = tk.Tk()
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
