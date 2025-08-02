import streamlit as st
import plotly.express as px
import pandas as pd

from config import POLLUTANTS, AGGREGATION_FUNCTIONS, TOP_NB_POLLUTED_CITIES
from data.irceline_data_fetcher import aggregate_pollution_data


def render_top_polluting_view(start_date: str, end_date: str) -> None:
    # Ask user input
    pollutant = st.selectbox("Select a Pollutant", list(POLLUTANTS.keys()))
    aggregation_method = st.selectbox(
        "Select aggregation method for selected period and multiple stations",
        options=AGGREGATION_FUNCTIONS.keys(),
        index=0
    )
    aggregation_func = AGGREGATION_FUNCTIONS[aggregation_method]

    # Aggregate pollution data per city
    pollution_per_city = agg_pollution_per_city(
        start_date,
        end_date,
        pollutant,
        aggregation_func,
    )

    # Create charts
    create_pollution_bar_chart(
        pollution_per_city,
        start_date,
        end_date,
        pollutant,
        aggregation_func,
    )
    create_pollution_city_map(pollution_per_city)


def agg_pollution_per_city(
    start_date: str,
    end_date: str,
    pollutant: str,
    aggregation_func: str,
) -> pd.DataFrame:
    return (
        aggregate_pollution_data(start_date, end_date)
        .query("pollutant == @pollutant")
        .groupby("city")
        .agg(
            value=("value", aggregation_func),
            lat=("lat", "mean"),
            lon=("lon", "mean"),
            nb_stations=("station_id", pd.Series.nunique)
        )
        .sort_values("value", ascending=False)
        .reset_index()
        .head(TOP_NB_POLLUTED_CITIES)
    )


def create_pollution_bar_chart(
    city_pollution_df: pd.DataFrame,
    start_date: str,
    end_date: str,
    pollutant: str,
    aggregation_func: str,
) -> None:
    fig = px.bar(
        city_pollution_df.reset_index(),
        x="city",
        y="value",
        title=f"Top {TOP_NB_POLLUTED_CITIES} polluted cities based on the {aggregation_func} {pollutant} between {start_date} and {end_date}.",
        color_discrete_sequence=["crimson"],
        hover_data=["city", "value", "nb_stations"],
        labels={"value": "Pollution Value", "city": "City", "nb_stations": "Number of Stations"},
        width=700,
        height=400,
    )
    fig.update_layout(
        xaxis=dict(categoryorder='array', categoryarray=city_pollution_df.index.tolist()),
    )

    st.plotly_chart(fig)


def create_pollution_city_map(city_pollution_df: pd.DataFrame) -> None:
    fig = px.scatter_mapbox(
        city_pollution_df,
        lat="lat",
        lon="lon",
        size="value",
        hover_data=["city", "value", "nb_stations"],
        labels={"city": "City", "value": "Pollution Value", "nb_stations": "Number of Stations", "lat": "Latitude", "lon": "Longitude"},
        zoom=7,
        height=600,
        width=800,
        title = f"Location of these top {TOP_NB_POLLUTED_CITIES} polluted cities.",
        mapbox_style="open-street-map"
    )

    st.plotly_chart(fig)
