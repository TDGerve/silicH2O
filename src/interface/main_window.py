from tkinter import ttk
import tkinter as tk

import pathlib, sys
from typing import List, Dict, Tuple

from .sample_navigation import Sample_navigation

from .menus import io_menu
from .tabs import Baseline_correction_frame
from .plots import Plot
from .screens import Computer_screen

from .. import settings


# Move all constants and settings outside the code

# Don't store widgets in variables, but give them names and call them from their parent, see:
# https://stackoverflow.com/questions/71902896/tkinter-access-specifc-widgets-created-with-for-loop/71906287#71906287

# Set up draw methods to create the GUI, instead of doing it inside the initialiser

# Separate all GUI code from datamanagement and calculations

_main_folder = pathlib.Path(__file__).parents[1]
_theme_file = _main_folder / "theme/breeze.tcl"


class Main_window(tk.Tk):
    def __init__(self, title: str):

        super().__init__()
        self.screen = self.get_screen_info()

        self.title(title)

        self.set_theme()
        self.set_geometry()

        self.create_main_frame()
        self.create_tabs()

    def set_theme(self):
        self.style = ttk.Style()
        self.tk.call("source", _theme_file)
        self.style.theme_use(settings.gui["theme"])
        self.style.configure(".", settings.gui["font"]["family"])

        self.background_color = self.style.lookup(settings.gui["theme"], "background")
        self.background_color = self.winfo_rgb(self.background_color)

    def set_geometry(self):

        width, height = self.screen.resolution

        self.minsize(*settings.gui["geometry"]["size_min"])
        resolution_str = f"{int(width * 0.7)}x{int(height * 0.7)}"

        self.geometry(resolution_str)

        self.resizable(True, True)

        ttk.Sizegrip(self).grid(row=0, sticky=("se"))

        self.rowconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

    def get_screen_info(self) -> None:

        resolution = self.winfo_screenwidth(), self.winfo_screenheight()
        dpi = self.winfo_fpixels("1i")

        return Computer_screen(resolution, dpi)

    def create_menus(self):

        self.option_add("*tearOff", False)
        menubar = tk.Menu(self, name="menus")
        self["menu"] = menubar
        io_menu(menubar)

    def create_navigation_frame(self, variables: Dict, widgets: Dict):
        # Create the two main frames
        Sample_navigation(self, variables, widgets).grid(
            row=0, column=0, rowspan=1, columnspan=1, sticky=("nesw")
        )

    def create_main_frame(self):
        main_frame = ttk.Frame(self, name="main_frame")
        main_frame.grid(row=0, column=1, rowspan=1, columnspan=1, sticky=("nesw"))
        main_frame.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)

    def create_tabs(self):
        main_frame = self.nametowidget("main_frame")
        self.tabs = ttk.Notebook(main_frame, name="tabs")
        self.tabs.grid(column=0, row=0, sticky=("nesw"))
        self.tabs.rowconfigure(0, weight=1)
        self.tabs.columnconfigure(0, weight=1)

        # trigger function on tab change
        self.tabs.bind("<<NotebookTabChanged>>", lambda event: self.on_tab_change)

    def populate_tabs(self, variables: Dict[str, any], widgets: Dict[str, any]):
        frame = self.nametowidget("main_frame")
        tabs = frame.nametowidget("tabs")

        baseline_correction = Baseline_correction_frame(
            tabs, name="baseline_correction", variables=variables, widgets=widgets
        )
        baseline_correction.grid(column=0, row=0, sticky=("nesw"))
        tabs.add(baseline_correction, text="Baseline correction")

    def add_plots(self, plots):
        for name, plot in plots.items():
            frame = self.tabs.nametowidget(name)
            self.set_plot_background_color(plot)
            frame.draw_plot(plot)

    def set_plot_background_color(self, plot: Plot):
        # calculate background color to something matplotlib understands
        background_color = tuple((c / 2**16 for c in self.background_color))
        plot.fig.patch.set_facecolor(background_color)

    def refresh_plots(self):
        # update = {
        # "Baseline correction": self.water_calc.update_plot,
        # "Interpolation": self.interpolation.update_plot,
        # "Host correction": self.subtract.update_plot,
        # }
        # current_tab = self.tabs.tab(self.tabs.select(), "text")
        # update[current_tab]()
        pass

    def on_tab_change(self):
        """
        Refresh plot on the opened tab
        """

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
