import os, glob
import webbrowser
import pandas as pd
import tkinter as tk
from tkinter import ttk

# Import all app elements
from settings import settings
from data_processing import data_processing
from water_calc import water_calc
from interpolation import interpolation
from subtraction import subtraction
from current_sample import current_sample


# Move all constants and settings outside the code

# Don't store widgets in variables, but give them names and call them from their parent, see:
# https://stackoverflow.com/questions/71902896/tkinter-access-specifc-widgets-created-with-for-loop/71906287#71906287

# Set up draw methods to create the GUI, instead of doing it inside the initialiser

# Separate all GUI code from datamanagement and calculations


class main_window:
    def __init__(self, root, *args, **kwargs):
        """
        Main window
        """

        # Set tkinter theme
        style = ttk.Style()
        root.tk.call("source", f"{os.getcwd()}/theme/breeze.tcl")
        theme = "Breeze"
        style.theme_use(theme)
        style.configure(".", font="helvetica")
        # Grab some theme elements, for passing on to widgets
        self.font = style.lookup(theme, "font")
        self.fontsize = 13
        self.bgClr = style.lookup(theme, "background")
        # calculate background color to something matplotlib understands
        self.bgClr_plt = tuple((c / 2**16 for c in root.winfo_rgb(self.bgClr)))

        root.title("ramCOH by T. D. van Gerve")

        # Set some geometries
        root.minsize(1000, 830)
        root.geometry("1200x1000")
        root.resizable(True, True)
        sizegrip = ttk.Sizegrip(root)
        sizegrip.grid(row=7, sticky=("se"))
        root.rowconfigure(0, weight=1)
        root.columnconfigure(3, weight=1)

        ##### INITIALISE VARIABLES #####
        self.data_bulk = None
        self.current_sample = None

        ##### INITIATE SETTINGS #####
        self.settings = settings(root, self)

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

        ##### CREATE FRAMES #####
        # Create the two main frames
        samples = ttk.Frame(root)
        main_frame = ttk.Frame(root)
        samples.grid(row=0, column=0, columnspan=2, rowspan=8, sticky=("nesw"))
        main_frame.grid(row=0, column=3, rowspan=8, columnspan=6, sticky=("nesw"))
        # Let the first row fill the frame
        samples.rowconfigure(0, weight=1)
        samples.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)

        # Create tabs inside the main frame
        self.tabs = ttk.Notebook(main_frame)
        self.water_calc = water_calc(self.tabs, self)
        self.interpolation = interpolation(self.tabs, self)
        self.subtract = subtraction(self.tabs, self)
        # Put the frames on the grid
        self.tabs.grid(column=0, row=0, sticky=("nesw"))
        self.water_calc.grid(column=0, row=0, sticky=("nesw"))
        self.interpolation.grid(column=0, row=0, sticky=("nesw"))
        self.subtract.grid(column=0, row=0, sticky=("nesw"))
        # Label the notebook tabs
        self.tabs.add(self.water_calc, text="Baseline correction")
        self.tabs.add(self.interpolation, text="Interpolation")
        self.tabs.add(self.subtract, text="Host correction")
        # Adjust resizability
        self.tabs.rowconfigure(0, weight=1)
        self.tabs.columnconfigure(0, weight=1)
        # trigger function on tab change
        self.tabs.bind("<<NotebookTabChanged>>", self.on_tab_change)

        ##### POPULATE SAMPLES FRAME #####
        # List with all samples
        self.samplesVar = tk.StringVar(value=[])
        self.sample_list = tk.Listbox(
            samples,
            listvariable=self.samplesVar,
            selectmode=tk.BROWSE,
            font=(self.font, self.fontsize),
            state=tk.DISABLED,
        )
        self.sample_list.grid(column=0, row=0, columnspan=2, rowspan=6, sticky=("nesw"))
        # Scroll bar for the samples list
        sample_scroll = ttk.Scrollbar(
            samples, orient=tk.VERTICAL, command=self.sample_list.yview
        )
        sample_scroll.grid(row=0, column=2, sticky=("ns"))
        self.sample_list["yscrollcommand"] = sample_scroll.set
        # Buttons to move through samples
        self.button_next = ttk.Button(
            samples, text="Previous", state=tk.DISABLED, command=self.previous_sample
        )
        self.button_next.grid(row=6, column=0, padx=5, pady=5)
        self.button_previous = ttk.Button(
            samples, text="Next", state=tk.DISABLED, command=self.next_sample
        )
        self.button_previous.grid(row=6, column=1, padx=5, pady=5)
        # Bind listobx selection to sample selection
        self.sample_list.bind(
            "<<ListboxSelect>>",
            lambda event: self.select_sample(self.sample_list.curselection()),
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

    def update_plots(self):

        update = {
            "Baseline correction": self.water_calc.update_plot,
            "Interpolation": self.interpolation.update_plot,
            "Host correction": self.subtract.update_plot,
        }
        current_tab = self.tabs.tab(self.tabs.select(), "text")
        update[current_tab]()

    def on_tab_change(self, event):
        """
        Refresh plot on the opened tab
        """
        tab = event.widget.tab("current")["text"]

        update = {
            "Baseline correction": self.water_calc.update_plot,
            "Interpolation": self.interpolation.update_plot,
            "Host correction": self.subtract.update_plot,
        }

        if self.current_sample:
            # selected_sample = self.current_sample.index
            update[tab]()

    def select_sample(self, index):
        """ """
        if index:
            selection = index[-1]
            self.current_sample = current_sample(self.data_bulk, selection)
            self.update_plots()

    def next_sample(self):
        current = self.sample_list.curselection()
        if not current:  # See if selection exists
            return
        current = current[-1]  # Grab actucal number
        total = self.sample_list.size()
        new = current + 1
        if current < (total - 1):
            self.sample_list.select_clear(current)
            self.sample_list.selection_set(new)
            self.sample_list.see(new)
            self.select_sample(self.sample_list.curselection())

    def previous_sample(self):
        current = self.sample_list.curselection()[-1]
        if not current:
            return
        new = current - 1
        if current > 0:
            self.sample_list.select_clear(current)
            self.sample_list.selection_set(new)
            self.sample_list.see(new)
            self.select_sample(self.sample_list.curselection())

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


def main():

    root = tk.Tk()
    main_window(root)

    root.mainloop()


if __name__ == "__main__":
    main()
