from .plot_interaction import *
from .Baseline_correction_plots import *
from .plots import *
import sys

if sys.platform != "win":
    import matplotlib as mpl

    mpl.use("TkAgg")
    from matplotlib import pyplot as plt
