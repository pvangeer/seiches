import matplotlib

matplotlib.use("Agg")
from pathlib import Path
from pydrever.data import DikernelInput
from pydrever.calculation import Dikernel
from seiches_io_references import *
from seiches_io import *
from calculate_utils import (
    profiles,
    measured_time_series,
    get_calculation_name,
    get_hydrodynamics,
    get_schematized_locations,
)

wave_height = 0.8

for sch in profiles:
    schematization, nordic_stone_zone, grass_wave_impact_zone, grass_wave_runup_zone, grass_wave_overtopping_zone = (
        get_schematized_locations(sch)
    )
    for time_series in measured_time_series:
        for free_board in [0.2, 0, -0.2]:
            time_series[1].filtered = False

            water_level_increase = max(schematization.z_positions) - free_board - max(time_series[1].water_levels_filtered)
            hydrodynamics = get_hydrodynamics(
                time_series[1], schematization.dike_orientation, max_wave_height=wave_height, water_level_increase=water_level_increase
            )

            input = DikernelInput(dike_schematization=schematization, hydrodynamic_input=hydrodynamics)
            input.output_revetment_zones = [grass_wave_impact_zone, grass_wave_runup_zone, grass_wave_overtopping_zone]
            kernel = Dikernel(input)
            kernel.calculate_locations_parallel = True
            kernel.calculate_time_steps_parallel = True

            calculation_name = get_calculation_name(sch, time_series[0], free_board, True)
            print("Calculating: " + calculation_name, end="")
            success = kernel.run()
            if success:
                path = Path(realistic_output_dir)
                path.parent.mkdir(parents=True, exist_ok=True)
                save(
                    [success, input, kernel.output, kernel.warnings, kernel.errors, water_level_increase],
                    os.path.join(realistic_output_dir, calculation_name + ".pyst"),
                )
            print(" - " + ("Success" if success else "Unsuccessful"))

            time_series[1].filtered = True
            hydrodynamics = get_hydrodynamics(
                time_series[1], schematization.dike_orientation, max_wave_height=wave_height, water_level_increase=water_level_increase
            )

            input = DikernelInput(dike_schematization=schematization, hydrodynamic_input=hydrodynamics)
            input.output_revetment_zones = [grass_wave_impact_zone, grass_wave_runup_zone, grass_wave_overtopping_zone]
            kernel = Dikernel(input)
            kernel.calculate_locations_parallel = True
            kernel.calculate_time_steps_parallel = True

            calculation_name = get_calculation_name(sch, time_series[0], free_board, False)
            print("Calculating: " + calculation_name, end="")
            success = kernel.run()
            if success:
                path = Path(realistic_output_dir)
                path.parent.mkdir(parents=True, exist_ok=True)
                save(
                    [success, input, kernel.output, kernel.warnings, kernel.errors, water_level_increase],
                    os.path.join(realistic_output_dir, calculation_name + ".pyst"),
                )

            print(" - " + ("Success" if success else "Unsuccessful"))
