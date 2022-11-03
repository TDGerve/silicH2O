from tkinter import ttk
import tkinter as tk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os

from toolbar_vertical import vertical_toolbar


class subtraction(ttk.Frame):

    # plot x limits
    xmin = 250
    xmax = 1400
    selection_colors = ["grey", "darkgreen"]

    # Initiate variables
    olivine = None
    raw_spectrum = None
    spectrum_corrected = None
    correction_region = None
    # Object to store lines to be dragged
    _dragging_line = None
    # Store the id of the baseline interpolation region being dragged, 0 for left, 1 for right
    _dragging_line_id = None

    def __init__(self, parent, app):
        super().__init__(parent)

        self.app = app
        self.sample_info = None

        font = app.font
        fontsize = app.fontsize
        self.colors = plt.rcParams["axes.prop_cycle"].by_key()["color"]

        # Create frames
        plot_frame = ttk.Frame(self)
        toolbar_frame = ttk.Frame(self)
        settings_frame = ttk.Frame(self)
        # Put frames on a grid
        plot_frame.grid(row=0, column=0, sticky=("nesw"))
        toolbar_frame.grid(row=0, column=1, sticky=("nesw"))
        settings_frame.grid(row=1, column=0, columnspan=2, sticky=("nesw"))
        # Configure resizing
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)
        plot_frame.columnconfigure(0, weight=1)
        plot_frame.rowconfigure(0, weight=1)
        settings_frame.rowconfigure(2, weight=1)
        settings_frame.columnconfigure(3, weight=1)

        # Create plot canvas
        self.fig, self.ax = plt.subplots(
            figsize=(5.8, 4.5), constrained_layout=True, dpi=80
        )
        self.canvas = FigureCanvasTkAgg(self.fig, plot_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky=("nesw"))
        # Plot navigation toolbar
        toolbar = vertical_toolbar(self.canvas, toolbar_frame)
        # Don't pack 'configure subplots' and 'save figure'
        toolbar.children["!button4"].pack_forget()
        toolbar.children["!button5"].pack_forget()
        toolbar.update()
        toolbar.grid(row=0, column=0, sticky="ne")
        self.fig.canvas.draw()
        # Plot axes
        self.ax.set_xlabel(" ")
        self.ax.set_ylabel("Intensity (arbitr. units)")
        self.ax.set_yticks([])
        self.ax.set_xlim(self.xmin, self.xmax)
        self.fig.patch.set_facecolor(app.bgClr_plt)

    def initiate_plot(self):
        """ """
        # Enable all widgets
        for widget in []:
            widget.configure(state=tk.NORMAL)

        self.sample_info = self.app.current_sample
        sample = self.sample_info.sample
        self.old_spectrum = sample._spectrumSelect

        if hasattr(self.sample_info, "host_crystal"):
            # plot olivine and corrected spectrum
            pass

        # Calculate ymax and set axis limits
        x_trim = (self.xmax > sample.x) & (sample.x > self.xmin)
        y_max = np.max(sample.signal.raw[x_trim]) * 1.3
        self.ax.set_ylim(0, y_max)
        self.ax.set_xlim(self.xmin, self.xmax)

        # Plot spectra
        (self.raw_spectrum,) = self.ax.plot(
            sample.x,
            sample.signal.raw,
            color=self.colors[0],
            label="raw",
        )
        if hasattr(self.sample_info, "host_crystal"):
            olivine = self.sample_info.host_crystal
            (self.olivine,) = self.ax.plot(
                olivine.x,
                olivine.signal.baseline_corrected,
                color=self.colors[1],
                label="olivine",
            )

        self.canvas.draw()

    def update_plot(self):
        """ """
        self.sample_info = self.app.current_sample
        sample = self.sample_info.sample
        self.old_spectrum = sample._spectrumSelect

        self.raw_spectrum.set_data(sample.x, sample.signal.raw)

        if hasattr(self, "olivine"):
            olivine = self.sample_info.host_crystal
            self.olivine.set_data(olivine.x, olivine.signal.baseline_corrected)

        # Calculate ymax and set axis limits
        x_trim = (self.xmax > sample.x) & (sample.x > self.xmin)
        y_max = np.max(sample.signal.raw[x_trim]) * 1.3
        self.ax.set_ylim(0, y_max)
        self.ax.set_xlim(self.xmin, self.xmax)

        self.fig.canvas.draw_idle()

    def load_olivine(self):
        """ """
        index = self.app.current_sample.index

        try:
            filename = tk.filedialog.askopenfilenames(initialdir=os.getcwd())
        except AttributeError:
            print("Opening file cancelled by user")
            return

        self.app.data_bulk.add_host_crystal(index=index, file=filename, phase="olivine")
        self.app.current_sample.host_crystal = self.app.data_bulk.host_crystals[index]
        self.update_plot()
