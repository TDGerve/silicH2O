import os
import ramCOH as ram
import pandas as pd
import numpy as np
import json



def import_birs():
    with open("birs.json") as f: # keeo json file in same folder
        birs_all = json.load(f)

    birs = {}

    for name, bir in birs_all.items():
        birs[name] = np.array(bir["birs"])   

    return birs    


class data_processing:

    smooth_factor = 1

    # Get baseline interpolation regions
    Si_birs = import_birs()

    def __init__(self, files, settings, modeltype="H2O"):
        self.settings = settings
        # Parse files
        self.files = tuple(files)
        self.names = self.get_names_from_files(files)

        self.samples = {}
        self.host_crystals = {}
        self.model = getattr(ram, modeltype)
        self.sample_selected = None
        self.sample_name = None

        # Create dataframe to store outputs
        self.results = pd.DataFrame({"name": self.names})
        self.results["SiArea"] = np.zeros(self.results.shape[0])
        self.results["H2Oarea"] = np.zeros(self.results.shape[0])
        self.results["rWS"] = np.zeros(self.results.shape[0])

        # Create dataframe to store processing parameters
        self.processing = pd.DataFrame({"name": self.names, "interpolate": False})
        self.processing["interpolate_left"] = int(self.settings.interpolate_left) 
        self.processing["interpolate_right"] = int(self.settings.interpolate_right)
        self.processing["interpolation_smoothing"] = self.settings.interpolation_smoothing
        self.processing["Si_bir"] = self.settings.Si_bir  
        self.processing["water_left"] = int(self.settings.H2O_left)
        self.processing["water_right"] = int(self.settings.H2O_right)

        # # Get baseline interpolation regions
        # self.Si_birs_labels, self.Si_birs = import_birs()

    def get_names_from_files(self, files):
        separator = self.settings.name_separator_var.get()
        names = tuple()

        for file in files:
            name = os.path.basename(file)
            if separator not in name:
                names = names + tuple([name])
            else:
                names = names + tuple([name[: name.find(separator)]])

        return names     
        

    def preprocess(self):
        laser = self.settings.laser_var.get()
        for i, f in enumerate(self.files):
            x, y = np.genfromtxt(f, unpack=True)
            self.samples[i] = self.model(x, y, laser=laser)
            # self.samples[i].longCorrect()
            self.samples[i].baselineCorrect(smooth_factor=self.smooth_factor)
            self.samples[i].calculate_SiH2Oareas()
            Si_area, H2O_area = self.samples[i].SiH2Oareas
            self.results.loc[i, ["SiArea", "H2Oarea"]] = Si_area, H2O_area
            self.results.loc[i, "rWS"] = H2O_area / Si_area

            self.host_crystals[i] = None
        self.sample_selected = 0
        self.sample_name = self.names[self.sample_selected]

    def add_sample(self, file):
        """ 
        """
        laser = self.settings.laser_var.get()
        # Get name, file and index
        index = len(self.files)
        name = self.get_names_from_files([file])
        self.names = self.names + name
        self.files = self.files + tuple([file])
        # Load and processes spectrum
        x, y = np.genfromtxt(file, unpack=True)
        self.samples[index] = self.model(x, y, laser=laser)
        # self.samples[index].longCorrect()
        self.samples[index].baselineCorrect(smooth_factor=1)
        self.samples[index].calculate_SiH2Oareas()
        # Calculate areas
        Si_area, H2O_area = self.samples[index].SiH2Oareas
        # Add sample to the results and processing dataframes
        new_processing = pd.Series(
            {
                "name": name[0],
                "interpolate": False,
                "interpolate_left": int(self.settings.interpolate_left),
                "interpolate_right": int(self.settings.interpolate_right),
                "Si_bir": self.settings.Si_bir,
                "water_left": int(self.settings.H2O_left),
                "water_right": int(self.settings.H2O_right),
            }, name=index
        )
        self.processing.loc[index] = new_processing
        new_result = pd.Series(
            {
                "name": name[0],
                "SiArea": Si_area,
                "H2Oarea": H2O_area,
                "rWs": H2O_area / Si_area,
            }, name=index
        )
        self.results.loc[index] = new_result

    def add_host_crystal(self, index, file, phase):
        laser = self.settings.laser_var.get()
        model = getattr(ram, phase)
        x, y = np.genfromtxt(file, unpack=True)
        self.host_crystals[index] = model(x, y, laser=laser)
        self.host_crystals[index].baselineCorrect()


    def batch_recalculate(self, save=True):
        for i, sample in self.samples.items():

            H2O_left, H2O_right = self.processing.loc[i, ["water_left", "water_right"]]
            Si_birs_select = int(self.processing.loc[i, "Si_bir"])
            Si_bir = self.Si_birs[Si_birs_select]

            sample.baselineCorrect(Si_birs=Si_bir, H2O_boundaries=[H2O_left, H2O_right], smooth_factor=self.smooth_factor)
            sample.calculate_SiH2Oareas()
            Si_area, H2O_area = sample.SiH2Oareas

            if save:
                self.results.loc[i, ["SiArea", "H2Oarea"]] = Si_area, H2O_area
                self.results.loc[i, "rWS"] = H2O_area / Si_area
