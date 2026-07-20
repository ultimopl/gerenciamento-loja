import tkinter as tk

import data
from app import App


def main():
    data.init_db()
    root = tk.Tk()
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
