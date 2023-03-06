import tkinter as tk
from tkinter import ttk
from typing import Callable, Dict, List, Tuple

import blinker as bl

from .. import app_configuration

on_sample_change = bl.signal("sample change")
on_samples_removed = bl.signal("samples removed")

on_delete = bl.signal("delete")


class Sample_navigation(ttk.Frame):
    def __init__(
        self, parent: ttk.Frame, variables: Dict, widgets: Dict, *args, **kwargs
    ):

        super().__init__(parent, name="sample_navigation", *args, **kwargs)

        self.variables = {}
        variables["sample_navigation"] = self.variables

        self.widgets = {}
        widgets["sample_navigation"] = self.widgets

        self.make_listbox()
        self.make_scrollbar()
        self.make_buttons()

        self.rowconfigure(0, weight=1)
        for c in [0, 1]:
            self.columnconfigure(c, weight=1)

        on_delete.connect(self.remove_samples)

    def make_listbox(self):
        var = tk.StringVar()

        listbox = tk.Listbox(
            self,
            listvariable=var,
            selectmode=tk.EXTENDED,
            exportselection=False,
            name="sample_list",
            state=tk.DISABLED,
            font=(
                app_configuration.gui["font"]["family"],
                app_configuration.gui["font"]["size"],
            ),
            activestyle=tk.DOTBOX,
        )
        listbox.grid(column=0, row=0, columnspan=2, rowspan=1, sticky=("nesw"))

        self.widgets["samplelist"] = listbox
        self.variables["samplelist"] = var

        # Bind listobx selection to sample selection
        listbox.bind(
            "<<ListboxSelect>>",
            lambda event: self.change_sample(listbox.curselection()),
        )

    def select_sample(self, selection):
        listbox = self.nametowidget("sample_list")

        listbox.selection_set(selection)
        listbox.activate(selection)
        listbox.see(selection)

    def make_scrollbar(self):
        listbox = self.nametowidget("sample_list")
        sample_scroll = ttk.Scrollbar(self, orient=tk.VERTICAL, command=listbox.yview)
        sample_scroll.grid(row=0, column=3, sticky=("ns"))
        listbox["yscrollcommand"] = sample_scroll.set

    def make_button(
        self, name: str, command: Callable, position: List[int], sticky="nws"
    ):
        button = ttk.Button(
            self,
            name=name,
            text=name,
            state=tk.DISABLED,
            command=command,
        )
        button.grid(row=position[0], column=position[1], padx=5, pady=5, sticky=sticky)
        self.widgets[name] = button

    def make_buttons(self):

        self.make_button("previous", self.previous_sample, [1, 0], "nes")
        self.make_button("next", self.next_sample, [1, 1])
        self.make_button("delete", self.remove_samples, [2, 0])

    def next_sample(self):

        listbox = self.nametowidget("sample_list")

        current = listbox.curselection()

        if not current:  # See if selection exists
            return
        current = current[0]  # Grab actucal number
        total = listbox.size()
        new = current + 1

        if current < (total - 1):
            listbox.select_clear(current)
            self.select_sample(new)
            self.change_sample((new,))

    def previous_sample(self):
        listbox = self.nametowidget("sample_list")
        current = listbox.curselection()[0]
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
        index = selection[0]
        # listbox = self.nametowidget("sample_list")
        on_sample_change.send("navigator", index=index)

    def remove_samples(self, *args):

        listbox = self.nametowidget("sample_list")
        selection = listbox.curselection()
        if not selection:
            return
        index = list(selection)

        on_samples_removed.send("navigator", index=index)

        new_selection = max(index[0] - 1, 0)
        self.select_sample(new_selection)
        self.change_sample((new_selection,))
