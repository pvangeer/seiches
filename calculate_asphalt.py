from data_time_series import WaterLevelTimeSeries, MeasuredSurgeSeries
from pydrever.data import DikernelInput, AsphaltLayerSpecification, TopLayerType, DikeSchematization
from pydrever.calculation import Dikernel
from calculate_utils import *
from seiches_io_references import *


def add_output_locations(input: DikernelInput):
    x_locations = np.arange(input.dike_schematization.x_outer_toe, input.dike_schematization.x_outer_crest, 1.0).tolist()
    x_locations[0] = x_locations[0] + 0.1
    x_locations[-1] = x_locations[-1] - 0.1

    for x_location in x_locations:
        input.add_output_location(
            x_location=x_location,
            top_layer_specification=AsphaltLayerSpecification(
                top_layer_type=TopLayerType.Asphalt,
                flexural_strength=0.9,
                soil_elasticity=64.0,
                upper_layer_thickness=0.10,
                upper_layer_elasticity_modulus=5712.0,
            ),
        )


def calculate_scenario(
    schematization: DikeSchematization,
    time_series: WaterLevelTimeSeries,
    max_wave_height: float,
    limited_output: bool = False,
):
    hydrodynamics = get_hydrodynamics(time_series, schematization.dike_orientation, max_wave_height)

    input = DikernelInput(dike_schematization=schematization, hydrodynamic_input=hydrodynamics)
    if limited_output:
        input.output_time_steps = np.linspace(min(time_series.times), max(time_series.times), 25)
    add_output_locations(input)
    kernel = Dikernel(input)
    kernel.calculate_locations_parallel = True
    kernel.calculate_time_steps_parallel = True
    runresult = kernel.run()

    return [runresult, input, kernel.output, kernel.warnings, kernel.errors]


def perform_asphalt_calculation_schematic(
    profile_name: str, profile: DikeSchematization, time_series_name: str, time_series: WaterLevelTimeSeries
):
    calculation_name = "profile " + profile_name + " - asphalt - " + time_series_name
    print("Calculating: " + calculation_name, end="")
    result = calculate_scenario(profile, time_series, 1.3)
    print(" - " + "Success" if result[0] else "Unsuccessful")
    if result[0]:
        store_results(result, calculation_name + ".pyst", asphalt_output_dir)


def perform_asphalt_calculations_measured(
    profile_name: str, profile: DikeSchematization, time_series_name: str, time_series: MeasuredSurgeSeries
):
    calculation_name = "profile " + profile_name + " - asphalt - " + time_series_name + " - gemeten"
    print("Calculating: " + calculation_name, end="")
    time_series.filtered = False
    result = calculate_scenario(profile, time_series, 0.7, True)
    print(" - " + "Success" if result[0] else "Unsuccessful")
    if result[0]:
        store_results(result, calculation_name + ".pyst", asphalt_output_dir)

    calculation_name = "profile " + profile_name + " - asphalt - " + time_series_name + " - gefilterd"
    print("Calculating: " + calculation_name, end="")
    time_series.filtered = True
    result = calculate_scenario(profile, time_series, 0.7, True)
    print(" - " + "Success" if result[0] else "Unsuccessful")
    if result[0]:
        store_results(result, calculation_name + ".pyst", asphalt_output_dir)
