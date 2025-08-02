import streamlit as st
import plotly.express as px
import pandas as pd

from data.irceline_data_fetcher import get_station_details


def render_station_overview() -> None:
    stations = get_station_details()

    # Ask user input
    selected_city = st.selectbox("Select City", sorted(stations["city"].unique()))

    # Filter stations data for selected city
    city_station_df = stations.query("city == @selected_city")

    # Create stations details charts
    create_station_overview_table(city_station_df)
    create_station_overview_map(city_station_df, selected_city)


def create_station_overview_table(city_station_df: pd.DataFrame) -> None:
    station_df = (
        city_station_df[["station_id", "label", "lat", "lon"]]
        .rename(columns={
            "station_id": "Station Identifier",
            "label": "Station Name/Label",
            "lat": "Latitude",
            "lon": "Longitude",
        })
        .reset_index(drop=True)
    )

    st.table(station_df)


def create_station_overview_map(city_station_df: pd.DataFrame, selected_city: str) -> None:
    fig = px.scatter_map(
        city_station_df,
        lat="lat",
        lon="lon",
        hover_data=["station_id", "label", "lat", "lon"],
        labels={"station_id": "Station Identifier", "label": "Station Name/Label", "lat": "Latitude", "lon": "Longitude"},
        color_discrete_sequence=["crimson"],
        zoom=10,
        height=500,
        title = f"Location of stations in city of {selected_city}.",
    )
    fig.update_traces(marker=dict(size=10))

    st.plotly_chart(fig)
