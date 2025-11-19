from abc import ABC, abstractmethod
from enum import Enum
from pydantic import BaseModel


class SeicheType(Enum):
    NoSeiches = "No seiches"
    Nse = "Default Nse schematization"
    BasePeriod = "Only base period"
    TwoPeaks = "Only base period, but 50% and 100% increase of 1st and 3rd resp 2nd side wave, on both sides of the peak by increasing the amplitude"
    LeftPeak = "Only increase before storm"
    RightPeak = "Only increase after storm"
    ThreePeriods = "Three periods"
    Measured = "From measurements"


class WaterLevelTimeSeries(BaseModel, ABC):
    times: list[float]

    @property
    @abstractmethod
    def water_levels(self) -> list[float]:
        pass

    def __hash__(self):
        return id(self)

    def __eq__(self, other):
        return self is other


class MeasuredSurgeSeries(WaterLevelTimeSeries):
    filtered: bool = False
    water_levels_measured: list[float]
    water_levels_filtered: list[float]
    seiches_signal: list[float]

    @property
    def water_levels(self) -> list[float]:
        return self.water_levels_filtered if self.filtered else self.water_levels_measured


class SurgeSeries(WaterLevelTimeSeries):
    tide: list[float]
    surge: list[float]
    seiches_signal: list[float]

    @property
    def water_levels(self) -> list[float]:
        return [t + s + se for t, s, se in zip(self.tide, self.surge, self.seiches_signal)]
