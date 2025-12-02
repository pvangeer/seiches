import os

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
realistic_output_dir = os.path.join(base_output_dir, "realistic")
schematic_output_dir = os.path.join(base_output_dir, "schematic")
os.makedirs(os.path.dirname(realistic_output_dir), exist_ok=True)
os.makedirs(os.path.dirname(schematic_output_dir), exist_ok=True)

base_figures_dir = os.path.join(base_dir_results, "visualization")
realistic_figures_dir = os.path.join(base_figures_dir, "realistic")
schematic_figures_dir = os.path.join(base_figures_dir, "schematic")
os.makedirs(os.path.dirname(realistic_figures_dir), exist_ok=True)
os.makedirs(os.path.dirname(schematic_figures_dir), exist_ok=True)
