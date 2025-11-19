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
):
    output_measured = result_measured
    output_filtered = result_filtered

    fig = plt.figure(figsize=(8, 10))
    fig.suptitle(output_file_name)

    ax1 = plt.subplot(4, 1, 1)
    ax1.grid()
    ax1.set(ylabel="Damage level [-]")
    ax1.set_title("Golfklap")

    x_outer_crest = input.dike_schematization.x_outer_crest
    output_impact_measured = [o for o in output_measured if isinstance(o, GrassWaveImpactOutputLocation) and o.x_position < x_outer_crest]
    x_locations_impact_measured = [l.x_position for l in output_impact_measured]
    output_impact_filtered = [o for o in output_filtered if isinstance(o, GrassWaveImpactOutputLocation) and o.x_position < x_outer_crest]
    x_locations_impact_filtered = [l.x_position for l in output_impact_filtered]

    plt.axhline(1.0, color="red", linewidth=2.0, linestyle="--")
    ax1.plot(
        x_locations_impact_measured,
        list(loc.final_damage for loc in output_impact_measured),
        linestyle="-",
        marker="o",
        color="green",
        label="Met seiches",
    )
    ax1.plot(
        x_locations_impact_filtered,
        list(loc.final_damage for loc in output_impact_filtered),
        linestyle="-",
        marker="o",
        color="orange",
        label="Zonder seiches",
    )

    ax2 = plt.subplot(4, 1, 2, sharex=ax1)
    ax2.grid()
    ax2.set(ylabel="Damage level [-]")
    ax2.set_title("Golfoploop")

    output_runup_measured = [
        o for o in output_measured if isinstance(o, GrassCumulativeOverloadOutputLocation) and o.x_position < x_outer_crest
    ]
    x_locations_runup_measured = [l.x_position for l in output_runup_measured]
    output_runup_filtered = [
        o for o in output_filtered if isinstance(o, GrassCumulativeOverloadOutputLocation) and o.x_position < x_outer_crest
    ]
    x_locations_runup_filtered = [l.x_position for l in output_runup_filtered]

    plt.axhline(1.0, color="red", linewidth=2.0, linestyle="--")

    ax2.plot(
        x_locations_runup_measured,
        list(loc.final_damage for loc in output_runup_measured),
        linestyle="-",
        marker="o",
        color="green",
        label="Met seiches",
    )
    ax2.plot(
        x_locations_runup_filtered,
        list(loc.final_damage for loc in output_runup_filtered),
        linestyle="-",
        marker="o",
        color="orange",
        label="Zonder seiches",
    )

    ax3 = plt.subplot(4, 1, 3, sharex=ax1)
    ax3.grid()
    ax3.set(ylabel="Damage level [-]")
    ax3.set_title("Overloop / overslag")
    plt.axhline(1.0, color="red", linewidth=2.0, linestyle="--")
    output_overtopping_measured = [o for o in result_measured if o.x_position >= x_outer_crest]
    output_overtopping_filtered = [o for o in result_filtered if o.x_position >= x_outer_crest]
    ax3.plot(
        [o.x_position for o in output_overtopping_measured],
        [o.final_damage for o in output_overtopping_measured],
        linestyle="-",
        marker="o",
        color="green",
        label="Met seiches",
    )
    ax3.plot(
        [o.x_position for o in output_overtopping_filtered],
        [o.final_damage for o in output_overtopping_filtered],
        linestyle="-",
        marker="o",
        color="orange",
        label="Zonder seiches",
    )

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

    ax4 = plt.subplot(4, 1, 4, sharex=ax1)
    ax4.grid()
    ax4.set(ylabel="Height [m]", xlabel="Cross-shore position [x]")

    h_max = max(input.hydrodynamic_input.water_levels)
    h_min = min(input.hydrodynamic_input.water_levels)
    x_final, z_lower_final, z_upper_final = find_patch(
        x_positions=input.dike_schematization.x_positions, z_positions=input.dike_schematization.z_positions, h_min=h_min, h_max=h_max
    )
    plt.fill_between(x_final, z_lower_final, z_upper_final, color="blue", alpha=0.5)
    ax4.plot(
        input.dike_schematization.x_positions,
        input.dike_schematization.z_positions,
        linestyle="solid",
        color="black",
        marker="o",
    )
    ax4.plot(x_passed, z_passed, linestyle="none", marker="o", color="g")
    ax4.plot(x_failed, z_failed, linestyle="none", marker="x", color="r")

    fig.tight_layout()

    if not os.path.exists(realistic_figures_dir):
        os.mkdir(realistic_figures_dir)
    fig.savefig(os.path.join(realistic_figures_dir, output_file_name + ".png"))


def plot_hydrodynamics(input, output_file_name):
    hfig = plot_hydrodynamic_conditions(input)
    hfig.savefig(os.path.join(realistic_figures_dir, output_file_name + "-hydro" + ".png"))
    plt.close("all")


for profile in profiles:
    for time_serie in measured_time_series:
        for free_board in [0.2, 0, -0.2]:
            calculation_name = get_calculation_name(profile, time_serie[0], free_board, None)
            print("Plotting: " + calculation_name, end="")
            result_measured = load(
                os.path.join(realistic_output_dir, get_calculation_name(profile, time_serie[0], free_board, True) + ".pyst")
            )
            result_filtered = load(
                os.path.join(realistic_output_dir, get_calculation_name(profile, time_serie[0], free_board, False) + ".pyst")
            )
            plot_run(result_measured[1], result_measured[2], result_filtered[2], output_file_name=calculation_name)
            plot_hydrodynamics(result_filtered[1], calculation_name + " - filtered - hydrodynamics.png")
            plot_hydrodynamics(result_measured[1], calculation_name + " - measured - hydrodynamics.png")
            print(" - Finished")
