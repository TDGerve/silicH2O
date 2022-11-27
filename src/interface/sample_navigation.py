import tkinter as tk
from tkinter import ttk

import blinker as bl
from typing import Tuple, Dict

from .. import app_settings

on_sample_change = bl.signal("sample change")
on_samples_removed = bl.signal("samples removed")


class Sample_navigation(ttk.Frame):
    def __init__(
        self, parent: ttk.Frame, variables: Dict, widgets: Dict, *args, **kwargs
    ):

        super().__init__(parent, name="sample_navigation", *args, **kwargs)

        self.variables = []
        variables["sample_navigation"] = self.variables

        self.widgets = []
        widgets["sample_navigation"] = self.widgets

        self.make_listbox()
        self.make_scrollbar()
        self.make_buttons()

        self.rowconfigure(0, weight=1)
        for c in [0, 1]:
            self.columnconfigure(c, weight=1)

    def make_listbox(self):
        var = tk.StringVar()
        self.variables.append(var)
        listbox = tk.Listbox(
            self,
            listvariable=var,
            selectmode=tk.BROWSE,
            exportselection=False,
            name="sample_list",
            state=tk.DISABLED,
            font=(
                app_settings.gui["font"]["family"],
                app_settings.gui["font"]["size"],
            ),
        )
        listbox.grid(column=0, row=0, columnspan=2, rowspan=1, sticky=("nesw"))
        self.widgets.append(listbox)

        # Bind listobx selection to sample selection
        listbox.bind(
            "<<ListboxSelect>>",
            lambda event: self.change_sample(listbox.curselection()),
        )

    def select_sample(self, selection):
        listbox = self.nametowidget("sample_list")

        listbox.selection_set(selection)
        listbox.see(selection)

    def make_scrollbar(self):
        listbox = self.nametowidget("sample_list")
        sample_scroll = ttk.Scrollbar(self, orient=tk.VERTICAL, command=listbox.yview)
        sample_scroll.grid(row=0, column=3, sticky=("ns"))
        listbox["yscrollcommand"] = sample_scroll.set

    def make_buttons(self):

        # Buttons to move through samples
        button_previous = ttk.Button(
            self,
            text="Previous",
            state=tk.DISABLED,
            name="previous",
            command=self.previous_sample,
        )
        button_previous.grid(row=1, column=0, padx=5, pady=5, sticky=("nes"))

        button_next = ttk.Button(
            self, text="Next", state=tk.DISABLED, name="next", command=self.next_sample
        )
        button_next.grid(row=1, column=1, padx=5, pady=5, sticky=("nws"))

        self.widgets += [button_previous, button_next]

    def next_sample(self):
        listbox = self.nametowidget("sample_list")

        current = listbox.curselection()
        if not current:  # See if selection exists
            return
        current = current[-1]  # Grab actucal number
        total = listbox.size()
        new = current + 1
        if current < (total - 1):
            listbox.select_clear(current)
            self.select_sample(new)
            self.change_sample((new,))

    def previous_sample(self):
        listbox = self.nametowidget("sample_list")
        current = listbox.curselection()[-1]
        if not current:
            return
        new = current - 1
        if current > 0:
            listbox.select_clear(current)
            self.select_sample(new)
            self.change_sample((new,))

    def change_sample(self, selection: Tuple[int]):
        if not selection:
            return
        index = selection[-1]
        # listbox = self.nametowidget("sample_list")
        on_sample_change.send("navigator", index=index)
