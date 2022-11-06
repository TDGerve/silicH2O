import tkinter as tk

from ...io import io_handler


class io_menu:
    def __init__(self, parent, io_handler: io_handler):
        self.parent = parent
        self.io_handler = io_handler

        io = tk.Menu(parent, name="io")
        parent.add_cascade(menu=io, label="File")

        io.add_command(label="load spectra", command=self.load_spectra)
        io.add_command(label="load directory", command=self.load_directory)
        io.add_separator()
        io.add_command(label="export results", command=self.export_results)
        io.add_command(label="export sample", command=self.export_sample)
        io.add_command(label="export all samples", command=self.export_all_samples)

        for item in ["export results", "export sample", "export all samples"]:
            io.entryconfigure(item, state=tk.DISABLED)

    def load_spectra(self):
        io = self.parent.nametowidget("io")

        self.io_handler.load_spectra()

        for item in [
            "export results",
            "export sample",
            "export all samples",
        ]:
            io.entryconfigure(item, state=tk.NORMAL)

    def load_directory(self):
        pass

    def export_results(self):
        pass

    def export_sample(self):
        pass

    def export_all_samples(self):
        pass
