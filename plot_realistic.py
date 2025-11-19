import matplotlib

matplotlib.use("Agg")
import os
from pydrever.data import DikernelOutputLocation, DikernelInput
from seiches_io import load
from seiches_io_references import *
from data_calculation import *
import matplotlib.pyplot as plt
from pydrever.visualization import plot_hydrodynamic_conditions
from calculate_utils import profiles, measured_time_series, get_calculation_name, find_horizontal_intersections
from pydrever.data import TimeDependentOutputQuantity, GrassWaveImpactOutputLocation, GrassCumulativeOverloadOutputLocation
import numpy
from collections import defaultdict


def get_output_values(output) -> list[list[float]]:
    return [getattr(location, TimeDependentOutputQuantity.DamageDevelopment.value) for location in output]


def find_patch(x_positions: list[float], z_positions: list[float], h_max: float, h_min: float):
    x = [x for x in x_positions]
    z_upper = [h_max if z <= h_max else z for z in z_positions]
    z_lower = [h_min if z <= h_min else z for z in z_positions]

    x_z_max_intersections = find_horizontal_intersections(x_positions, z_positions, h_max)
    x_z_min_intersections = find_horizontal_intersections(x_positions, z_positions, h_min)

    z_min_dict = defaultdict(list)
    z_max_dict = defaultdict(list)
    x_all = x
    x_all.extend(x_z_min_intersections)
    x_all.extend(x_z_max_intersections)
    z_min_all = z_lower
    z_min_all.extend([h_min for z in x_z_min_intersections])
    z_min_all.extend([h_max for z in x_z_max_intersections])
    z_max_all = z_upper
    z_max_all.extend([h_max for z in x_z_min_intersections])
    z_max_all.extend([h_max for z in x_z_max_intersections])

    z_min_dict = defaultdict(list)
    z_max_dict = defaultdict(list)
    for x, z_min, z_max in zip(x_all, z_min_all, z_max_all):
        z_min_dict[x].append(z_min)
        z_max_dict[x].append(z_max)

    x_final = sorted(set(x_all))
    z_lower_final = [z_min_dict[x][0] for x in x_final]
    z_upper_final = [z_max_dict[x][0] for x in x_final]

    return x_final, z_lower_final, z_upper_final


def plot_run(
    input: DikernelInput,
    result_measured: list[DikernelOutputLocation],
    result_filtered: list[DikernelOutputLocation],
    output_file_name: str,
    fig_title: str,
):
    output_measured = result_measured
    output_filtered = result_filtered

    fig = plt.figure(figsize=(10, 6))
    fig.suptitle(fig_title)

    ax1 = plt.subplot(2, 1, 1)
    ax1.grid()
    ax1.set(ylabel="Schadegetal [-]")

    x_outer_crest = input.dike_schematization.x_outer_crest
    output_impact_measured = [o for o in output_measured if isinstance(o, GrassWaveImpactOutputLocation) and o.x_position < x_outer_crest]
    output_impact_filtered = [o for o in output_filtered if isinstance(o, GrassWaveImpactOutputLocation) and o.x_position < x_outer_crest]
    output_runup_measured = [
        o for o in output_measured if isinstance(o, GrassCumulativeOverloadOutputLocation) and o.x_position < x_outer_crest
    ]
    output_runup_filtered = [
        o for o in output_filtered if isinstance(o, GrassCumulativeOverloadOutputLocation) and o.x_position < x_outer_crest
    ]
    marker_edge_color = "k"
    filtered_face_color = "#FFD814"
    measured_face_color = "#00B389"
    filtered_color = "#9f9f9f"
    measured_color = "#6f6f6f"
    marker_size = 8

    plt.axhline(1.0, color="red", linewidth=2.0, linestyle="--")
    ax1.plot(
        [l.x_position for l in output_impact_filtered],
        [loc.final_damage for loc in output_impact_filtered],
        linestyle="--",
        marker="s",
        markersize=marker_size,
        markerfacecolor=filtered_face_color,
        markeredgecolor=marker_edge_color,
        color=filtered_color,
        label="Golfklap (zonder seiches)",
    )
    ax1.plot(
        [l.x_position for l in output_impact_measured],
        [loc.final_damage for loc in output_impact_measured],
        linestyle="-",
        marker="o",
        markersize=marker_size,
        markerfacecolor=measured_face_color,
        markeredgecolor=marker_edge_color,
        color=measured_color,
        label="Golfklap (seiches)",
    )

    ax1.plot(
        [l.x_position for l in output_runup_filtered],
        [loc.final_damage for loc in output_runup_filtered],
        linestyle="--",
        marker="<",
        markersize=marker_size,
        markerfacecolor=filtered_face_color,
        markeredgecolor=marker_edge_color,
        color=filtered_color,
        label="golfoploop (zonder seiches)",
    )
    ax1.plot(
        [l.x_position for l in output_runup_measured],
        [loc.final_damage for loc in output_runup_measured],
        linestyle="-",
        marker="h",
        markersize=marker_size,
        markerfacecolor=measured_face_color,
        markeredgecolor=marker_edge_color,
        color=measured_color,
        label="Golfoploop (seiches)",
    )

    output_overtopping_measured = [o for o in result_measured if o.x_position >= x_outer_crest]
    output_overtopping_filtered = [o for o in result_filtered if o.x_position >= x_outer_crest]
    ax1.plot(
        [o.x_position for o in output_overtopping_filtered],
        [o.final_damage for o in output_overtopping_filtered],
        linestyle="--",
        marker=">",
        markersize=marker_size,
        markerfacecolor=filtered_face_color,
        markeredgecolor=marker_edge_color,
        color=filtered_color,
        label="Overslag (zonder seiches)",
    )
    ax1.plot(
        [o.x_position for o in output_overtopping_measured],
        [o.final_damage for o in output_overtopping_measured],
        linestyle="-",
        marker="p",
        markersize=marker_size,
        markerfacecolor=measured_face_color,
        markeredgecolor=marker_edge_color,
        color=measured_color,
        label="Overslag (seiches)",
    )
    ax1.legend(loc="lower left")

    x_failed = list(loc.x_position for loc in output_measured if loc.failed)
    x_passed = list(loc.x_position for loc in output_measured if not loc.failed)
    z_failed = numpy.interp(
        x_failed,
        input.dike_schematization.x_positions,
        input.dike_schematization.z_positions,
    )
    z_passed = numpy.interp(
        x_passed,
        input.dike_schematization.x_positions,
        input.dike_schematization.z_positions,
    )

    ax2 = plt.subplot(2, 1, 2, sharex=ax1)

    ax2.grid()
    ax2.set(ylabel="Hoogte [m+NAP]", xlabel="Afstand [x]")

    h_max = max(input.hydrodynamic_input.water_levels)
    h_min = min(input.hydrodynamic_input.water_levels)
    x_final, z_lower_final, z_upper_final = find_patch(
        x_positions=input.dike_schematization.x_positions, z_positions=input.dike_schematization.z_positions, h_min=h_min, h_max=h_max
    )
    plt.fill_between(x_final, z_lower_final, z_upper_final, color="#0EBBF0", alpha=0.2)
    ax2a = ax2.twiny()
    ax2a.plot(
        input.hydrodynamic_input.time_steps[:-1], input.hydrodynamic_input.water_levels, linestyle="solid", color="#0D38E0", alpha=0.2
    )
    ax2.fill_between(
        input.dike_schematization.x_positions,
        [min(input.dike_schematization.z_positions) for x in input.dike_schematization.x_positions],
        input.dike_schematization.z_positions,
        color="#FFD814",
        alpha=0.9,
    )
    ax2.plot(
        input.dike_schematization.x_positions,
        input.dike_schematization.z_positions,
        linestyle="solid",
        linewidth=3,
        color="#FF960D",
        marker="o",
    )
    ax2.plot(x_passed, z_passed, linestyle="none", marker="o", color="g")
    ax2.plot(x_failed, z_failed, linestyle="none", marker="x", color="r")

    fig.tight_layout()

    if not os.path.exists(realistic_figures_dir):
        os.mkdir(realistic_figures_dir)
    fig.savefig(os.path.join(realistic_figures_dir, output_file_name + ".png"))


def plot_hydrodynamics(input_measured: DikernelInput, input_filtered: DikernelInput, figure_title: str, output_file_name: str):
    fig = plt.figure(figsize=(10, 4))
    fig.suptitle(figure_title)

    ax1 = plt.subplot(1, 1, 1)
    ax1.grid()
    ax1.set(ylabel="Waterstand [m+NAP]", xlabel="Tijd [s]")

    ax2 = ax1.twiny()
    ax2.set_xticks([])
    ax2.set_xticklabels([])
    ax2.fill_between(
        input_measured.dike_schematization.x_positions,
        [min(input_measured.dike_schematization.z_positions) for x in input_measured.dike_schematization.x_positions],
        input_measured.dike_schematization.z_positions,
        color="#FFD814",
        alpha=0.1,
        zorder=-4,
    )
    ax2.plot(
        input_measured.dike_schematization.x_positions,
        input_measured.dike_schematization.z_positions,
        color="#00B389",
        alpha=0.1,
        linewidth=3,
    )

    ax1.plot(
        input_measured.hydrodynamic_input.time_steps[:-1],
        input_measured.hydrodynamic_input.water_levels,
        label="Waterstand (met seiches)",
        color="#080C80",
    )
    ax1.plot(
        input_filtered.hydrodynamic_input.time_steps[:-1],
        input_filtered.hydrodynamic_input.water_levels,
        label="Waterstand (geen seiches)",
        color="#FF960D",
    )
    ax1.text(
        0.95,
        0.96,
        f"$H_s = { input_measured.hydrodynamic_input.wave_heights[0]:.2f}$",
        transform=ax1.transAxes,
        ha="right",
        va="top",
        color="k",
    )
    ax1.text(
        0.95,
        0.90,
        f"$T_p = { input_measured.hydrodynamic_input.wave_periods[0]:.2f}$",
        transform=ax1.transAxes,
        ha="right",
        va="top",
        color="k",
    )

    y_min = min(min(input_measured.hydrodynamic_input.water_levels), min(input_filtered.hydrodynamic_input.water_levels))
    y_max = max(max(input_measured.hydrodynamic_input.water_levels), max(input_filtered.hydrodynamic_input.water_levels))
    y_margin = (y_max - y_min) * 0.1
    ax1.set_ylim(ymin=y_min - y_margin, ymax=y_max + y_margin)
    ax1.legend(loc="upper left")
    fig.savefig(os.path.join(realistic_figures_dir, output_file_name + ".png"))


for profile in profiles:
    for time_serie in measured_time_series:
        for free_board in [0.2, 0, -0.2]:
            calculation_name = get_calculation_name(profile, time_serie[0], free_board, None)
            figure_title = f"Profiel {profile.value} - {time_serie[0]} ({free_board:.1f} m)"
            print("Plotting: " + calculation_name, end="")
            result_measured = load(
                os.path.join(realistic_output_dir, get_calculation_name(profile, time_serie[0], free_board, True) + ".pyst")
            )
            result_filtered = load(
                os.path.join(realistic_output_dir, get_calculation_name(profile, time_serie[0], free_board, False) + ".pyst")
            )
            plot_run(result_measured[1], result_measured[2], result_filtered[2], output_file_name=calculation_name, fig_title=figure_title)
            plot_hydrodynamics(result_measured[1], result_filtered[1], figure_title, calculation_name + " - hydrodynamics.png")
            plt.close("all")
            print(" - Finished")
