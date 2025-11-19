import os
from data_calculation import CalculationType

# analysis
#   - data
#   - results
#       - output
#           - asphalt
#           - grass_wave_impact
#           - grass_wave_overtopping
#           - grass_wave_runup
#           - realistic
#       - visualization
#           - asphalt
#           - grass_wave_impact
#           - grass_wave_overtopping
#           - grass_wave_runup
#           - realistic

base_dir_code = "C:\\src\\seiches"
base_dir_results = "C:\\Pieter\\Projecten\\BOI-Seiches"

profiles_dir = os.path.join(base_dir_code, "data")
time_series_dir = profiles_dir

base_output_dir = os.path.join(base_dir_results, "output")
asphalt_output_dir = os.path.join(base_output_dir, CalculationType.Asphalt.value)
grass_wave_impact_output_dir = os.path.join(base_output_dir, CalculationType.GrassWaveImpact.value)
grass_wave_overtopping_output_dir = os.path.join(base_output_dir, CalculationType.GrassWaveOvertopping.value)
grass_wave_runup_output_dir = os.path.join(base_output_dir, CalculationType.GrassWaveRunup.value)
realistic_output_dir = os.path.join(base_output_dir, "realistic")

base_figures_dir = os.path.join(base_dir_results, "visualization")
asphalt_figures_dir = os.path.join(base_figures_dir, CalculationType.Asphalt.value)
grass_wave_impact_figures_dir = os.path.join(base_figures_dir, CalculationType.GrassWaveImpact.value)
grass_wave_overtopping_figures_dir = os.path.join(base_figures_dir, CalculationType.GrassWaveOvertopping.value)
grass_wave_runup_figures_dir = os.path.join(base_figures_dir, CalculationType.GrassWaveRunup.value)
realistic_figures_dir = os.path.join(base_figures_dir, "realistic")
