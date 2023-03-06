import sys

from .baseline_correction_plots import *
from .Calibration_plots import *
from .Interference_plots import *
from .Interpolation_plots import *
from .plot_interaction import *
from .plots import *

if sys.platform != "win":
    import matplotlib as mpl

    mpl.use("TkAgg")
    from matplotlib import pyplot as plt
