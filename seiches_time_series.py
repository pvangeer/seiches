import numpy as np
from datetime import datetime
import os
from data_time_series import *


def __parse_datetime(s):
    return datetime.strptime(s, "%Y-%m-%d %H:%M")


def read_signal_from_file(filename: str) -> MeasuredSurgeSeries:
    if not (os.path.exists(filename)):
        raise ValueError("Specified filename does not exist")

    data = np.genfromtxt(filename, delimiter=",", skip_header=1, converters={0: __parse_datetime}, dtype=None)
    dates = data["f0"]
    t_0 = dates[0]
    elapsed_time = [(d - t_0).total_seconds() for d in dates]
    seiche_signal_raw: list[float] = data["f3"].ravel().tolist()
    water_levels_filtered_raw: list[float] = data["f2"].ravel().tolist()
    water_levels_measured_raw: list[float] = data["f1"].ravel().tolist()
    return MeasuredSurgeSeries(
        times=elapsed_time,
        seiches_signal=[s / 100 for s in seiche_signal_raw],
        water_levels_filtered=[s / 100 for s in water_levels_filtered_raw],
        water_levels_measured=[s / 100 for s in water_levels_measured_raw],
    )


def generate_surge(
    type: SeicheType,
    t_total: float = 54.0,
    a_tide: float = 1.0,
    t_tide: float = 12.0,
    a_nse: float = 0.5,
    dt: float = 0.02,
    a_storm_surge: float = 3.5,
    t_storm_peak: float = 2.0,
    t_storm_duration: float = 44.0,
) -> SurgeSeries:

    times = np.arange(-t_total / 2.0, t_total / 2.0, dt, dtype=float)

    surge_base = times * 0.0
    l_left_mask = (times > -t_storm_duration / 2.0) & (times < -t_storm_peak / 2.0)
    l_right_mask = (times < t_storm_duration / 2.0) & (times > t_storm_peak / 2.0)
    l_peak_mask = (times >= -t_storm_peak / 2.0) & (times <= t_storm_peak / 2.0)
    surge_base[l_left_mask] = (times[l_left_mask] + t_storm_duration / 2.0) / ((t_storm_duration - t_storm_peak) / 2.0)
    surge_base[l_right_mask] = (t_storm_duration / 2.0 - times[l_right_mask]) / ((t_storm_duration - t_storm_peak) / 2.0)
    surge_base[l_peak_mask] = 1

    tide = (a_tide * np.cos(2 * np.pi * times / t_tide)).ravel().tolist()
    surge = (a_storm_surge * surge_base).ravel().tolist()
    nse = (a_nse * surge_base).ravel().tolist()

    period_1 = 90 / 60
    period_2 = 50 / 60
    period_3 = 20 / 60

    match type:
        case SeicheType.NoSeiches:
            return SurgeSeries(
                times=times.tolist(),
                tide=tide,
                surge=surge,
                seiches_signal=(0 * surge_base).ravel().tolist(),
            )
        case SeicheType.Nse:
            return SurgeSeries(
                times=times.tolist(),
                tide=tide,
                surge=surge,
                seiches_signal=nse,
            )
        case SeicheType.BasePeriod:
            return SurgeSeries(
                times=times.tolist(),
                tide=tide,
                surge=surge,
                seiches_signal=(a_nse * np.cos(2 * np.pi * times / period_1) * surge_base).ravel().tolist(),
            )
        case SeicheType.TwoPeaks:
            incr = np.maximum(0, np.minimum(abs(times) / (2 * period_1), 2 - abs(times) / (2 * period_1)))
            return SurgeSeries(
                times=times.tolist(),
                tide=tide,
                surge=surge,
                seiches_signal=(a_nse * (1 + incr) * np.cos(2 * np.pi * times / period_1) * surge_base).ravel().tolist(),
            )
        case SeicheType.LeftPeak:
            incr = np.maximum(0, np.minimum(-times / (2 * period_1), 2 + times / (2 * period_1)))
            return SurgeSeries(
                times=times.tolist(),
                tide=tide,
                surge=surge,
                seiches_signal=(a_nse * (1 + incr) * np.cos(2 * np.pi * times / period_1) * surge_base).ravel().tolist(),
            )
        case SeicheType.RightPeak:
            incr = np.maximum(0, np.minimum(times / (2 * period_1), 2 - times / (2 * period_1)))
            return SurgeSeries(
                times=times.tolist(),
                tide=tide,
                surge=surge,
                seiches_signal=(a_nse * (1 + incr) * np.cos(2 * np.pi * times / period_1) * surge_base).ravel().tolist(),
            )
        case SeicheType.ThreePeriods:
            as_1 = 1 / 2 * a_nse
            as_2 = 1 / 3 * a_nse
            as_3 = 1 / 6 * a_nse
            return SurgeSeries(
                times=times.tolist(),
                tide=tide,
                surge=surge,
                seiches_signal=(
                    (
                        as_1 * np.cos(2 * np.pi * times / period_1)
                        + as_2 * np.cos(2 * np.pi * times / period_2)
                        + as_3 * np.cos(2 * np.pi * times / period_3)
                    )
                    * surge_base
                )
                .ravel()
                .tolist(),
            )
        case _:
            raise ValueError("Unknown surge type")
