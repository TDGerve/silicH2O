import webbrowser

import pandas as pd

import tkinter as tk
from tkinter import ttk


##### CREATE MENU BAR #####
# Prevent menu from tearting off
root.option_add("*tearOff", False)
menubar = tk.Menu(root)
root["menu"] = menubar
self.menu_file = tk.Menu(menubar)
menu_settings = tk.Menu(menubar)
menu_help = tk.Menu(menubar)
menubar.add_cascade(menu=self.menu_file, label="File")
menubar.add_cascade(menu=menu_settings, label="Settings")
menubar.add_cascade(menu=menu_help, label="Help")
# File menu
self.menu_file.add_command(label="Load spectra", command=self.add_spectra)
self.menu_file.add_command(label="Load directory", command=self.load_directory)
self.menu_file.add_separator()
self.menu_file.add_command(label="Export results", command=self.export_results)
self.menu_file.add_command(
    label="Export sample spectra", command=self.export_sample_spectra
)
self.menu_file.add_command(
    label="Export bulk spectra", command=self.export_bulk_spectra
)
# disable data export on intialisation
for menu_item in [
    "Export results",
    "Export sample spectra",
    "Export bulk spectra",
]:
    self.menu_file.entryconfigure(menu_item, state=tk.DISABLED)
# Settings menu
menu_settings.add_command(
    label="Settings", command=self.settings.open_general_settings
)
menu_settings.add_command(
    label="Baseline settings", command=self.settings.open_bir_settings
)
# Help menu
menu_help.add_command(
    label="Contact", command=lambda: self.contact(parent=root)
)


def load_directory(self):
        """ """
        try:
            dirname = tk.filedialog.askdirectory(initialdir=os.getcwd())
        except AttributeError:
            print("Opening files cancelled by user")
            return
        files = glob.glob(os.path.join(dirname, "*.txt"))
        if not files:
            return
        self.initiate_load_files(files)

def initiate_load_files(self, files):
    """ """
    self.data_bulk = data_processing(files, self.settings)
    self.data_bulk.preprocess()
    self.samplesVar.set(list(self.data_bulk.names))
    for menu_item in [
        "Export results",
        "Export sample spectra",
        "Export bulk spectra",
    ]:
        self.menu_file.entryconfigure(menu_item, state=tk.NORMAL)
    for w in [self.sample_list, self.button_next, self.button_previous]:
        w.configure(state=tk.NORMAL)
    del w
    self.sample_list.selection_set(first=0)
    if not self.current_sample:
        self.current_sample = current_sample(self.data_bulk, 0)
        self.interpolation.initiate_plot()
        self.water_calc.initiate_plot()
        self.subtract.initiate_plot()
    else:
        self.current_sample = current_sample(self.data_bulk, 0)
        self.update_plots()

def add_spectra(self):
    """ """
    try:
        filenames = tk.filedialog.askopenfilenames(initialdir=os.getcwd())
    except AttributeError:
        print("Opening files cancelled by user")
        return

    if not self.data_bulk:
        self.initiate_load_files(filenames)

    else:
        current_selection = self.sample_list.curselection()
        for f in filenames:
            self.data_bulk.add_sample(f)
        self.samplesVar.set(list(self.data_bulk.names))
            self.sample_list.selection_set(current_selection)


def export_results(self):
        dataframe = pd.concat(
            [self.data_bulk.processing, self.data_bulk.results.drop(columns=["name"])],
            axis=1,
        )
        try:
            with tk.filedialog.asksaveasfile(mode="w", defaultextension=".csv") as file:
                dataframe.to_csv(file.name, index=False)
        except AttributeError:
            print("Saving cancelled")

def export_sample_spectra(self):
    """
    Export processed spectra for a single sample
    """

    sample = self.current_sample.sample
    name = self.current_sample.name
    # Raw data
    dataframe = pd.DataFrame({"x": sample.x})
    dataframe["raw"] = sample.signal.raw
    # Grab all processed sectra
    spectra = {
        name: getattr(sample.signal, name)
        for name, check in sample._processing.items()
        if check
    }
    dataframe = pd.concat([dataframe, pd.DataFrame(spectra)], axis=1)
    dataframe["baseline"] = sample.baseline

    try:
        with tk.filedialog.asksaveasfile(
            mode="w", initialfile=name, defaultextension="csv"
        ) as file:
            dataframe.to_csv(file.name, index=False)
    except AttributeError:
        print("Saving cancelled")

def export_bulk_spectra(self):
    """
    Export (processed) spectra for all samples
    """

    try:
        dirname = tk.filedialog.askdirectory(initialdir=os.getcwd())
    except AttributeError:
        print("Exporting files cancelled by user")
        return

    for i, sample in self.data_bulk.samples.items():
        name = self.data_bulk.names[i]
        # Raw data
        dataframe = pd.DataFrame({"x": sample.x})
        dataframe["raw"] = sample.signal.raw
        # Grab all processed sectra
        spectra = {
            name: getattr(sample.signal, name)
            for name, check in sample._processing.items()
            if check
        }
        dataframe = pd.concat([dataframe, pd.DataFrame(spectra)], axis=1)
        dataframe["baseline"] = sample.baseline

        dataframe.to_csv(f"{dirname}/{i:02}_{name}.csv", index=False)

def contact(self, parent):
    def link(event):
        webbrowser.open_new(event.widget.cget("text"))

    popup = tk.Toplevel(parent)
    popup.title("Contact")
    window = ttk.Frame(popup)
    window.grid(column=0, row=0, sticky=("nesw"))
    for i in (0, 2):
        window.columnconfigure(i, weight=1)
        window.rowconfigure(i, weight=1)
    help_string = "For information, questions or assistance, catch me at:"
    github_link = "https://github.com/TDGerve/ramCOH"
    email_string = "thomasvangerve@gmail.com"

    font = (self.font, "14")
    ttk.Label(window, text=help_string, font=font, anchor="center").grid(
        row=0, column=0, sticky=("nesw")
    )
    ttk.Label(window, text=email_string, font=font, anchor="center").grid(
        row=2, column=0, sticky=("nesw")
    )
    github = ttk.Label(
        window,
        text=github_link,
        foreground="blue",
        cursor="hand2",
        font=font,
        anchor="center",
    )
    github.grid(row=1, column=0, sticky=("nesw"))
    github.bind("<Button-1>", link)

    for child in window.winfo_children():
        child.grid_configure(padx=50, pady=10)

    popup.attributes("-topmost", True)