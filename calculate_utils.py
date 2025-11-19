import os
from pathlib import Path
import numpy as np
from pydrever.data import (
    HydrodynamicConditions,
    DikeSchematization,
)
from pydrever.io import prflreader
from data_schematizations import ProfileSchematization
from data_calculation import CustomVerticalRevetmentZoneDefinition
from seiches_io import *
from seiches_io_references import *
from data_time_series import WaterLevelTimeSeries, MeasuredSurgeSeries
from seiches_time_series import read_signal_from_file
from pydrever.data import (
    RevetmentZoneSpecification,
    HorizontalRevetmentZoneDefinition,
    NordicStoneLayerSpecification,
    GrassWaveImpactLayerSpecification,
    GrassWaveRunupLayerSpecification,
    GrassOvertoppingLayerSpecification,
    OutputLocationSpecification,
    TopLayerType,
    DikeSchematization,
)


def get_calculation_name(sch: ProfileSchematization, time_series_name, free_board: float, measured: bool | None):
    base_calculation_name = "Profile " + sch.value + " - " + time_series_name + " - " + format(free_board, ".1f")
    if measured is not None:
        return base_calculation_name + " - " + ("gemeten" if measured else "gefilterd")

    return base_calculation_name


def read_schematization(filename: ProfileSchematization) -> DikeSchematization:

    schematization = prflreader.read(os.path.join(profiles_dir, filename.get_file_name()))
    schematization.foreshore_slope = 0.01
    schematization.z_bottom = min(schematization.z_positions) - 0.1

    if schematization.x_inner_crest is None:
        x_inner_crest = max(schematization.x_positions) + 10
        z_inner_crest = schematization.z_positions[-1]

        schematization.x_inner_crest = x_inner_crest
        schematization.x_inner_toe = x_inner_crest + 15

        schematization.x_positions.append(x_inner_crest)
        schematization.x_positions.append(schematization.x_inner_toe)
        schematization.z_positions.append(z_inner_crest)
        schematization.z_positions.append(z_inner_crest - 5)
        schematization.roughnesses.append(schematization.roughnesses[-1])
        schematization.roughnesses.append(schematization.roughnesses[-1])

    return schematization


def read_measured_time_series(number: str) -> MeasuredSurgeSeries:
    return read_signal_from_file(os.path.join(time_series_dir, "seiche_peak_" + number + "_timeseries.txt"))


def __get_wave_period(wave_height: float, wave_steepness: float = 0.08) -> float:
    wave_length = wave_height / wave_steepness
    wave_period = np.sqrt(wave_length * 2.0 * np.pi / 9.81)
    return wave_period


def get_hydrodynamics(
    series: WaterLevelTimeSeries,
    dike_orientation,
    water_level_increase: float = 0.0,
    max_wave_height: float = 1.3,
    min_wave_height: float = 0.3,
):
    water_levels = [w + water_level_increase for w in series.water_levels[:-1]]
    wave_heights = [max_wave_height for h in water_levels]
    # min_water_level = min(water_levels)
    # max_water_level = max(water_levels)
    # wave_heights = [
    #     min_wave_height + (v - min_water_level) / (max_water_level - min_water_level) * (max_wave_height - min_wave_height)
    #     for v in water_levels
    # ]
    wave_periods = [__get_wave_period(hs) for hs in wave_heights]
    wave_directions = np.full(len(water_levels), dike_orientation)

    return HydrodynamicConditions(
        time_steps=series.times,
        water_levels=water_levels,
        wave_heights=wave_heights,
        wave_periods=wave_periods,
        wave_directions=wave_directions,
    )


def get_outer_slope(dike_schematization: DikeSchematization):
    if dike_schematization.x_outer_crest is None:
        return 0.3

    i_outer_crest = dike_schematization.x_positions.index(dike_schematization.x_outer_crest)
    if i_outer_crest == 0 or i_outer_crest == len(dike_schematization.x_positions):
        return 0.3

    x2 = dike_schematization.x_outer_crest
    x1 = dike_schematization.x_positions[i_outer_crest - 1]
    z2 = dike_schematization.z_positions[i_outer_crest]
    z1 = dike_schematization.z_positions[i_outer_crest - 1]

    return (z2 - z1) / (x2 - x1)


z_grass_zones = {ProfileSchematization.A: 5.2, ProfileSchematization.B: 3.1, ProfileSchematization.C: 3.4}


def get_overtopping_output_location(profile: DikeSchematization):
    if profile.x_inner_crest is None or profile.x_inner_toe is None:
        raise Exception()

    return OutputLocationSpecification(
        x_position=(profile.x_inner_crest + profile.x_inner_toe) / 2.0,
        top_layer_specification=GrassOvertoppingLayerSpecification(top_layer_type=TopLayerType.GrassClosedSod),
    )


def get_schematized_locations(seiche_profile: ProfileSchematization, n_grass_locations: int = 10, n_stone_locations: int = 10):
    profile = read_schematization(seiche_profile)

    nordic_stone_zone_definition = CustomVerticalRevetmentZoneDefinition(
        z_min=min(profile.z_positions),
        z_max=z_grass_zones[seiche_profile],
        nz=n_stone_locations,
        x_min=profile.x_outer_toe,
        x_max=profile.x_outer_crest,
        include_schematization_coordinates=True,
    )
    grass_zone_definition = CustomVerticalRevetmentZoneDefinition(
        z_min=z_grass_zones[seiche_profile],
        z_max=max(profile.z_positions),
        nz=n_grass_locations,
        x_min=profile.x_outer_toe,
        x_max=profile.x_outer_crest,
        include_schematization_coordinates=True,
    )
    grass_wave_overtopping_zone_definition = HorizontalRevetmentZoneDefinition(
        x_min=profile.x_outer_crest + 0.01,
        x_max=profile.x_inner_toe - 0.01 if profile.x_inner_toe is not None else max(profile.x_positions),
        nx=5,
        include_schematization_coordinates=True,
    )

    nordic_stone_zone = RevetmentZoneSpecification(
        zone_definition=nordic_stone_zone_definition,
        top_layer_specification=NordicStoneLayerSpecification(
            top_layer_type=TopLayerType.NordicStone, top_layer_thickness=0.44, relative_density=2.707
        ),
    )
    grass_wave_impact_zone = RevetmentZoneSpecification(
        zone_definition=grass_zone_definition,
        top_layer_specification=GrassWaveImpactLayerSpecification(top_layer_type=TopLayerType.GrassClosedSod),
    )
    grass_wave_runup_zone = RevetmentZoneSpecification(
        zone_definition=grass_zone_definition,
        top_layer_specification=GrassWaveRunupLayerSpecification(
            top_layer_type=TopLayerType.GrassClosedSod, outer_slope=get_outer_slope(profile)
        ),
    )
    grass_wave_overtopping_zone = RevetmentZoneSpecification(
        zone_definition=grass_wave_overtopping_zone_definition,
        top_layer_specification=GrassOvertoppingLayerSpecification(top_layer_type=TopLayerType.GrassClosedSod),
    )

    return profile, nordic_stone_zone, grass_wave_impact_zone, grass_wave_runup_zone, grass_wave_overtopping_zone


def store_results(results, file_name, base_output_path):
    output_file_path = os.path.join(base_output_path, file_name)
    path = Path(output_file_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    save(results, output_file_path)


def find_horizontal_intersections(x: list[float], z: list[float], z_ref: float) -> list[float]:
    """
    Find all x positions where the line defined by (x, z) crosses z_ref.

    Parameters:
        x (List[float]): x-coordinates of the line
        z (List[float]): z-coordinates of the line
        z_ref (float): horizontal reference level to intersect

    Returns:
        List[float]: x-coordinates of intersections
    """
    if len(x) != len(z):
        raise ValueError("x and z must have the same length")

    intersections = []

    for i in range(len(x) - 1):
        z0, z1 = z[i], z[i + 1]
        x0, x1 = x[i], x[i + 1]

        # Check if z_ref is between z0 and z1 (including equality)
        if (z0 - z_ref) * (z1 - z_ref) <= 0:
            # Avoid division by zero for flat segments exactly at z_ref
            if z1 != z0:
                x_int = x0 + (x1 - x0) * (z_ref - z0) / (z1 - z0)
            else:
                # If z0 == z1 == z_ref, take midpoint
                x_int = (x0 + x1) / 2
            intersections.append(x_int)

    return intersections


measured_time_series = [
    # ["Tijdserie 1", read_measured_time_series("1")],
    # ["Tijdserie 2", read_measured_time_series("2")],
    # ["Tijdserie 3", read_measured_time_series("3")],
    # ["Tijdserie 4", read_measured_time_series("4")],
    ["Tijdserie 5", read_measured_time_series("5")],
    ["Tijdserie 6", read_measured_time_series("6")],
    # ["Tijdserie 7", read_measured_time_series("7")],
    ["Tijdserie 8", read_measured_time_series("8")],
    ["Tijdserie 9", read_measured_time_series("9")],
    ["Tijdserie 10", read_measured_time_series("10")],
]

profiles = [ProfileSchematization.A, ProfileSchematization.B, ProfileSchematization.C]
