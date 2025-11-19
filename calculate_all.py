from seiches_io import *
from seiches_io_references import *
from seiches_time_series import *
from data_schematizations import ProfileSchematization
from calculate_utils import read_schematization, read_measured_time_series
from calculate_asphalt import perform_asphalt_calculation_schematic, perform_asphalt_calculations_measured
from calculate_grass_wave_impact import perform_grass_wave_impact_calculation_schematic, perform_grass_wave_impact_calculations_measured
from calculate_grass_wave_runup import perform_grass_wave_runup_calculation_schematic, perform_grass_wave_runup_calculations_measured
from calculate_grass_wave_overtopping import (
    perform_grass_wave_overtopping_calculation_schematic,
    perform_grass_wave_overtopping_calculations_measured,
)

profiles = [ProfileSchematization.A, ProfileSchematization.B, ProfileSchematization.C]


schematized_time_series = [
    ["Geen seiches", generate_surge(SeicheType.NoSeiches)],
    ["NSE", generate_surge(SeicheType.Nse)],
    ["Scenario 1 (Basis periode)", generate_surge(SeicheType.BasePeriod)],
    ["Scenario 2 (Twee pieken)", generate_surge(SeicheType.TwoPeaks)],
    ["Scenario 3 (Piek links)", generate_surge(SeicheType.LeftPeak)],
    ["Scenario 4 (Piek rechts)", generate_surge(SeicheType.RightPeak)],
    ["Scenario 5 (Drie periodes)", generate_surge(SeicheType.ThreePeriods)],
]


measured_time_series = [
    ["Tijdserie 1", read_measured_time_series("1")],
    ["Tijdserie 2", read_measured_time_series("2")],
    ["Tijdserie 3", read_measured_time_series("3")],
    ["Tijdserie 4", read_measured_time_series("4")],
    ["Tijdserie 5", read_measured_time_series("5")],
    ["Tijdserie 6", read_measured_time_series("6")],
    ["Tijdserie 7", read_measured_time_series("7")],
    ["Tijdserie 8", read_measured_time_series("8")],
    ["Tijdserie 9", read_measured_time_series("9")],
    ["Tijdserie 10", read_measured_time_series("10")],
]

# save(profiles, os.path.join(output_base_dir, "Profiles.pyst"))
# save(schematized_time_series, os.path.join(base_output_dir, "Schematized_time_series.pyst"))
save(measured_time_series, os.path.join(base_output_dir, "Measured_time_series.pyst"))

for pr in profiles:
    profile_name = pr.value
    profile = read_schematization(pr)
    for s in schematized_time_series:
        perform_asphalt_calculation_schematic(profile_name, profile, s[0], s[1])
    #     perform_grass_wave_impact_calculation_schematic(profile_name, profile, s[0], s[1])
    #     perform_grass_wave_runup_calculation_schematic(profile_name, profile, s[0], s[1])
    #     perform_grass_wave_overtopping_calculation_schematic(profile_name, profile, s[0], s[1])

    for m in measured_time_series:
        perform_asphalt_calculations_measured(profile_name, profile, m[0], m[1])
        # perform_grass_wave_impact_calculations_measured(profile_name, profile, m[0], m[1])
        # perform_grass_wave_runup_calculations_measured(profile_name, profile, m[0], m[1])
        # perform_grass_wave_overtopping_calculations_measured(profile_name, profile, m[0], m[1])
