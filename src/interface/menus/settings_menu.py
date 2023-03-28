# import glob
# import os
import tkinter as tk
import webbrowser

import blinker as bl

# from tkinter import filedialog, simpledialog, ttk
# from typing import List


# from ... import app_configuration

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


class Settings_menu:
    def __init__(self, parent):

        menu = tk.Menu(parent)
        parent.add_cascade(menu=menu, label="Settings")

        glass_menu = tk.Menu(menu)
        menu.add_cascade(menu=glass_menu, label="glass")

        glass_menu.add_command(
            label="current as default", command=self.current_glass_as_default
        )
        glass_menu.add_command(
            label="restore defaults",
            command=lambda: self.restore_defaults(type="glass"),
        )

        interference_menu = tk.Menu(menu)
        menu.add_cascade(menu=glass_menu, label="interference")
        interference_menu.add_command(
            label="current as default",
            command=self.current_interference_as_default,
        )
        interference_menu.add_command(
            label="restore defaults",
            command=lambda: self.restore_defaults(type="interference"),
        )

        menu.add_separator()
        menu.add_command(label="help", command=self.help)

    def help(*args):
        webbrowser.open_new("https://silich2o.readthedocs.io/en/latest/")

    def restore_defaults(self, type: str):
        on_restore_default_settings.send(type=type)

    def current_glass_as_default(self, *args):
        on_set_default_glass_settings.send()

    def current_interference_as_default(self, *args):
        on_set_default_interference_settings.send()
