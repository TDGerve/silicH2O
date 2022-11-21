import matplotlib.pyplot as plt


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


def Plot_layout(
    scaling,
    linewidth=0.8,
    font_size=8,
    colors=colors.vitaminC,
):
    font_size = font_size / scaling
    axtitle_size = font_size + 3
    axlabel_size = font_size + 2
    ticklabel_size = font_size + 1

    linewidth = linewidth / scaling

    plt.rcParams["figure.constrained_layout.use"] = True
    plt.rcParams["savefig.dpi"] = 300

    # Text
    plt.rc("font", family="sans-serif", size=font_size)

    # Legend
    plt.rc("legend", fontsize=font_size, fancybox=False, facecolor="white")

    # Axes
    plt.rc("xtick", direction="in", top=True, labelsize=ticklabel_size)
    plt.rc("xtick.major", size=3 / scaling, width=linewidth)
    plt.rc("ytick", right=True, direction="in", labelsize=ticklabel_size)

    plt.rc(
        "axes",
        grid=True,
        titlesize=axtitle_size,
        labelsize=axlabel_size,
        axisbelow=True,
        linewidth=linewidth,
        prop_cycle=colors,
        facecolor="white",
    )
    plt.rc("axes.grid", axis="x")
    plt.rc("grid", color="whitesmoke", alpha=1)

    # Lines
    plt.rc("lines", linewidth=linewidth, markersize=10 / scaling, markeredgecolor="k")
