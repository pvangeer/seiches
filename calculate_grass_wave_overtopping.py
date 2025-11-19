from seiches_time_series import WaterLevelTimeSeries, MeasuredSurgeSeries
from pydrever.data import DikernelInput, GrassOvertoppingLayerSpecification, TopLayerType, DikeSchematization
from pydrever.calculation import Dikernel
from calculate_utils import *
from seiches_io_references import *


def add_output_locations(input: DikernelInput):
    x_locations = np.arange(input.dike_schematization.x_outer_toe, input.dike_schematization.x_outer_crest, 1.0).tolist()
    x_locations[0] = x_locations[0] + 0.1
    x_locations[-1] = x_locations[-1] - 0.1

    if input.dike_schematization.x_inner_crest is not None and input.dike_schematization.x_inner_toe is not None:
        input.add_output_location(
            x_location=(input.dike_schematization.x_inner_crest + input.dike_schematization.x_inner_toe) / 2.0,
            top_layer_specification=GrassOvertoppingLayerSpecification(top_layer_type=TopLayerType.GrassClosedSod),
        )


def calculate_scenario(schematization: DikeSchematization, time_series: WaterLevelTimeSeries):
    hydrodynamics = get_hydrodynamics(time_series, schematization.dike_orientation)

    input = DikernelInput(dike_schematization=schematization, hydrodynamic_input=hydrodynamics)
    add_output_locations(input)
    kernel = Dikernel(input)
    kernel.calculate_locations_parallel = True
    kernel.calculate_time_steps_parallel = True
    runresult = kernel.run()

    return [runresult, input, kernel.output, kernel.warnings, kernel.errors]


def perform_grass_wave_overtopping_calculation_schematic(
    profile_name: str, profile: DikeSchematization, time_series_name: str, time_series: WaterLevelTimeSeries
):
    calculation_name = "profile " + profile_name + " - wave_overtopping - " + time_series_name

    print("Calculating: " + calculation_name, end="")
    result = calculate_scenario(profile, time_series)
    print(" - " + "Success" if result[0] else "Unsuccessful")

    if result[0]:
        store_results(result, calculation_name + ".pyst", grass_wave_overtopping_output_dir)


def perform_grass_wave_overtopping_calculations_measured(
    profile_name: str, profile: DikeSchematization, time_series_name: str, time_series: MeasuredSurgeSeries
):
    calculation_name = "profile " + profile_name + " - wave_overtopping - " + time_series_name + " - gemeten"

    print("Calculating: " + calculation_name, end="")
    time_series.filtered = False
    result = calculate_scenario(profile, time_series)
    print(" - " + "Success" if result[0] else "Unsuccessful")

    if result[0]:
        store_results(result, calculation_name + ".pyst", grass_wave_overtopping_output_dir)

    calculation_name = "profile " + profile_name + " - wave_overtopping - " + time_series_name + " - gefilterd"

    print("Calculating: " + calculation_name, end="")
    time_series.filtered = True
    result = calculate_scenario(profile, time_series)
    print(" - " + "Success" if result[0] else "Unsuccessful")

    if result[0]:
        store_results(result, calculation_name + ".pyst", grass_wave_overtopping_output_dir)
