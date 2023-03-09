import matplotlib as mpl

from .baseline_correction_plots import *
from .Calibration_plots import *
from .Interference_plots import *
from .Interpolation_plots import *
from .plot_interaction import *
from .plots import *

# Set Tk as the backend
mpl.use("TkAgg")
# import pyplot again
from matplotlib import pyplot as plt
