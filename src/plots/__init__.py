import sys

from .baseline_correction_plots import *
from .Calibration_plots import *
from .Interference_plots import *
from .Interpolation_plots import *
from .plot_interaction import *
from .plots import *


def set_plot_backend():
    # if sys.platform != "win32":
    import matplotlib as mpl

    mpl.use("TkAgg")
    # reimport pyplot
    from matplotlib import pyplot as plt


set_plot_backend()
