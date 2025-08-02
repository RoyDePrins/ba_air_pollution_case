import streamlit as st
import plotly.express as px
import pandas as pd

from config import POLLUTANTS, AGGREGATION_FUNCTIONS
from data.irceline_data_fetcher import aggregate_pollution_data


def render_hourly_pollution_view(start_date: str, end_date: str) -> None:
    city_pollution_df = aggregate_pollution_data(start_date, end_date)

    # Ask user input
    selected_city = st.selectbox("Select City", sorted(city_pollution_df["city"].unique()))
    aggregation_method = st.selectbox(
        "Select aggregation method in case of multiple stations",
        options=AGGREGATION_FUNCTIONS.keys(),
        index=0
    )

    # Aggregate pollution data for selected city
    pollution_per_city = agg_hourly_pollution_for_city(
        city_pollution_df,
        selected_city,
        AGGREGATION_FUNCTIONS[aggregation_method]
    )

    # Create pollution charts
    create_hourly_pollution_line_charts(
        pollution_per_city,
        start_date,
        end_date,
    )


def agg_hourly_pollution_for_city(
    city_pollution_df: pd.DataFrame,
    selected_city: str,
    aggregation_func: str
) -> pd.DataFrame:
    return (
        city_pollution_df
        .query("city == @selected_city")
        .groupby(["city", "pollutant", "timestamp"])
        .agg(
            value=("value", aggregation_func),
            nb_stations=("station_id", pd.Series.nunique)
        )
        .reset_index()
    )


def create_hourly_pollution_line_charts(
    city_pollution_df: pd.DataFrame,
    start_date: str,
    end_date: str,
) -> None:
    for pollutant in POLLUTANTS.keys():
        pollutant_df = city_pollution_df.query("pollutant == @pollutant")

        fig = px.line(
            pollutant_df,
            x="timestamp",
            y="value",
            title=f"Hourly {pollutant} Values between {start_date} and {end_date}.",
            hover_data={"timestamp", "value", "nb_stations"},
            labels={"value": "Pollution Value", "timestamp": "Timestamp", "nb_stations": "Number of Stations"},
        )
        fig.update_layout(height=250, margin={"t": 50, "l": 0, "r": 0, "b": 0})

        st.plotly_chart(fig)
