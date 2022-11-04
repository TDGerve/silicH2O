import tkinter as tk
from tkinter import filedialog

import os

from ..spectrum_processing.sample_database import samples
from ..sample_navigation import sample_selection


class io_handler:
    def __init__(self, sample_database: samples, sample_selector: sample_selection):

        self.sample_selector = sample_selector
        self.samples = sample_database

    def load_spectra(self):
        """ """
        # Read file names from dialog
        # try:

        filenames = filedialog.askopenfilenames(initialdir=os.getcwd())
        # except AttributeError:

        #     print("Opening files cancelled by user")
        #     return
        # Store filenames in database
        self.samples.add_files(filenames)
        names = self.samples.names
        self.sample_selector.update_listbox(names)

    def load_directory(self):
        pass

    def export_results(self):
        pass

    def export_sample(self):
        pass

    def export_all_samples(self):
        pass


# def load_directory(self):
#         """ """
#         try:
#             dirname = tk.filedialog.askdirectory(initialdir=os.getcwd())
#         except AttributeError:
#             print("Opening files cancelled by user")
#             return
#         files = glob.glob(os.path.join(dirname, "*.txt"))
#         if not files:
#             return
#         self.initiate_load_files(files)

# def initiate_load_files(self, files):
#     """ """
#     self.data_bulk = data_processing(files, self.settings)
#     self.data_bulk.preprocess()
#     self.samplesVar.set(list(self.data_bulk.names))
#     for menu_item in [
#         "Export results",
#         "Export sample spectra",
#         "Export bulk spectra",
#     ]:
#         self.menu_file.entryconfigure(menu_item, state=tk.NORMAL)
#     for w in [self.sample_list, self.button_next, self.button_previous]:
#         w.configure(state=tk.NORMAL)
#     del w
#     self.sample_list.selection_set(first=0)
#     if not self.current_sample:
#         self.current_sample = current_sample(self.data_bulk, 0)
#         self.interpolation.initiate_plot()
#         self.water_calc.initiate_plot()
#         self.subtract.initiate_plot()
#     else:
#         self.current_sample = current_sample(self.data_bulk, 0)
#         self.update_plots()

# def add_spectra(self):
#     """ """
#     try:
#         filenames = tk.filedialog.askopenfilenames(initialdir=os.getcwd())
#     except AttributeError:
#         print("Opening files cancelled by user")
#         return

#     if not self.data_bulk:
#         self.initiate_load_files(filenames)

#     else:
#         current_selection = self.sample_list.curselection()
#         for f in filenames:
#             self.data_bulk.add_sample(f)
#         self.samplesVar.set(list(self.data_bulk.names))
#             self.sample_list.selection_set(current_selection)


# def export_results(self):
#         dataframe = pd.concat(
#             [self.data_bulk.processing, self.data_bulk.results.drop(columns=["name"])],
#             axis=1,
#         )
#         try:
#             with tk.filedialog.asksaveasfile(mode="w", defaultextension=".csv") as file:
#                 dataframe.to_csv(file.name, index=False)
#         except AttributeError:
#             print("Saving cancelled")

# def export_sample_spectra(self):
#     """
#     Export processed spectra for a single sample
#     """

#     sample = self.current_sample.sample
#     name = self.current_sample.name
#     # Raw data
#     dataframe = pd.DataFrame({"x": sample.x})
#     dataframe["raw"] = sample.signal.raw
#     # Grab all processed sectra
#     spectra = {
#         name: getattr(sample.signal, name)
#         for name, check in sample._processing.items()
#         if check
#     }
#     dataframe = pd.concat([dataframe, pd.DataFrame(spectra)], axis=1)
#     dataframe["baseline"] = sample.baseline

#     try:
#         with tk.filedialog.asksaveasfile(
#             mode="w", initialfile=name, defaultextension="csv"
#         ) as file:
#             dataframe.to_csv(file.name, index=False)
#     except AttributeError:
#         print("Saving cancelled")

# def export_bulk_spectra(self):
#     """
#     Export (processed) spectra for all samples
#     """

#     try:
#         dirname = tk.filedialog.askdirectory(initialdir=os.getcwd())
#     except AttributeError:
#         print("Exporting files cancelled by user")
#         return

#     for i, sample in self.data_bulk.samples.items():
#         name = self.data_bulk.names[i]
#         # Raw data
#         dataframe = pd.DataFrame({"x": sample.x})
#         dataframe["raw"] = sample.signal.raw
#         # Grab all processed sectra
#         spectra = {
#             name: getattr(sample.signal, name)
#             for name, check in sample._processing.items()
#             if check
#         }
#         dataframe = pd.concat([dataframe, pd.DataFrame(spectra)], axis=1)
#         dataframe["baseline"] = sample.baseline

#         dataframe.to_csv(f"{dirname}/{i:02}_{name}.csv", index=False)
