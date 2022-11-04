import tkinter as tk

from gui_main import GUI


class app:
    def __init__(self, root):
        self.gui = GUI(root)


def run_app():

    root = tk.Tk()
    app(root)

    root.mainloop()


if __name__ == "__main__":
    run_app()
