import glob
import os
import tkinter as tk
import webbrowser
from tkinter import filedialog, simpledialog, ttk
from typing import List

import blinker as bl

from ... import app_configuration

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

on_calibration_window = bl.signal("calibration window")


class Calibration_menu:
    def __init__(self, parent):

        menu = tk.Menu(parent)
        parent.add_cascade(
            menu=menu,
            label="Calibration",
        )

        menu.add_command(label="calibrate", command=self.calibration_window_popup)
        menu.add_command(label="import as project")

    def calibration_window_popup(self):
        on_calibration_window.send()
