from matplotlib.font_manager import FontProperties
import matplotlib.pyplot as plt
import matplotlib as mpl
from importlib import resources
import pandas as pd
import seaborn as sns

# Color palettes
class colors:
    """
    Color palettes for plots
    """

    flatDesign = plt.cycler(
        color=["#e27a3d", "#344d5c", "#df5a49", "#43b29d", "#efc94d"]
    )

    firenze = plt.cycler(color=["#8E2800", "#468966", "#B64926", "#FFF0A5", "#FFB03B"])

    vitaminC = plt.cycler(color=["#FD7400", "#004358", "#FFE11A", "#1F8A70", "#BEDB39"])

    bella = plt.cycler(color=["#801637", "#047878", "#FFB733", "#F57336", "#C22121"])

    buddha = plt.cycler(color=["#192B33", "#FF8000", "#8FB359", "#FFD933", "#CCCC52"])

    elemental = plt.cycler(
        color=["#E64661", "#FFA644", "#998A2F", "#2C594F", "#002D40"]
    )

    carolina = plt.cycler(color=["#73839C", "#2E4569", "#AECCCF", "#D5957D", "#9C7873"])

    fourtyTwo = plt.cycler(
        color=["#2469A6", "#C4E1F2", "#F2E205", "#F2D22E", "#D9653B"]
    )

    terrazaverde = plt.cycler(
        color=["#DFE2F2", "#88ABF2", "#4384D9", "#56BFAC", "#D9B341"]
    )


def plot_layout(
    linewidth=1.2,
    fontSize=14,
    axTitleSize=14,
    axLabelSize=14,
    tickLabelSize=10,
    colors=colors.bella,
):

    plt.rcParams["figure.constrained_layout.use"] = True
    plt.rcParams["savefig.dpi"] = 300

    plt.rc("figure", figsize=(8, 7), facecolor="white")

    # Text
    plt.rc("font", family="sans-serif", size=fontSize)

    # Legend
    plt.rc("legend", fontsize=fontSize / 1.5, fancybox=False, facecolor="white")

    # Axes
    plt.rc("xtick", direction="in", labelsize=tickLabelSize)
    plt.rc("ytick", direction="in", labelsize=tickLabelSize)
    plt.rc(
        "axes",
        grid=True,
        titlesize=axTitleSize,
        labelsize=axLabelSize,
        axisbelow=True,
        linewidth=linewidth,
        prop_cycle=colors,
        facecolor="whitesmoke",
    )
    plt.rc("grid", color="snow")

    # Lines
    plt.rc("lines", linewidth=linewidth, markersize=10, markeredgecolor="k")


