import glob
import os
import tkinter as tk
from tkinter import filedialog
from typing import List

import blinker as bl

on_new_project = bl.signal("new project")
on_load_project = bl.signal("load project")
on_samples_added = bl.signal("samples added")

on_save_project = bl.signal("save project")
on_export_results = bl.signal("export results")
on_display_message = bl.signal("display message")


class io_menu:
    def __init__(self, parent):
        self.parent = parent

        io = tk.Menu(parent, name="io")
        parent.add_cascade(menu=io, label="File")

        io.add_command(label="new...", command=self.new_project)
        io.add_command(label="load project", command=self.load_project)
        io.add_separator()
        io.add_command(label="add spectra", command=self.get_files)
        io.add_command(label="add directory", command=self.get_directory)
        io.add_separator()
        io.add_command(label="export results", command=self.export_results)
        io.add_command(label="export sample", command=self.export_sample)
        io.add_command(label="export all samples", command=self.export_all_samples)
        io.add_separator()
        io.add_command(label="save project", command=self.save_project)
        io.add_command(label="save project as", command=self.save_project_as)

        for item in [
            "export results",
            "export sample",
            "export all samples",
            "save project",
            "save project as",
        ]:
            io.entryconfigure(item, state=tk.DISABLED)

        self.export_enabled = False

    def new_project(self):

        on_new_project.send("io")

    def load_files(self, files: List[str]):

        on_samples_added.send("io", files=files)

        if self.export_enabled:
            return

        self.activate_menus()

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

    def load_project(self):

        on_display_message.send(message="loading project...", duration=None)
        try:
            project = filedialog.askopenfilename(
                initialdir=os.getcwd(), filetypes=[("SilicH2O project", "*.h2o")]
            )
        except AttributeError:
            print("Opening files cancelled by user")
            return

        if len(project) == 0:
            return

        on_load_project.send("io", filepath=project)

        on_display_message.send(message="project loaded")

        if self.export_enabled:
            return

        self.activate_menus()

    def export_results(self):

        on_display_message.send(message="exporting results...", duration=None)

        try:
            f = filedialog.asksaveasfilename(
                defaultextension=".csv", title="Export results as..."
            )
        except AttributeError:
            print("Opening files cancelled by user")
            return

        on_export_results.send("io", filepath=f)
        on_display_message.send(message="exporting complete")

    def export_sample(self):
        pass

    def export_all_samples(self):
        pass

    def save_project(self):
        on_save_project.send("io")

    def save_project_as(self):
        try:
            f = filedialog.asksaveasfilename(
                defaultextension=".h2o", title="Save project as..."
            )
        except AttributeError:
            print("Opening files cancelled by user")
            return

        on_save_project.send("io", filepath=f)

    def activate_menus(self):

        io = self.parent.nametowidget("io")

        for item in [
            "export results",
            "export sample",
            "export all samples",
            "save project",
            "save project as",
        ]:

            io.entryconfigure(item, state=tk.NORMAL)
        self.export_enabled = True
