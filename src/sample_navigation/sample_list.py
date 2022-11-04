import tkinter as tk
from tkinter import ttk

from .. import settings
from ..spectrum_processing.sample_database import samples


class sample_selection(ttk.Frame):
    def __init__(
        self, parent: ttk.Frame, sample_database: samples = None, *args, **kwargs
    ):
        self.samples = sample_database
        super().__init__(parent, *args, **kwargs)

        self.list = tk.StringVar(value=[])
        self.make_listbox()
        self.make_scrollbar()
        self.make_buttons()

        self.rowconfigure(0, weight=1)
        for c in [0, 1]:
            self.columnconfigure(c, weight=1)

    def make_listbox(self):
        listbox = tk.Listbox(
            self,
            listvariable=self.list,
            selectmode=tk.BROWSE,
            name="listbox",
            state=tk.DISABLED,
            font=(
                settings.gui["font"]["family"],
                settings.gui["font"]["size"],
            ),
        )
        listbox.grid(column=0, row=0, columnspan=2, rowspan=1, sticky=("nesw"))

        # Bind listobx selection to sample selection
        listbox.bind(
            "<<ListboxSelect>>",
            lambda event: self.samples.select_sample(listbox.curselection()[0]),
        )

    def update_listbox(self, names):
        # Update listbox widget
        listbox = self.nametowidget("listbox")
        current_selection = listbox.curselection()
        self.list.set(names)
        if current_selection:
            listbox.selection_set(current_selection)
        else:
            listbox.selection_set(0)

        listbox.configure(state=tk.NORMAL)

    def make_scrollbar(self):
        list = self.nametowidget("listbox")
        sample_scroll = ttk.Scrollbar(self, orient=tk.VERTICAL, command=list.yview)
        sample_scroll.grid(row=0, column=3, sticky=("ns"))
        list["yscrollcommand"] = sample_scroll.set

    def make_buttons(self):

        # Buttons to move through samples
        ttk.Button(
            self,
            text="Previous",
            state=tk.DISABLED,
            name="previous",
            command=self.previous_sample,
        ).grid(row=1, column=0, padx=5, pady=5, sticky=("nes"))

        ttk.Button(
            self, text="Next", state=tk.DISABLED, name="next", command=self.next_sample
        ).grid(row=1, column=1, padx=5, pady=5, sticky=("nws"))

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
            listbox.selection_set(new)
            listbox.see(new)
            self.samples.select_sample(listbox.curselection())

    def previous_sample(self):
        listbox = self.nametowidget("listbox")
        current = listbox.curselection()[-1]
        if not current:
            return
        new = current - 1
        if current > 0:
            listbox.select_clear(current)
            listbox.selection_set(new)
            listbox.see(new)
            self.samples.select_sample(listbox.curselection())
