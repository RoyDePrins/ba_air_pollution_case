import streamlit as st
import altair as alt
import plotly.express as px
import pandas as pd

from config import POLLUTANTS, AGGREGATION_FUNCTIONS
from data.irceline_data_fetcher import aggregate_pollution_data


def render_top_polluting_view(start_date: str, end_date: str) -> None:
    # Ask user input
    pollutant = st.selectbox("Select a Pollutant", list(POLLUTANTS.keys()))
    aggregation_method = st.selectbox(
        "Select aggregation method for time and multiple stations",
        options=AGGREGATION_FUNCTIONS.keys(),
        index=0
    )

    # Aggregate pollution data per city
    pollution_per_city = agg_pollution_per_city(
        start_date,
        end_date,
        pollutant,
        AGGREGATION_FUNCTIONS[aggregation_method]
    )

    # Create charts
    create_pollution_bar_chart(pollution_per_city)
    create_pollution_city_map(pollution_per_city)


def agg_pollution_per_city(
    start_date: str,
    end_date: str,
    pollutant: str,
    aggregation_func: str,
    top_records_to_keep: int = 10
) -> pd.DataFrame:
    return (
        aggregate_pollution_data(start=start_date, end=end_date)
        .query(f"pollutant == '{pollutant}'")
        .groupby("city")
        .agg(
            value=("value", aggregation_func),
            lat=("lat", "mean"),
            lon=("lon", "mean"),
            nb_stations=("station_id", pd.Series.nunique)
        )
        .sort_values("value", ascending=False)
        .reset_index()
        .head(top_records_to_keep)
    )


def create_pollution_bar_chart(city_pollution_df: pd.DataFrame) -> None:
    bar_chart = alt.Chart(city_pollution_df.reset_index()).mark_bar(color="crimson").encode(
        x=alt.X("city:N", sort=list(city_pollution_df.index), title="City"),
        y=alt.Y("value:Q", title="Maximum Pollution over given period"),
        tooltip=["city", "value", "nb_stations"]
    ).properties(
        width=700,
        height=400
    )

    st.altair_chart(bar_chart)


def create_pollution_city_map(city_pollution_df: pd.DataFrame) -> None:
    fig = px.scatter_mapbox(
        city_pollution_df,
        lat="lat",
        lon="lon",
        size="value",
        hover_data={"city": True, "value": True, "nb_stations": True},
        zoom=7,
        height=600,
        width=800,
    )

    fig.update_layout(mapbox_style="open-street-map")
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

    st.plotly_chart(fig)
