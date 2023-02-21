import glob
import os
import tkinter as tk
from tkinter import filedialog, simpledialog
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


on_display_message = bl.signal("display message")


class IO_menu:
    def __init__(self, parent):
        self.parent = parent

        menu = tk.Menu(parent, name="io_menu")
        parent.add_cascade(menu=menu, label="File")

        menu.add_command(label="new...", command=self.new_project)
        menu.add_command(label="load project", command=self.load_project)
        menu.add_separator()
        menu.add_command(label="add spectra", command=self.get_files)
        menu.add_command(label="add directory", command=self.get_directory)
        menu.add_separator()
        menu.add_command(label="export results", command=self.export_results)
        menu.add_command(label="export sample", command=self.export_sample)
        menu.add_command(label="export all", command=self.export_all)
        menu.add_separator()
        menu.add_command(label="save project", command=self.save_project)
        menu.add_command(label="save project as", command=self.save_project_as)

        for item in [
            "export results",
            "export sample",
            "export all",
            "save project",
            "save project as",
        ]:
            menu.entryconfigure(item, state=tk.DISABLED)

        self.export_enabled = False

    def get_name_delimiter(self):
        delimeter_init = app_configuration.general["name_separator"]
        delimiter = simpledialog.askstring(
            title="Settings",
            prompt="Sample name delimeter:",
            initialvalue=delimeter_init,
        )
        return delimiter

    def new_project(self):

        on_new_project.send("menu")

    def load_files(self, files: List[str], name_delimiter):

        on_samples_added.send("menu", files=files, name_delimiter=name_delimiter)

        if self.export_enabled:
            return

        self.activate_menus()

    def get_directory(self):

        on_display_message.send(message="adding directory...", duration=None)

        try:
            dirname = tk.filedialog.askdirectory(initialdir=os.getcwd())
        except AttributeError:
            print("Opening files cancelled by user")
            return
        files = glob.glob(os.path.join(dirname, "*.txt"))
        if not files:
            return
        delimiter = self.get_name_delimiter()
        self.load_files(files, name_delimiter=delimiter)
        on_display_message.send(message="directory added!")

    def get_files(self):

        try:
            files = filedialog.askopenfilenames(
                initialdir=os.getcwd(), filetypes=[("txt files", "*.txt")]
            )
        except AttributeError:
            print("Opening files cancelled by user")
            return
        delimiter = self.get_name_delimiter()
        self.load_files(files, name_delimiter=delimiter)

    def load_project(self):

        try:
            project = filedialog.askopenfilename(
                initialdir=os.getcwd(), filetypes=[("SilicH2O project", "*.h2o")]
            )
        except AttributeError:
            print("Opening files cancelled by user")
            return

        if len(project) == 0:
            return

        on_load_project.send("menu", filepath=project)

        if self.export_enabled:
            return

        self.activate_menus()

    def export_results(self):

        try:
            f = filedialog.asksaveasfilename(
                defaultextension=".csv", title="Export results as..."
            )
        except AttributeError:
            print("Opening files cancelled by user")
            return

        on_export_results.send("menu", filepath=f)

    def export_sample(self):

        try:
            f = filedialog.asksaveasfilename(
                defaultextension=".csv", title="Export sample as ..."
            )
        except AttributeError:
            print("Exporting cancelled by user")
            return

        on_export_sample.send(filepath=f)

    def export_all(self):
        try:
            dir = filedialog.askdirectory(initialdir=os.getcwd())
        except AttributeError:
            print("Saving file cancelled by user")
            return

        on_export_all.send(folderpath=dir)

    def save_project(self):
        on_save_project.send("menu")

    def save_project_as(self):
        try:
            f = filedialog.asksaveasfilename(
                defaultextension=".h2o", title="Save project as..."
            )
        except AttributeError:
            print("Opening files cancelled by user")
            return

        on_save_project.send("menu", filepath=f)

    def activate_menus(self):

        menu = self.parent.nametowidget("io_menu")

        for item in [
            "export results",
            "export sample",
            "export all",
            "save project",
            "save project as",
        ]:

            menu.entryconfigure(item, state=tk.NORMAL)
        self.export_enabled = True
