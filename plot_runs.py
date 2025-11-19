import os
from seiches_io import load
from seiches_io_references import *
from data_calculation import *
import matplotlib.pyplot as plt
from pydrever.visualization import plot_damage_levels, plot_hydrodynamic_conditions


def __get_output_dir(calc_type: CalculationType) -> str:
    match calc_type:
        case CalculationType.Asphalt:
            return asphalt_output_dir
        case CalculationType.GrassWaveImpact:
            return grass_wave_impact_output_dir
        case CalculationType.GrassWaveRunup:
            return grass_wave_runup_output_dir
        case CalculationType.GrassWaveImpact:
            return grass_wave_overtopping_output_dir
    return base_output_dir


def __get_correct_figures_dir(calc_type: CalculationType) -> str:
    match calc_type:
        case CalculationType.Asphalt:
            return asphalt_figures_dir
        case CalculationType.GrassWaveImpact:
            return grass_wave_impact_figures_dir
        case CalculationType.GrassWaveRunup:
            return grass_wave_runup_figures_dir
        case CalculationType.GrassWaveImpact:
            return grass_wave_overtopping_figures_dir
    return base_figures_dir


def plot_run(profile: str, time_series: str, calc_type: CalculationType, measured: bool | None = None):
    calc_type_name = calc_type.value.replace("grass_", "")
    output_file_name = "profile " + profile + " - " + calc_type_name + " - " + time_series
    if measured is not None:
        output_file_name = output_file_name + (" - gefilterd" if not measured else " - gemeten")

    result = load(os.path.join(__get_output_dir(calc_type), output_file_name + ".pyst"))

    if not result[0]:
        for m in result[4]:
            print("\033[31m" + m + "\033[0m")
        return

    fig = plot_damage_levels(result[2], result[1], plot_development=True, plot_reference=False)
    output_figure_dir = __get_correct_figures_dir(calc_type)
    if not os.path.exists(output_figure_dir):
        os.mkdir(output_figure_dir)
    fig.savefig(os.path.join(output_figure_dir, output_file_name + ".png"))

    hfig = plot_hydrodynamic_conditions(result[1])
    hfig.savefig(os.path.join(output_figure_dir, output_file_name + "-hydro" + ".png"))
    plt.close("all")


profiles = [
    "A",
    # "B",
    # "C"
]

time_series = [
    "Geen seiches",
    "NSE",
    "Scenario 1 (Basis periode)",
    "Scenario 2 (Twee pieken)",
    "Scenario 3 (Piek links)",
    "Scenario 4 (Piek rechts)",
    "Scenario 5 (Drie periodes)",
    "Tijdserie 1",
    "Tijdserie 2",
    "Tijdserie 3",
    "Tijdserie 4",
    "Tijdserie 5",
    "Tijdserie 6",
    "Tijdserie 7",
    "Tijdserie 8",
    "Tijdserie 9",
    "Tijdserie 10",
]

calc_types = [
    CalculationType.Asphalt,
    # CalculationType.GrassWaveImpact,
    # CalculationType.GrassWaveRunup,
    # CalculationType.GrassWaveOvertopping,
]

for profile in profiles:
    for time_serie in time_series:
        for calc_type in calc_types:
            if time_serie.startswith("Tijdserie"):
                plot_run(profile, time_serie, calc_type, True)
                plot_run(profile, time_serie, calc_type, False)
            else:
                plot_run(profile, time_serie, calc_type, None)
