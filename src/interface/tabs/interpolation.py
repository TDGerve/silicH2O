from tkinter import ttk

import blinker as bl
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from ... import app_settings
from ..scrollframes import ScrollFrame
from ..validate_input import validate_numerical_input
from ..vertical_toolbar import vertical_toolbar

on_settings_change = bl.signal("settings change")

_font = app_settings.gui["font"]["family"]
_fontsize = app_settings.gui["font"]["size"]
_fontsize_head = _fontsize

padding = 2


class Interpolation_frame(ttk.Frame):
    def __init__(self, parent: ttk.Frame, name: str, variables, widgets, **kwargs):

        self.canvas = None

        self.baseline_widgets = {}
        # self.baseline_smoothing_widgets = {}
        self.save_widgets = {}

        self.baseline_variables = {}
        # self.baseline_smoothing_variables = {}
        self.areas_variables = {}
        self.signal_variables = {}

        variables["baseline"] = self.baseline_variables
        variables["areas"] = self.areas_variables
        variables["signal"] = self.signal_variables
        # variables["baseline_smoothing"] = self.baseline_smoothing_variables

        widgets["baseline"] = self.baseline_widgets
        # widgets["baseline_smoothing"] = self.baseline_smoothing_widgets
        widgets["baseline_save"] = self.save_widgets

    def draw_plot(self, plot):
        fig = plot.fig
        rows = self.grid_size()[1]
        self.canvas = FigureCanvasTkAgg(fig, self)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=0, column=0, rowspan=rows, sticky=("nesw"))

        # Plot navigation toolbar
        toolbar = vertical_toolbar(self.canvas, self)
        # Don't pack 'configure subplots' and 'save figure'
        toolbar.children["!button4"].pack_forget()
        # toolbar.children["!button5"].pack_forget()
        toolbar.update()
        toolbar.grid(row=0, column=1, sticky="nw")
