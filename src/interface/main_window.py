from tkinter import ttk
import tkinter as tk

import pathlib
from typing import Dict, Any

from .sample_navigation import Sample_navigation
from .menus import io_menu
from .tabs import Baseline_correction_frame
from .screens import Computer_screen

from .. import settings

_main_folder = pathlib.Path(__file__).parents[1]
_theme_file = _main_folder / "theme/breeze.tcl"

_font = settings.gui["font"]["family"]
_fontsize = settings.gui["font"]["size"]


class Main_window(tk.Tk):
    def __init__(self, title: str, variables: Dict[str, Any], widgets: Dict[str, Any]):

        super().__init__()
        self.screen = self.get_screen_info()

        self.title(title)

        self.set_theme()
        self.set_geometry()

        self.create_main_frame()
        self.create_navigation_frame(variables, widgets)
        self.create_tabs()

        self.populate_tabs(variables, widgets)

        self.create_menus()

        # Give focus to the main window when pressing return
        self.bind("<Return>", lambda event: self.focus_set())

    def set_theme(self):
        self.style = ttk.Style()
        self.tk.call("source", _theme_file)
        self.style.theme_use(settings.gui["theme"])
        self.style.configure(".", _font)

        self.style.configure(
            "TNotebook.Tab", font=(_font, _fontsize, "bold"), padding=[1, 2]
        )

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

    def get_screen_info(self) -> Computer_screen:

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

    def populate_tabs(self, variables: Dict[str, Any], widgets: Dict[str, Any]):
        frame = self.nametowidget("main_frame")
        tabs = frame.nametowidget("tabs")

        baseline_correction = Baseline_correction_frame(
            tabs, name="baseline_correction", variables=variables, widgets=widgets
        )
        baseline_correction.grid(column=0, row=0, sticky=("nesw"))

        tabs.add(baseline_correction, text="Baseline correction")

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

    def on_return(self, *event):

        self.focus_set()
