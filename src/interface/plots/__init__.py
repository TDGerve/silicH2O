from .plots import *
from .double_plots import *
import sys

if sys.platform != "win":
    import matplotlib as mpl

    mpl.use("TkAgg")
    from matplotlib import pyplot as plt
