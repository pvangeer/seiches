from pydrever.data import VerticalRevetmentZoneDefinition, DikeSchematization


class CustomVerticalRevetmentZoneDefinition(VerticalRevetmentZoneDefinition):
    x_min: float | None
    """The minimum distance of this revetment zone."""
    x_max: float | None
    """The maximum distance of this revetment zone."""

    def get_x_coordinates(self, dike_schematizaion: DikeSchematization, inner_slope: bool = False):
        x_coordinates = super().get_x_coordinates(dike_schematizaion, inner_slope)
        return [x for x in x_coordinates if x > self.x_min and x < self.x_max]
