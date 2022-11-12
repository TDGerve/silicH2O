import tkinter as tk
from tkinter import ttk

import blinker as bl
from typing import List


from .. import settings


on_sample_change = bl.signal("sample change")
on_samples_removed = bl.signal("samples removed")


class Sample_navigation(ttk.Frame):
    def __init__(
        self, parent: ttk.Frame, gui_variables: dict, widget_list: List, *args, **kwargs
    ):

        super().__init__(parent, name="sample_navigation", *args, **kwargs)

        self.sample_list = tk.StringVar([])
        gui_variables["sample_list"] = self.sample_list

        self.widgets = []
        widget_list["sample_navigation"] = self.widgets

        self.make_listbox()
        self.make_scrollbar()
        self.make_buttons()

        self.rowconfigure(0, weight=1)
        for c in [0, 1]:
            self.columnconfigure(c, weight=1)

    def make_listbox(self):
        listbox = tk.Listbox(
            self,
            listvariable=self.sample_list,
            selectmode=tk.BROWSE,
            name="listbox",
            state=tk.DISABLED,
            font=(
                settings.gui["font"]["family"],
                settings.gui["font"]["size"],
            ),
        )
        listbox.grid(column=0, row=0, columnspan=2, rowspan=1, sticky=("nesw"))
        self.widgets.append(listbox)

        # Bind listobx selection to sample selection
        listbox.bind(
            "<<ListboxSelect>>",
            lambda event: self.change_sample(listbox.curselection()[-1]),
        )

    # def update(self, names):
    #     # Update listbox widget

    #     listbox = self.nametowidget("listbox")

    #     if listbox["state"] == "disabled":
    #         listbox.configure(state=tk.NORMAL)

    #         for button in ["previous", "next"]:
    #             button = self.nametowidget(button)
    #             button.configure(state=tk.NORMAL)

    #     current_selection = listbox.curselection()

    #     self.sample_list.set(names)
    #     self.select_sample(current_selection)

    def select_sample(self, selection):
        listbox = self.nametowidget("listbox")

        listbox.selection_set(selection)
        listbox.see(selection)

    def make_scrollbar(self):
        listbox = self.nametowidget("listbox")
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
        listbox = self.nametowidget("listbox")

        current = listbox.curselection()
        if not current:  # See if selection exists
            return
        current = current[-1]  # Grab actucal number
        total = listbox.size()
        new = current + 1
        if current < (total - 1):
            listbox.select_clear(current)
            self.select_sample(new)
            self.change_sample(new)

    def previous_sample(self):
        listbox = self.nametowidget("listbox")
        current = listbox.curselection()[-1]
        if not current:
            return
        new = current - 1
        if current > 0:
            listbox.select_clear(current)
            self.select_sample(new)
            self.change_sample(new)

    def change_sample(self, index: int):
        # listbox = self.nametowidget("listbox")
        on_sample_change.send("sample selected", index=index)
