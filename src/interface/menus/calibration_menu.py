import os
import pathlib
import sys
import tkinter as tk
from tkinter import filedialog, messagebox

import blinker as bl

on_new_project = bl.signal("new project")
on_load_project = bl.signal("load project")
on_samples_added = bl.signal("samples added")

on_save_project = bl.signal("save project")
on_export_results = bl.signal("export results")
on_export_sample = bl.signal("export sample")
on_export_all = bl.signal("export all")

on_set_default_glass_settings = bl.signal("set default glass")
on_set_default_interference_settings = bl.signal("set default interference")
on_restore_default_settings = bl.signal("restore default settings")


on_display_message = bl.signal("display message")
on_import_calibration_project = bl.signal("project calibration")
on_calibration_window = bl.signal("calibration window")
on_read_calibration_file = bl.signal("read calibration file")

on_activate_menus = bl.signal("activate menus")


if getattr(sys, "frozen", False):
    EXE_LOCATION = pathlib.Path(os.path.dirname(sys.executable))  # cx_Freeze frozen
    if sys.platform == "darwin":
        # from mac bundle
        calibration_folder = EXE_LOCATION.parents[2] / "calibration"
    else:
        calibration_folder = EXE_LOCATION.parents[0] / "calibration"
else:
    calibration_folder = pathlib.Path(__file__).parents[2] / "calibration"


class Calibration_menu:
    def __init__(self, parent):
        menu = tk.Menu(parent)
        parent.add_cascade(
            menu=menu,
            label="Calibration",
        )

        menu.add_command(label="calibrate", command=self.calibration_window_popup)
        menu.add_command(
            label="import calibration as project", command=self.import_project
        )

    def calibration_window_popup(self):
        on_calibration_window.send()

    def import_project(self):
        result = messagebox.askokcancel(
            title="confirm",
            message="Unsaved progress will be lost.\nAre you sure?",
            icon="question",
        )
        if not result:
            return

        try:
            project = filedialog.askopenfilename(
                initialdir=calibration_folder / "projects",
                filetypes=[("SilicH2O project", "*.h2o")],
            )

        except AttributeError:
            print("Opening files cancelled by user")
            return

        if len(project) == 0:
            return

        name = pathlib.Path(project).stem

        on_load_project.send("menu", filepath=project)
        on_import_calibration_project.send(update_gui=False)

        calibration_file = calibration_folder / f"{name}.cH2O"
        on_read_calibration_file.send(
            filepath=calibration_file, which=["H2Oreference", "use"], update_gui=False
        )

        on_activate_menus.send()
