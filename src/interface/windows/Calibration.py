import tkinter as tk
from functools import partial
from tkinter import ttk
from typing import Any, Dict

import blinker as bl
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from ... import app_configuration
from ..frames.scrollframes import ScrollFrame
from ..widgets.validate_input import validate_numerical_input

_font = app_configuration.gui["font"]["family"]
_fontsize = app_configuration.gui["font"]["size"]
_fontsize_head = _fontsize + 2

on_set_H2Oreference = bl.signal("set H2O reference")
on_set_calibration_std = bl.signal("set calibration std")

on_import_calibration_project = bl.signal("project calibration")
on_import_calibration_file = bl.signal("file calibration")
on_get_calibration_info = bl.signal("get calibration info")


class Calibration_window(tk.Toplevel):
    def __init__(
        self,
        parent,
        title: str,
        name: str,
        widgets: Dict[str, Any],
        variables: Dict[str, Any],
    ):

        super().__init__(master=parent, name=name)
        self.title(title)

        self.widgets = {}
        self.variables = {}

        self.statistics_variables = {}

        widgets["calibration"] = self.widgets
        variables["calibration"] = self.variables
        variables["calibration_statistics"] = self.statistics_variables

        self.rowconfigure(1, weight=1)
        self.columnconfigure(1, weight=1)

        self.plot_frame = ttk.Frame(self, name="plot")
        self.plot_frame.grid(row=0, column=1, sticky="new")

        # self.scrollframe = None
        self.make_sample_scrollframe(parent=self, row=0, col=0, rowspan=2)
        self.make_results_frame(parent=self, row=0, col=2)

        for child in self.winfo_children():
            child.grid_configure(padx=10, pady=10)

        self.make_menu()
        # self.bind(

        self.set_keybindings()
        # always on top
        self.attributes("-topmost", True)
        # not resizeable
        self.resizable(0, 0)
        # ask for calibration data
        parent.after_idle(on_get_calibration_info.send)

    def set_keybindings(self):
        self.bind(
            "<Return>",
            lambda event: self.focus(),
        )
        self.bind("<Control-s>", lambda event: print("save calibration"))  # CH

    def make_menu(self):

        menubar = tk.Menu(self, name="menus")
        self["menu"] = menubar
        self.option_add("*tearOff", False)

        menu = tk.Menu()
        menubar.add_cascade(menu=menu, label="Import")

        menu.add_command(
            label="current project", command=on_import_calibration_project.send
        )
        menu.add_command(label="from file", command=on_import_calibration_file.send)

    def make_results_frame(self, parent, row, col):

        frame = ttk.Frame(self, name="results")
        frame.grid(row=row, column=col, sticky="nesw")

        ttk.Separator(frame, orient=tk.HORIZONTAL).grid(row=0, column=0, sticky=("new"))
        self.make_statistics_frame(
            parent=frame, row=1, col=0, variables=self.statistics_variables
        )
        ttk.Separator(frame, orient=tk.HORIZONTAL).grid(row=2, column=0, sticky=("new"))
        self.make_io_frame(parent=frame, row=3, col=0)

        frame.rowconfigure(3, weight=1)

        for child in frame.winfo_children():
            child.grid_configure(pady=5)

    def make_sample_scrollframe(self, parent, row: int, col: int, rowspan: int):
        background_color = app_configuration.background_color

        self.scrollframe = ScrollFrame(
            parent,
            name="sample_scrollframe",
            background_color=background_color,
            width="12c",
        )
        self.scrollframe.grid(row=row, column=col, rowspan=rowspan, sticky="nesw")

        header_labels = [
            "Sample  ",
            "H\u2082O:silicate  ",
            "H\u2082O (wt.%)  ",
            "use  ",
        ]

        for k, name in enumerate(header_labels):
            tk.Label(
                self.scrollframe.headers,
                text=name,
                font=(_font, _fontsize_head, "bold"),
            ).grid(row=0, column=k, sticky=("nsw"))

        self.make_sample_widgets(sample_amount=20, state=tk.DISABLED)

    def make_io_frame(self, parent: tk.Frame, row: int, col: int):
        frame = ttk.Frame(parent)
        frame.grid(row=row, column=col, sticky="new")

        names = ["save", "save as ...", "use"]
        commands = [  # CH
            lambda: print("do something"),
            lambda: print("do something"),
            lambda: print("do something"),
        ]

        for i, (name, command) in enumerate(zip(names, commands)):
            button = ttk.Button(frame, text=name, command=command)
            button.grid(row=i, column=0, sticky="new")

        for child in frame.winfo_children():
            child.grid_configure(padx=10, pady=5)

    def make_statistics_frame(self, parent: tk.Frame, row: int, col: int, variables):

        frame = ttk.Frame(parent)
        frame.grid(row=row, column=col, sticky="new")

        var_names = ["R2", "RMSE", "p_value", "intercept", "slope"]
        var_labels = ["R\u00B2", "RMSE", "p-value", "intercept", "slope"]

        for i, (name, label) in enumerate(zip(var_names, var_labels)):
            var = tk.StringVar()

            label = ttk.Label(
                frame, anchor="w", text=label, font=(_font, _fontsize_head, "italic")
            )
            value = ttk.Label(
                frame, anchor="w", textvariable=var, font=(_font, _fontsize_head)
            )

            label.grid(row=i, column=0, sticky="new")
            value.grid(row=i, column=1, sticky="new")

            variables[name] = var

        frame.columnconfigure(1, minsize="5c")

        for child in frame.winfo_children():
            child.grid_configure(padx=10, pady=10)

    def draw_plot(self, plot):

        # plot_frame = ttk.Frame(self, name="plot")
        # plot_frame.grid(row=0, column=1, sticky="nesw")
        # plot_frame.grid_configure(padx=10, pady=10)

        fig = plot.fig
        self.canvas = FigureCanvasTkAgg(fig, self.plot_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky=("nesw"))

    def make_sample_widgets(self, sample_amount, state=tk.NORMAL):

        self.variables.clear()
        self.widgets.clear()

        parent = self.scrollframe.inner_frame

        for widget in parent.winfo_children():
            widget.destroy()

        for i in range(sample_amount):

            label_var = tk.StringVar(value=f"{'':<17}")
            H2OSi_var = tk.StringVar()
            h2o_var = tk.StringVar()
            use_var = tk.BooleanVar()

            label = ttk.Label(
                parent,
                textvariable=label_var,
                font=(_font, _fontsize),
                width=17,
            )
            h2oSi = ttk.Label(
                parent,
                textvariable=H2OSi_var,
                font=(_font, _fontsize),
                width=8,
            )
            h2o = ttk.Entry(
                parent,
                validate="focusout",
                validatecommand=(
                    parent.register(
                        partial(
                            self.validate_h2o,
                            index=i,
                        )
                    ),
                    r"%P %s %W",
                ),
                invalidcommand=(
                    parent.register(partial(self.invalid_h2o, index=i)),
                    r"%s %P",
                ),
                width=4,
                background="white",
                font=(_font, _fontsize),
                state=state,
            )

            use = ttk.Checkbutton(
                parent,
                text="",
                variable=use_var,
                onvalue=True,
                offvalue=False,
                command=partial(on_set_calibration_std.send, sample_index=i),
            )

            label.grid(row=i, column=0, sticky="nsw")
            h2oSi.grid(row=i, column=1, sticky="nesw")
            h2o.grid(row=i, column=2, sticky="nesw")
            use.grid(row=i, column=3, sticky="nesw")

            self.variables[f"samplename_{i:02d}"] = label_var
            self.variables[f"h2oSi_{i:02d}"] = H2OSi_var

            self.widgets[f"h2o_{i:02d}"] = h2o
            self.variables[f"h2o_{i:02d}"] = h2o_var

            self.variables[f"use_{i:02d}"] = use_var

            for i in range(4):
                parent.columnconfigure(i, weight=1)

    def validate_h2o(self, values: str, index: int):
        new_value = values[: values.index(" ")]
        widget = self.widgets[f"h2o_{index:02d}"]
        variable = self.variables[f"h2o_{index:02d}"]

        valid, new_value = validate_numerical_input(
            value=new_value,
            accepted_range=[0, np.inf],
            widget=widget,
            variable=variable,
            dtype=float,
        )

        if valid:
            on_set_H2Oreference.send(sample_index=index, H2O=new_value)

        return valid

    def invalid_h2o(self, values: str, index: int):

        variable = self.variables[f"h2o_{index:02d}"]
        old_value = variable.get()

        widget = self.widgets[f"h2o_{index:02d}"]
        widget.delete(0, tk.END)
        widget.insert(0, float(old_value))
