import matplotlib

matplotlib.use("Agg")
from pydrever.data import DikernelInput
from pydrever.calculation import Dikernel
from seiches_io import *
from seiches_io_references import *
from seiches_time_series import *
from calculate_utils import (
    profiles,
    schematized_time_series,
    get_schematized_locations,
    get_hydrodynamics,
    get_calculation_name,
)

# save(profiles, os.path.join(base_output_dir, "Profiles.pyst"))
# save(schematized_time_series, os.path.join(base_output_dir, "Schematized_time_series.pyst"))
# save(measured_time_series, os.path.join(base_output_dir, "Measured_time_series.pyst"))


wave_height = 1.8
water_level_increase = 0.0

for pr in profiles:
    profile_name = pr.value
    schematization, nordic_stone_zone, grass_wave_impact_zone, grass_wave_runup_zone, grass_wave_overtopping_zone = (
        get_schematized_locations(pr)
    )
    for time_series in schematized_time_series:
        hydrodynamics = get_hydrodynamics(
            time_series[1], schematization.dike_orientation, max_wave_height=wave_height, water_level_increase=water_level_increase
        )

        input = DikernelInput(dike_schematization=schematization, hydrodynamic_input=hydrodynamics)
        input.output_revetment_zones = [grass_wave_impact_zone, grass_wave_runup_zone, grass_wave_overtopping_zone]
        kernel = Dikernel(input)
        kernel.calculate_locations_parallel = True
        kernel.calculate_time_steps_parallel = True

        calculation_name = get_calculation_name(pr, time_series[0])
        print("Calculating: " + calculation_name, end="")
        success = kernel.run()
        if success:
            save(
                [success, input, kernel.output, kernel.warnings, kernel.errors, water_level_increase],
                os.path.join(schematic_output_dir, calculation_name + ".pyst"),
            )
        print(" - " + ("Success" if success else "Unsuccessful"))
