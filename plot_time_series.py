from seiches_io import load
from seiches_io_references import *
from pathlib import Path
import os
import matplotlib.pyplot as plt

path = Path(os.path.join(base_figures_dir, "test.png"))
path.parent.mkdir(parents=True, exist_ok=True)

measured_time_series = load(os.path.join(base_output_dir, "Measured_time_series.pyst"))
schematized_time_series = load(os.path.join(base_output_dir, "Schematized_time_series.pyst"))
nse_time_series = schematized_time_series[1][1]
no_seiche_series = schematized_time_series[0][1]

for time_series in schematized_time_series[2:]:
    fig, axs = plt.subplots(ncols=1, nrows=2)
    fig.suptitle(time_series[0], fontsize=16)
    axs[0].set_facecolor("#F2F2F2")
    axs[1].set_facecolor("#F2F2F2")

    axs[0].plot(nse_time_series.times, nse_time_series.seiches_signal, "#FF960D", label="Incl. NSE")
    axs[0].plot(time_series[1].times, time_series[1].seiches_signal, "#080C80", label="Incl. seiches")
    axs[0].grid(True, color="#E6E6E6")
    axs[0].set(ylabel="Seiche uitwijking [m]")

    axs[1].plot(no_seiche_series.times, no_seiche_series.water_levels, "#00B389", label="Excl. seiches")
    axs[1].plot(nse_time_series.times, nse_time_series.water_levels, "#FF960D", label="Incl. NSE")
    axs[1].plot(time_series[1].times, time_series[1].water_levels, "#080C80", label="Incl. seiches")
    axs[1].grid(True, color="#E6E6E6")
    axs[1].set(ylabel="Waterstand [m+NAP]", xlabel="Tijd [uur]")
    axs[1].legend()

    fig.tight_layout()
    fig.savefig(os.path.join(base_figures_dir, time_series[0] + ".png"))

for m in measured_time_series:
    series = m[1]
    fig, axs = plt.subplots(ncols=1, nrows=1)
    fig.suptitle(m[0])

    axs.set_facecolor("#F2F2F2")
    axs.plot([t / 3600 for t in series.times], series.water_levels_measured, "#FF960D", label="Gemeten")
    axs.plot([t / 3600 for t in series.times], series.water_levels_filtered, "#00B389", label="Gefilterd (geen seiches)")
    axs.plot([t / 3600 for t in series.times], series.seiches_signal, "#080C80", label="Seiches signaal")

    axs.grid(True, color="#E6E6E6")

    axs.set(ylabel="Waterstand [m+NAP]", xlabel="Tijd [uur]")
    axs.legend()

    fig.tight_layout()
    fig.savefig(os.path.join(base_figures_dir, m[0] + ".png"))
