import tkinter as tk
from tkinter import filedialog
from typing import List

import blinker as bl
import os, glob

on_samples_added = bl.signal("samples added")


class io_menu:
    def __init__(self, parent):
        self.parent = parent

        io = tk.Menu(parent, name="io")
        parent.add_cascade(menu=io, label="File")

        io.add_command(label="load spectra", command=self.get_files)
        io.add_command(label="load directory", command=self.get_directory)
        io.add_separator()
        io.add_command(label="export results", command=self.export_results)
        io.add_command(label="export sample", command=self.export_sample)
        io.add_command(label="export all samples", command=self.export_all_samples)

        for item in ["export results", "export sample", "export all samples"]:
            io.entryconfigure(item, state=tk.DISABLED)

        self.export_enabled = False

    def load_files(self, files: List[str]):

        on_samples_added.send("import files", files=files)

        if self.export_enabled:
            return

        io = self.parent.nametowidget("io")
        for item in [
            "export results",
            "export sample",
            "export all samples",
        ]:

            io.entryconfigure(item, state=tk.NORMAL)
        self.export_enabled = True

    def get_directory(self):
        try:
            dirname = tk.filedialog.askdirectory(initialdir=os.getcwd())
        except AttributeError:
            print("Opening files cancelled by user")
            return
        files = glob.glob(os.path.join(dirname, "*.txt"))
        if not files:
            return
        self.load_files(files)

    def get_files(self):
        try:
            files = filedialog.askopenfilenames(
                initialdir=os.getcwd(), filetypes=[("txt files", "*.txt")]
            )
        except AttributeError:
            print("Opening files cancelled by user")
            return
        self.load_files(files)

    def export_results(self):
        pass

    def export_sample(self):
        pass

    def export_all_samples(self):
        pass
