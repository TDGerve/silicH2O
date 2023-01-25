import tkinter as tk
from functools import partial
from tkinter import ttk
from typing import Dict

from .... import app_configuration
from .scrollframes import ScrollFrame

_font = app_configuration.gui["font"]["family"]
_fontsize = app_configuration.gui["font"]["size"]
_fontsize_head = _fontsize


class Baseline_interpolation_frame(ttk.Frame):
    def __init__(
        self,
        parent: tk.Frame,
        widgets: Dict,
        variables: Dict,
        row: int,
        col: int,
        width,
    ):

        self.widgets = widgets
        self.variables = variables

        super().__init__(parent, name="baseline")
        self.grid(row=row, column=col, sticky=("nesw"))
        # frame.grid_propagate(0)

        tk.Label(self, text="Baseline", font=(_font, _fontsize_head, "bold")).grid(
            row=0, column=0, columnspan=2, sticky=("nsw")
        )

        tk.Label(
            self,
            text="Interpolation regions",
            font=(_font, _fontsize_head),
        ).grid(row=1, column=0, columnspan=2, sticky=("nsw"))

        self.make_bir_scrollframe(self, width=width)
        self.make_smoothing_widgets(self, rowstart=9)

        for i in range(2):
            self.columnconfigure(i, weight=1)

    def make_bir_scrollframe(self, parent, width):
        background_color = app_configuration.background_color

        scrollframe = ScrollFrame(
            parent,
            name="bir_scrollframe",
            width=width,
            background_color=background_color,
        )
        scrollframe.grid(row=3, column=0, columnspan=2, sticky="nesw")
        for k, name in zip(range(3), ["No.", "From", "to"]):
            tk.Label(
                scrollframe.headers, text=name, font=(_font, _fontsize, "italic")
            ).grid(row=0, column=k, sticky=("nsw"))
        self.make_bir_widgets(scrollframe.inner_frame, bir_amount=5)

    def make_bir_widgets(self, parent, bir_amount: int):

        for widget in parent.winfo_children():
            widget.destroy()

        for i in range(bir_amount):
            label = ttk.Label(
                parent,
                text=f"{i + 1: <4} ",
                font=(_font, _fontsize),
            )
            label.grid(row=i, column=0, sticky=("nsw"))

            for j in range(2):
                name = f"bir_{i * 2 + j}"
                var = tk.StringVar(name=name)

                entry = ttk.Entry(
                    parent,
                    validate="focusout",
                    validatecommand=(
                        self.register(
                            partial(self.validate_bir_input, index=i * 2 + j)
                        ),
                        r"%P %s %W",
                    ),
                    invalidcommand=(
                        self.register(partial(self.invalid_bir_input, index=i * 2 + j)),
                        r"%s %P",
                    ),
                    width=4,
                    background="white",
                    font=(_font, _fontsize),
                    state=tk.DISABLED,
                    name=name,
                )
                entry.grid(row=i, column=j + 1, sticky=("nesw"))

                self.baseline_widgets[name] = entry
                self.baseline_variables[name] = var

        for i in (1, 2):
            parent.columnconfigure(i, weight=1)

        self.make_delete_add_buttons(parent, start_column=3)

    def make_delete_add_buttons(self, parent, start_column: int, width=2):

        rows = parent.grid_size()[1]
        for i in range(rows - 1):
            button = ttk.Button(
                parent,
                text="\uff0b",
                state=tk.DISABLED,
                name=f"add_bir_{i}",
                style="clean.TButton",
                width=width,
                # command=func,
            )
            button.grid(row=i, column=start_column)

        for i in range(rows - 2):
            button = ttk.Button(
                parent,
                text="\uff0d",
                state=tk.DISABLED,
                name=f"delete_bir_{i + 1}",
                style="clean.TButton",
                width=width,
                # command=func,
            )
            button.grid(row=i + 1, column=start_column + 1)

    def make_smoothing_widgets(self, parent, rowstart):

        name = "smoothing"

        ttk.Label(parent).grid(row=rowstart, column=0)  # empty row

        ttk.Label(
            parent,
            text="smoothing",
            font=(_font, _fontsize_head),
        ).grid(row=rowstart + 1, column=0, sticky=("nsw"))

        var = tk.StringVar(name=name)
        entry = ttk.Spinbox(
            parent,
            from_=0.1,
            to=100,
            increment=0.1,
            # textvariable=var,
            validate="focusout",
            validatecommand=(
                self.register(self.validate_smoothing),
                "%P",
            ),
            invalidcommand=(
                self.register(self.invalid_smoothing),
                r"%s",
            ),
            width=5,
            background="white",
            font=(_font, _fontsize),
            state=tk.DISABLED,
            name=name,
        )
        entry.grid(row=rowstart + 1, column=1, sticky=("nesw"))

        self.baseline_widgets[name] = entry
        self.baseline_variables[name] = var
