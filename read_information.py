import numpy as np
from seiches_time_series import MeasuredSurgeSeries, read_signal_from_file
from seiches_io import *
from seiches_io_references import *
from pydrever.io import prflreader
from pydrever.data import HydrodynamicConditions


def read_schematization(filename):

    schematization = prflreader.read(os.path.join(profiles_dir, filename))
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


def get_hydrodynamics(series, dike_orientation):
    water_levels = series.water_levels[:-1]
    wave_heights = len(water_levels) * [1.3]
    wave_periods = len(water_levels) * [6.5]
    wave_directions = np.full(len(water_levels), dike_orientation)

    return HydrodynamicConditions(
        time_steps=series.times,
        water_levels=water_levels,
        wave_heights=wave_heights,
        wave_periods=wave_periods,
        wave_directions=wave_directions,
    )
