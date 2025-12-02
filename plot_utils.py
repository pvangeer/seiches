from calculate_utils import find_horizontal_intersections
from collections import defaultdict


def find_patch(x_positions: list[float], z_positions: list[float], h_max: float, h_min: float):
    x = [x for x in x_positions]
    z_upper = [h_max if z <= h_max else z for z in z_positions]
    z_lower = [h_min if z <= h_min else z for z in z_positions]

    x_z_max_intersections = find_horizontal_intersections(x_positions, z_positions, h_max)
    x_z_min_intersections = find_horizontal_intersections(x_positions, z_positions, h_min)

    x_all = x
    x_all.extend(x_z_min_intersections)
    x_all.extend(x_z_max_intersections)
    z_min_all = z_lower
    z_min_all.extend([h_min for z in x_z_min_intersections])
    z_min_all.extend([h_max for z in x_z_max_intersections])
    z_max_all = z_upper
    z_max_all.extend([h_max for z in x_z_min_intersections])
    z_max_all.extend([h_max for z in x_z_max_intersections])

    z_min_dict = defaultdict(list)
    z_max_dict = defaultdict(list)
    for x, z_min, z_max in zip(x_all, z_min_all, z_max_all):
        z_min_dict[x].append(z_min)
        z_max_dict[x].append(z_max)

    x_final = sorted(set(x_all))
    z_lower_final = [z_min_dict[x][0] for x in x_final]
    z_upper_final = [z_max_dict[x][0] for x in x_final]

    return x_final, z_lower_final, z_upper_final
