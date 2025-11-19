from seiches_time_series import *


def test_generage_surge():
    time_series = generate_surge(type=SeicheType.BasePeriod)
    time_series = generate_surge(type=SeicheType.LeftPeak)
    time_series = generate_surge(type=SeicheType.RightPeak)
    time_series = generate_surge(type=SeicheType.TwoPeaks)
    time_series = generate_surge(type=SeicheType.ThreePeriods)


def test_read_series_works():
    series = read_signal_from_file(
        "N:/Projects/11211500/11211573/B. Measurements and calculations/001 HB - seiches/Tijdreeksen/Gemeten/seiche_peak_1_timeseries.txt"
    )

    print(series.water_levels)
