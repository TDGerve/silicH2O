import pathlib
import tkinter as tk
from tkinter import filedialog, simpledialog

import blinker as bl

on_import_calibration_project = bl.signal("project calibration")
on_read_calibration_file = bl.signal("read calibration file")
on_save_calibration_as = bl.signal("save calibration as")
on_calibration_plot_change = bl.signal("refresh calibration plot")

calibration_folder = pathlib.Path(__file__).parents[3] / "calibration"


class Calibration_menubar(tk.Menu):
    def __init__(self, parent, name):

        super().__init__(parent, name=name)

        import_menu = tk.Menu()

        self.add_cascade(menu=import_menu, label="Import")
        import_menu.add_command(
            label="current project",
            command=lambda: on_import_calibration_project.send(),
        )
        import_menu.add_command(label="from file", command=self.import_calibration_file)

        file_menu = tk.Menu()
        self.add_cascade(menu=file_menu, label="File")
        file_menu.add_command(label="save", command=lambda: print("do something"))  # CH
        file_menu.add_command(
            label="save as ...", command=self.save_calibration_as
        )  # CH

    def import_calibration_file(self):
        try:
            f = filedialog.askopenfilename(
                initialdir=calibration_folder, filetypes=[(".ch2o files", "*.ch2o")]
            )
        except AttributeError:
            print("Opening files cancelled by user")
            return

        if f is None:
            return

        on_read_calibration_file.send(filepath=f)

    def save_calibration_as(self):

        f = simpledialog.askstring(
            title="calibration", prompt="Save calibration as ..."
        )
        if not f:
            return

        on_save_calibration_as.send(name=f)
        on_calibration_plot_change.send()

    def save_calibration(self):
        on_save_calibration_as.send()
