import streamlit as st
import pandas as pd
import requests
from datetime import datetime, UTC
from typing import Dict, List
import geopandas as gpd
from shapely.geometry import Point

from config import BASE_URL, POLLUTANTS


def fetch_url(url: str) -> List[Dict]:
    response = requests.get(url)
    response.raise_for_status()
    return response.json()


@st.cache_data
def load_region_geometry(include_brussels: bool = True) -> gpd.GeoDataFrame:
    regions_to_include = ["vlaams gewest"]
    if include_brussels:
        regions_to_include.append("brussels hoofdstedelijk gewest")

    regions_gdf = gpd.read_file("data/regionsgeweste-belgium.geojson")[
        ["geometry", "reg_name_lower_nl"]
    ]
    return regions_gdf[regions_gdf["reg_name_lower_nl"].isin(regions_to_include)]


@st.cache_data
def fetch_stations() -> List[Dict]:
    url = f"{BASE_URL}/stations"
    return fetch_url(url)


def fetch_station_timeseries(station_id: str) -> List[Dict]:
    url = f"{BASE_URL}/stations/{station_id}"
    return fetch_url(url)


def fetch_timeseries_data(timeseries_id: str, start_date: str, end_date: str) -> List[Dict]:
    url = f"{BASE_URL}/timeseries/{timeseries_id}/getData?timespan={start_date}TZ/{end_date}TZ"
    return fetch_url(url)


def extract_city(label: str) -> str:
    city_mapping_dict = {
        "48R236 - Aeroport 2": "Liège",
        "48R516 - Aeroport 2": "Charleroi",
        "48R237 - Aeroport 1": "Liège",
        "48R515 - Aeroport 1": "Charleroi",
        "Arts-Loi": "Brussel",
        "Bruxelles": "Brussel",
        "Maerlant": "Antwerpen",
    }

    name_part = label.split(" - ", 1)[1]
    city = name_part.split("(", 1)[0].strip().capitalize()

    for city_mapping in list(city_mapping_dict.keys()):
        if city_mapping in label:
            city = city_mapping_dict.get(city_mapping)
    return city


def is_in_region(lat: float, lon: float) -> bool:
    return any(region_gdf.contains(Point(lon, lat)))


def get_station_details():
    stations = fetch_stations()
    data_rows = []

    for station in stations:
        lon, lat, _ = station.get("geometry").get("coordinates")
        if not is_in_region(lat, lon):
            continue

        city = extract_city(station.get("properties").get("label"))

        data_rows.append(
            {
                "city": city,
                "station_id": station.get("properties").get("id"),
                "label": station.get("properties").get("label"),
                "lat": lat,
                "lon": lon,
            }
        )

    return pd.DataFrame(data_rows)


@st.cache_data
def aggregate_pollution_data(start_date: str, end_date: str) -> pd.DataFrame:
    stations_df = get_station_details()
    data_rows = []

    for _, row in stations_df.iterrows():
        station_id = row["station_id"]
        city = row["city"]
        lat = row["lat"]
        lon = row["lon"]

        station_timeseries = fetch_station_timeseries(station_id).get("properties").get("timeseries")
        for ts_id, ts_details in station_timeseries.items():
            phenomenon_id = ts_details.get("phenomenon").get("id")
            for pollutant_name, pollution_id in POLLUTANTS.items():
                if phenomenon_id == pollution_id:
                    values = fetch_timeseries_data(ts_id, start_date, end_date).get("values")
                    for ts_value in values:
                        timestamp = datetime.fromtimestamp(int(ts_value.get("timestamp")) / 1000, UTC).strftime("%Y-%m-%d %H:%M:%S")
                        data_rows.append(
                            {
                                "city": city,
                                "station_id": station_id,
                                "lat": lat,
                                "lon": lon,
                                "pollutant": pollutant_name,
                                "timestamp": timestamp,
                                "value": ts_value.get("value"),
                            }
                        )
    return pd.DataFrame(data_rows)


region_gdf = load_region_geometry()
