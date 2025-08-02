from enum import Enum


BASE_URL = "https://geo.irceline.be/sos/api/v1"
POLLUTANTS = {  # Based on https://geo.irceline.be/sos/api/v1/phenomena
    "pm10": "5",
    "ppm25": "6001",
    "no2": "8",
    "co2": "71",
    "so2": "1",
}
AGGREGATION_FUNCTIONS = {
    "mean": "mean",
    "max": "max",
    "min": "min",
}
MAX_DAYS = 31
TOP_NB_POLLUTED_CITIES = 10


class ViewMode(str, Enum):
    TOP_POLLUTING_CITIES = "Top Polluting Cities"
    HOURLY_VIEW = "Hourly View"
    STATION_OVERVIEW = "Station Overview"
