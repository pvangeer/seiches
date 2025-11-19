from seiches_io import load
from seiches_io_references import *
from pathlib import Path
import os

path = Path(os.path.join(base_figures_dir, "test.png"))
path.parent.mkdir(parents=True, exist_ok=True)

profiles = load(os.path.join(base_output_dir, "Profiles.pyst"))

for pr in profiles:
    import matplotlib.pyplot as plt

    fig, axs = plt.subplots(ncols=1, nrows=1)
    fig.suptitle("Profiel " + pr[0])
    axs.set_facecolor("#F2F2F2")
    axs.plot(pr[1].x_positions, pr[1].z_positions, "#FF960D", zorder=1, marker="o", markersize=8, label="Profiel " + pr[0] + " - AHN")

    i_outer_toe = pr[1].x_positions.index(pr[1].x_outer_toe)
    i_outer_crest = pr[1].x_positions.index(pr[1].x_outer_crest)
    i_inner_toe = pr[1].x_positions.index(pr[1].x_inner_toe)
    i_inner_crest = pr[1].x_positions.index(pr[1].x_inner_crest)

    axs.scatter(
        pr[1].x_outer_toe,
        pr[1].z_positions[i_outer_toe],
        s=100,
        zorder=2,
        marker="o",
        c="#080C80",
        edgecolors="k",
        label="Buitenteen",
    )
    axs.scatter(
        pr[1].x_outer_crest, pr[1].z_positions[i_outer_crest], s=100, zorder=3, marker="o", c="#00B389", edgecolors="k", label="Buitenkruin"
    )
    axs.scatter(
        pr[1].x_inner_crest,
        pr[1].z_positions[i_inner_crest],
        s=100,
        zorder=3,
        marker="o",
        c="#00E6A1",
        edgecolors="k",
        label="Binnenkruin",
    )
    axs.scatter(
        pr[1].x_inner_toe, pr[1].z_positions[i_inner_toe], s=100, zorder=3, marker="o", c="#0EBBF0", edgecolors="k", label="Binnenteen"
    )

    axs.grid(True, color="#E6E6E6")
    axs.set(ylabel="Hoogte [m+NAP]", xlabel="Afstand [m]")
    axs.set_axisbelow(True)
    axs.legend()

    fig.tight_layout()
    fig.savefig(os.path.join(base_figures_dir, "Profile " + pr[0] + ".png"))
