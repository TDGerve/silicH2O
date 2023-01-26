import pathlib
import tkinter as tk
from tkinter import ttk
from typing import Any, Dict

import blinker as bl

from .. import app_configuration
from .infobar import Infobar
from .menus import io_menu
from .sample_navigation import Sample_navigation
from .screens import Computer_screen
from .tabs import Baseline_correction_frame, Interpolation_frame, Subtraction_frame

_main_folder = pathlib.Path(__file__).parents[1]
_theme_file = _main_folder / "theme/breeze.tcl"

_font = app_configuration.gui["font"]["family"]
_fontsize = app_configuration.gui["font"]["size"]

on_Ctrl_c = bl.signal("copy birs")
on_Ctrl_v = bl.signal("paste birs")
on_Ctrl_s = bl.signal("ctrl+s")
on_Ctrl_z = bl.signal("ctrl+z")
on_delete = bl.signal("delete")
on_switch_tab = bl.signal("switch tab")

on_display_message = bl.signal("display message")


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
        self.create_infobar(self, 1, 1, variables, widgets)

        self.populate_tabs(variables, widgets)

        self.create_menus()

        self.set_keybindings()

    def set_keybindings(self):
        # # Give focus to the main window when pressing return
        self.bind(
            "<Return>",
            lambda event: self.focus(),
        )
        self.bind("<Up>", lambda event: self.sample_navigation.previous_sample())
        self.bind("<Down>", lambda event: self.sample_navigation.next_sample())
        self.bind("<Control-c>", lambda event: on_Ctrl_c.send())
        self.bind("<Control-v>", lambda event: on_Ctrl_v.send())
        self.bind("<Control-s>", lambda event: on_Ctrl_s.send())
        self.bind("<Control-z>", lambda event: on_Ctrl_z.send())
        self.bind("<Delete>", lambda event: on_delete.send())

    def set_theme(self):
        self.style = ttk.Style()
        self.tk.call("source", _theme_file)
        self.style.theme_use(app_configuration.gui["theme"])
        self.style.configure(".", _font)

        self.style.configure("TNotebook.Tab", font=(_font, _fontsize), padding=[1, 2])

        self.style.configure(
            "clean.TButton",
            borderwidth=5,
            highlightthickness=0,
            relief=tk.FLAT,
            font=(_font, _fontsize + 2, "bold"),
            padding=-2,
        )

        self.background_color = self.style.lookup(
            app_configuration.gui["theme"], "background"
        )
        app_configuration.background_color = self.background_color

        self.background_color = self.winfo_rgb(self.background_color)

    def set_geometry(self):

        width, height = self.screen.resolution

        self.minsize(*app_configuration.gui["geometry"]["size_min"])
        resolution_str = (
            f"{int(width * 0.85)}x{int(height * 0.85)}+{int(width * 0.15 * 0.5)}+0"
        )

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
        self.sample_navigation = Sample_navigation(self, variables, widgets)
        self.sample_navigation.grid(
            row=0, column=0, rowspan=2, columnspan=1, sticky=("nesw")
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
        self.tabs.bind("<<NotebookTabChanged>>", self.on_tab_change)

    def populate_tabs(self, variables: Dict[str, Any], widgets: Dict[str, Any]):
        frame = self.nametowidget("main_frame")
        tabs = frame.nametowidget("tabs")

        baseline_correction = Baseline_correction_frame(
            tabs, name="baseline", variables=variables, widgets=widgets
        )

        subtraction = Subtraction_frame(
            tabs, name="interference", variables=variables, widgets=widgets
        )
        interpolation = Interpolation_frame(
            tabs, name="interpolation", variables=variables, widgets=widgets
        )

        frames = (baseline_correction, interpolation, subtraction)
        names = (
            "baseline\ncorrection",
            "interpolation\n ",
            "interference\nsubtraction",
        )

        for frame, name in zip(frames, names):
            frame.grid(column=0, row=0, sticky=("nesw"))
            tabs.add(frame, text=name)

        app_configuration.gui["current_tab"] = "baseline"

    def reset_baseline_widgets(self, bir_amount):

        target = app_configuration.gui["current_tab"]

        frames = ("tabs", target)
        widget = self.nametowidget("main_frame")
        for frame in frames:
            widget = widget.nametowidget(frame)

        widget.reset_baseline_widgets(bir_amount)

    def on_tab_change(self, event):
        """
        Refresh plot on the opened tab
        """

        tab = event.widget.tab("current")["text"]
        tab = tab[: tab.index("\n")]
        app_configuration.gui["current_tab"] = tab

        on_switch_tab.send()

        # update = {
        #     "Baseline correction": self.water_calc.update_plot,
        #     "Interpolation": self.interpolation.update_plot,
        #     "Host correction": self.subtract.update_plot,
        # }

        # if self.current_sample:
        #     # selected_sample = self.current_sample.index
        #     update[tab]()

    def create_infobar(self, frame, row, col, variables, widgets):
        # main_frame = self.nametowidget("main_frame")
        infobar = Infobar(frame, variables, widgets)
        infobar.grid(column=col, row=row, sticky=("nesw"))

    def on_return(self, *event):

        self.focus_set()
