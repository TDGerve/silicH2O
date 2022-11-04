from tkinter import ttk
import tkinter as tk

import pathlib
import json

from .menus import io_menu
from .. import settings
from ..spectrum_processing.sample_database import samples
from ..sample_navigation import sample_selection
from ..io import io_handler


# Move all constants and settings outside the code

# Don't store widgets in variables, but give them names and call them from their parent, see:
# https://stackoverflow.com/questions/71902896/tkinter-access-specifc-widgets-created-with-for-loop/71906287#71906287

# Set up draw methods to create the GUI, instead of doing it inside the initialiser

# Separate all GUI code from datamanagement and calculations

_main_folder = pathlib.Path(__file__).parents[1]
_theme_file = _main_folder / "theme/breeze.tcl"


class GUI:
    def __init__(self, root: tk.Tk, sample_database: samples):

        self.root = root
        self.root.title("silic-H2O by Thomas van Gerve")

        self.set_theme()
        self.set_geometry()

        self.create_frames(sample_database)
        self.io_handler = io_handler(
            sample_database, self.root.nametowidget("sample_selection")
        )
        self.create_menus(self.io_handler)
        self.create_tabs()

    def set_theme(self):
        self.style = ttk.Style()
        self.root.tk.call("source", _theme_file)
        self.style.theme_use(settings.gui["theme"])
        self.style.configure(".", settings.gui["font"]["family"])

    def set_geometry(self):
        self.root.minsize(*settings.gui["geometry"]["size_min"])
        self.root.geometry(settings.gui["geometry"]["size"])
        self.root.resizable(True, True)

        ttk.Sizegrip(self.root).grid(row=0, sticky=("se"))

        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)

    def create_menus(self, io_handler: io_handler):

        self.root.option_add("*tearOff", False)
        menubar = tk.Menu(self.root, name="menus")
        self.root["menu"] = menubar
        io_menu(menubar, io_handler)

    def create_frames(self, sample_database):
        # Create the two main frames
        sample_selection(self.root, sample_database, name="sample_selection").grid(
            row=0, column=0, rowspan=1, columnspan=1, sticky=("nesw")
        )

        ttk.Frame(self.root, name="main_frame").grid(
            row=0, column=1, rowspan=1, columnspan=1, sticky=("nesw")
        )

        for w in ["sample_selection", "main_frame"]:
            self.root.nametowidget(w).rowconfigure(0, weight=1)
            self.root.nametowidget(w).columnconfigure(0, weight=1)

    def create_tabs(self):
        main_frame = self.root.nametowidget("main_frame")
        tabs = ttk.Notebook(main_frame, name="tabs")

        # self.baseline_tab = baseline(self.tabs, self)
        # self.interpolation = interpolation(self.tabs, self)
        # self.subtract = subtraction(self.tabs, self)

        tabs.grid(column=0, row=0, sticky=("nesw"))
        # self.water_calc.grid(column=0, row=0, sticky=("nesw"))
        # self.interpolation.grid(column=0, row=0, sticky=("nesw"))
        # self.subtract.grid(column=0, row=0, sticky=("nesw"))
        # # Label the notebook tabs
        # self.tabs.add(self.water_calc, text="Baseline correction")
        # self.tabs.add(self.interpolation, text="Interpolation")
        # self.tabs.add(self.subtract, text="Host correction")
        # Adjust resizability

        tabs.rowconfigure(0, weight=1)
        tabs.columnconfigure(0, weight=1)
        # trigger function on tab change
        # tabs.bind("<<NotebookTabChanged>>", self.on_tab_change)

    def refresh_plots(self):
        # update = {
        # "Baseline correction": self.water_calc.update_plot,
        # "Interpolation": self.interpolation.update_plot,
        # "Host correction": self.subtract.update_plot,
        # }
        # current_tab = self.tabs.tab(self.tabs.select(), "text")
        # update[current_tab]()
        pass

    def _on_tab_change(self, event):
        """
        Refresh plot on the opened tab
        """

        pass
        # tab = event.widget.tab("current")["text"]

        # update = {
        #     "Baseline correction": self.water_calc.update_plot,
        #     "Interpolation": self.interpolation.update_plot,
        #     "Host correction": self.subtract.update_plot,
        # }

        # if self.current_sample:
        #     # selected_sample = self.current_sample.index
        #     update[tab]()
        pass


# # Grab some theme elements, for passing on to widgets
# self.font = style.lookup(theme, "font")
# self.fontsize = 13
# self.bgClr = style.lookup(theme, "background")
# # calculate background color to something matplotlib understands
# self.bgClr_plt = tuple((c / 2**16 for c in root.winfo_rgb(self.bgClr)))

# ##### INITIALISE VARIABLES #####
# self.data_bulk = None
# self.current_sample = None

# ##### INITIATE SETTINGS #####
# self.settings = settings(root, self)

# # Create tabs inside the main frame
