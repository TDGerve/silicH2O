import tkinter as tk

from src.gui_main import GUI
from src.io import io_handler
from src.spectrum_processing import samples


class app:
    def __init__(self, root):
        self.sample_database = samples()
        self.gui = GUI(root, self.sample_database)


def run_app():

    root = tk.Tk()
    app(root)

    root.mainloop()


if __name__ == "__main__":
    run_app()
