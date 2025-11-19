from enum import Enum


class ProfileSchematization(Enum):
    A = "A"
    B = "B"
    C = "C"

    def get_file_name(self):
        return "Locatie" + self.value + "_AHN.prfl"
