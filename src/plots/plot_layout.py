import matplotlib.pyplot as plt

markers = ["^", "D", "s", "o", "p", "8", "h", "d", 4, 5]
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

    hollywood = plt.cycler(
        color=[
            "#8ECAE6",
            "#FD9E02",
            "#219EBC",
            "#FB8500",
            "#126782",
            "#FFB703",
            "#023047",
        ],
    )

    campfire = plt.cycler(color=["#588C7E", "#F2E394", "#F2AE72", "#D96459", "#8C4646"])

    pastel = plt.cycler(
        color=[
            "#FAD2E1",
            "#BCD4E6",
            "#C5DEDD",
            "#99C1DE",
            "#EDDCD2",
            "#DBE7E4",
            "#FFF1E6",
            "#F0EFEB",
            "#FDE2E4",
            "#D6E2E9",
        ],
    )

    autumn = plt.cycler(
        color=[
            "#797D62",
            "#FFCB69",
            "#9B9B7A",
            "#E8AC65",
            "#BAA587",
            "#D08C60",
            "#D9AE94",
            "#B58463",
            "#997B66",
            "#F1DCA7",
        ],
    )

    rainbow = plt.cycler(
        color=[
            "#54478C",
            "#83E377",
            "#2C699A",
            "#048BA8",
            "#B9E769",
            "#EFEA5A",
            "#0DB39E",
            "#F1C453",
            "#16DB93",
            "#F29E4C",
        ]
    )

    matteblue = plt.cycler(
        color=["#666A86", "#788AA3", "#92B6B1", "#B2C9AB", "#E8DDB5"],
    )


def plot_layout(
    scaling,
    linewidth=0.5,
    font_size=8,
    colors=colors.rainbow,
):

    font_size = font_size / scaling
    axtitle_size = font_size + 3
    axlabel_size = font_size + 2
    ticklabel_size = font_size + 1

    linewidth = linewidth / scaling

    plt.rcParams["figure.constrained_layout.use"] = True
    plt.rcParams["savefig.dpi"] = 300

    plt.rc("figure", figsize=(8, 7), facecolor="white")

    # Text
    plt.rc("font", family="sans-serif", size=font_size)

    # Legend
    plt.rc("legend", fontsize=font_size, fancybox=False, facecolor="white")

    # Axes
    plt.rc("xtick", direction="in", top=True, labelsize=ticklabel_size)
    plt.rc("xtick.major", size=3 / scaling, width=linewidth)
    plt.rc("ytick", right=True, direction="in", labelsize=ticklabel_size)

    # Axes
    plt.rc(
        "axes",
        grid=True,
        axisbelow=True,
        prop_cycle=colors,
        facecolor="snow",
        linewidth=1,
    )
    plt.rc("grid", color="gainsboro")
    plt.rc("axes.grid", axis="x")

    # Lines
    plt.rc("lines", linewidth=linewidth, markersize=10 / scaling, markeredgecolor="k")
