from calculate_utils import profiles, schematized_time_series, get_calculation_name, read_schematization
from seiches_io import load, save
from seiches_io_references import schematic_output_dir, schematic_figures_dir
from pydrever.data import (
    DikeSchematization,
    DikernelOutputLocation,
    GrassCumulativeOverloadOutputLocation,
    GrassWaveImpactOutputLocation,
    DikernelInput,
)
from plot_utils import find_patch
import os
import matplotlib.pyplot as plt
import numpy


def add_result_to_plot(results: list[DikernelOutputLocation], label, marker, color, ax):
    ax.plot(
        [r.x_position for r in results],
        [r.final_damage for r in results],
        label=label,
        color=color,
        marker=marker,
        markeredgecolor="k",
        markerfacecolor=color,
    )


markers = ["o", "s", "v", "^", "*", "+", "<"]
colors = ["#080C80", "#0EBBF0", "#00B389", "#00E6A1", "#e6e6e6", "#ffd814", "#ff960d"]


def plot_run(
    schematization: DikeSchematization,
    results: list[list],
    h_min,
    h_max,
    wave_height,
    wave_period,
    output_file_name: str,
    figure_title: str,
):
    fig = plt.figure(figsize=(10, 6))
    fig.suptitle(figure_title)

    ax1 = plt.subplot(2, 1, 1)
    ax1.grid()
    ax1.set(ylabel="Schadegetal [-]")

    for ir, result in enumerate(results):
        add_result_to_plot(
            [r for r in result[1] if isinstance(r, GrassCumulativeOverloadOutputLocation) and r.x_position < schematization.x_outer_crest],
            "_nolegend_",
            markers[ir],
            colors[ir],
            ax1,
        )
        add_result_to_plot(
            [r for r in result[1] if isinstance(r, GrassCumulativeOverloadOutputLocation) and r.x_position >= schematization.x_outer_crest],
            "_nolegend_",
            markers[ir],
            colors[ir],
            ax1,
        )
        add_result_to_plot([r for r in result[1] if isinstance(r, GrassWaveImpactOutputLocation)], result[0], markers[ir], colors[ir], ax1)

    ax1.text(
        0.95,
        0.96,
        f"$H_s = {wave_height:.2f}$",
        transform=ax1.transAxes,
        ha="right",
        va="top",
        color="k",
    )

    ax1.text(
        0.95,
        0.90,
        f"$T_p = { wave_period:.2f}$",
        transform=ax1.transAxes,
        ha="right",
        va="top",
        color="k",
    )
    ax1.legend(loc="upper left")

    ax2 = plt.subplot(2, 1, 2, sharex=ax1)
    ax2.grid()
    ax2.set(ylabel="Hoogte [m+NAP]", xlabel="Afstand [m]")
    x_final, z_lower_final, z_upper_final = find_patch(
        x_positions=schematization.x_positions, z_positions=schematization.z_positions, h_min=h_min, h_max=h_max
    )
    plt.fill_between(x_final, z_lower_final, z_upper_final, color="#0EBBF0", alpha=0.2)

    ax2.plot(schematization.x_positions, schematization.z_positions)

    x_final, z_lower_final, z_upper_final = find_patch(
        x_positions=schematization.x_positions, z_positions=schematization.z_positions, h_min=h_min, h_max=h_max
    )
    plt.fill_between(x_final, z_lower_final, z_upper_final, color="#0EBBF0", alpha=0.2)

    x_locations = [l.x_position for l in results[0][1]]
    final_damages = [max(*v) for v in zip(*[[l.final_damage for l in r[1]] for r in results])]
    x_failed = [x for x, d in zip(x_locations, final_damages) if d > 1.0]
    x_passed = [x for x, d in zip(x_locations, final_damages) if d <= 1.0]
    z_failed = numpy.interp(
        x_failed,
        schematization.x_positions,
        schematization.z_positions,
    )
    z_passed = numpy.interp(
        x_passed,
        schematization.x_positions,
        schematization.z_positions,
    )

    ax2.plot(
        schematization.x_positions,
        schematization.z_positions,
        linestyle="solid",
        linewidth=3,
        color="#FF960D",
        marker="o",
    )
    ax2.plot(x_passed, z_passed, linestyle="none", marker="o", color="g")
    ax2.plot(x_failed, z_failed, linestyle="none", marker="x", color="r")

    fig.tight_layout()

    fig.savefig(os.path.join(schematic_figures_dir, output_file_name))


for profile in profiles:
    calculation_name = f"Profiel {profile.value}"
    figure_title = calculation_name
    results = []
    schematization = read_schematization(profile)
    print(f"Plotting: {profile.value}", end="")
    h_min = 10
    h_max = -10
    for time_serie in schematized_time_series:
        h_max_series = max(time_serie[1].water_levels)
        if h_max_series > h_max:
            h_max = h_max_series

        h_min_series = min(time_serie[1].water_levels)
        if h_min_series < h_min:
            h_min = h_min_series
        result = load(os.path.join(schematic_output_dir, get_calculation_name(profile, time_serie[0]) + ".pyst"))
        results.append([time_serie[0], result[2]])

    conditions = result[1].hydrodynamic_input
    plot_run(
        schematization,
        results,
        h_min,
        h_max,
        max(conditions.wave_heights),
        max(conditions.wave_periods),
        output_file_name=calculation_name + ".png",
        figure_title=figure_title,
    )

    plt.close("all")
    print(" - Finished")
