from tkinter import ttk
import tkinter as tk
import matplotlib.pyplot as plt
import numpy as np
import json
from plot_layout import plot_layout
from data_processing import data_processing

def import_birs_settings():
    with open("birs.json") as f: # keeo json file in same folder
        birs_all = json.load(f)


    birs_use = {}

    for name, bir in birs_all.items():
        birs_use[name] = bir["use"]

    return birs_use    


class settings:
    """
    Settings window
    """

    def __init__(self, parent, app):
        self.app = app
        self.parent = parent

        # Import processing settings from settinges.json
        self.import_settings()
        self.birs_use = import_birs_settings()
        """
        Default settings imported from json:
        ---------------------------
        laser_wavelength        float
        name_separator          str     
        Si_bir                  str
        H2O_left                int
        H2O_right               int
        interpolate_left        int
        interpolate_right       int
        interpolation_smoothing int, float
        """
        # File settings
        self.name_separator_var = tk.StringVar()
        self.name_separator_var.set(self.name_separator)
        # Raman Settings
        self.laser_var = tk.DoubleVar()
        self.laser_var.set(self.laser_wavelength)

        # Plot Layout
        # Set the plot layout
        fontsize = 6
        plot_layout(
            axTitleSize=fontsize,
            axLabelSize=fontsize,
            tickLabelSize=fontsize / 1.2,
            fontSize=fontsize,
    )
        
        
    def import_settings(self):
        with open("settings.json") as f:
            settings = json.load(f)

        for name, value in settings.items():
            setattr(self, name, value)

    def open_general_settings(self):

        font = (self.app.font, "16")

        popup = tk.Toplevel(self.parent)
        popup.title("Settings")
        window = ttk.Frame(popup)
        window.grid(column=0, row=0, sticky=("nesw"))
        popup.columnconfigure(0, weight=1)
        popup.rowconfigure(4, weight=1)
        # temparary variables
        laser_temp = tk.StringVar()
        separator_temp = tk.StringVar()
        # Create labels
        ttk.Label(window, text="Laser wavelength (nm)", font=font).grid(row=1, column=0)
        ttk.Label(window, text="File sample name separator", font=font).grid(row=3, column=0)
        ttk.Label(window, text="Current", font=font).grid(row=0, column=1)
        ttk.Label(window, text="New", font=font).grid(row=0, column=2)
        ttk.Label(window, textvariable=self.laser_var, font=font).grid(row=1, column=1)
        ttk.Label(window, textvariable=self.name_separator_var, font=font).grid(row=3, column=1)
        ttk.Label(window, text="Press Enter to store\nReload spectra to use new laser wavelength", font=font).grid(
            row=4, column=0, columnspan=3, sticky=("nesw")
        )
        # Create entry fields
        laser_entry = ttk.Entry(window, textvariable=laser_temp)
        separator_entry = ttk.Entry(window, textvariable=separator_temp)
        laser_entry.grid(row=1, column=2, sticky=("we"))
        separator_entry.grid(row=3, column=2, sticky=("we"))

        for child in window.winfo_children():
            child.grid_configure(padx=5, pady=5)

        def store_laser(event):
            try:
                new_laser = float(laser_temp.get())
                self.laser_var.set(new_laser)
                self.laser_wavelength = new_laser
            except ValueError:
                self.parent.bell()
                return


        def store_separator(event):
            self.name_separator_var.set(separator_temp.get())
            
            if self.app.data_bulk:
                files = self.app.data_bulk.files
                names = ()
                
                names = self.app.data_bulk.get_names_from_files(files)
                self.app.data_bulk.names = names
                self.app.samplesVar.set(list(names))



        laser_entry.bind("<Return>", store_laser)
        separator_entry.bind("<Return>", store_separator)
        # Keep window on top
        popup.attributes("-topmost", True)

    def open_bir_settings(self):

        birs = data_processing.Si_birs 
        bir_number = len(birs)
        column_max = 4
        column_number = column_max if bir_number > column_max else bir_number
        row_number = -1 * (-column_max // bir_number) # Ceiling divide

        font = (self.app.font, "14")

        popup = tk.Toplevel(self.parent)
        popup.title("Baseline interpolation regio settings")
        popup.columnconfigure(0, weight=1)
        popup.rowconfigure(0, weight=1)

        window = ttk.Frame(popup)
        window.grid(column=0, row=0, sticky=("nesw"))
        # window.rowconfigure(0, weight=1)
        # for row in range(1, row_number):
        #     window.rowconfigure(row, weight=2)
        # for column in range(column_max):
        #     window.columnconfigure(column, weight=1)

        padding = 20

        birs_title = ttk.Label(text="Baseline interpolation regions", font=(self.app.font, "14", "bold"))
        bir_label_frame = ttk.Labelframe(window, text="Silicate interpolation\nregions", padding=padding)
        bir_label_frame.grid(row=0, column=0, sticky=("nesw"))

        bir_frames = []
        for i in range(bir_number):
            bir_frame = ttk.Frame(bir_label_frame)
            bir_frame.grid(row=int(i / column_max), column=int(i % column_max), sticky=("nesw"))
            bir_frames.append(bir_frame)
        
        for i, (name, bir) in enumerate(birs.items()):
            ttk.Label(bir_frames[i], text=name, font=(self.app.font, "14", "bold")).grid(row=0, column=0, sticky=("nesw"))
            ttk.Separator(bir_frames[i], orient=tk.HORIZONTAL).grid(row=0, column=0, sticky=("sew"))
            for j, region in enumerate(bir):
                text = f"{region[0]:<5}-{region[1]:>5}"
                if j +1 == len(bir):
                    text = f"{region[0]: <4} \u2192"
                ttk.Label(bir_frames[i], text=text, font="TkFixedFont").grid(row=j+1, column=0, sticky=("nesw"))
 
                
        for child in bir_label_frame.winfo_children():
            child.grid_configure(padx=15, pady=20)

        table_frame = ttk.Frame(window, padding=padding)
        table_frame.grid(row=0, column=1)
        tickboxes = []
        radiobuttons = []
        bir_use = {}
        bir_default_var = tk.StringVar()
        bir_default_var.set(self.Si_bir)
        ttk.Label(table_frame, text="BIR", font=(self.app.font, "14", "bold")).grid(row=0, column=0, sticky=("nws"))
        ttk.Label(table_frame, text="Use", font=(self.app.font, "14", "bold")).grid(row=0, column=1, sticky=("nesw"))
        ttk.Label(table_frame, text="Default", font=(self.app.font, "14", "bold")).grid(row=0, column=2, sticky=("nesw"))
        for i, name in enumerate(birs):
            ttk.Label(table_frame, text=name, font=font).grid(row=i + 1, column=0, sticky=("nes"))
            tick_var = tk.BooleanVar()
            tick_var.set(self.birs_use[name])
            tick = ttk.Checkbutton(table_frame, variable=tick_var, onvalue=True, offvalue=False)
            radio = ttk.Radiobutton(table_frame, variable=bir_default_var, value=name)
            tick.grid(row=i + 1, column=1, sticky=("nesw"))
            radio.grid(row=i + 1, column=2, sticky=("nesw"))
            bir_use[name] = tick_var
            tickboxes.append(tick)
            radiobuttons.append(radio)
        ttk.Separator(table_frame, orient=tk.HORIZONTAL).grid(row=0, column=0, columnspan=3, sticky=("sew"))    
        ttk.Separator(table_frame, orient=tk.VERTICAL).grid(row=1, column=1, rowspan=len(birs), sticky=("nse"))


        """
        Create buttons for:
            - new BIR
            - reload defaults
            - Save and set
        A table with:
            Tickboxes for:
            - use
            Radiobuttons for:
            - Set as default
        """

        for child in window.winfo_children():
            child.grid_configure(padx=10, pady=10)







        