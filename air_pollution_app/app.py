import streamlit as st
from datetime import datetime, timedelta
from config import MAX_DAYS, ViewMode

from streamlit_views.view_top_pollution import render_top_polluting_view
from streamlit_views.view_hourly_pollution import render_hourly_pollution_view


def start_pollution_app():
    view_mode, start_date, end_date = generate_streamlit_outline()
    
    if view_mode == ViewMode.TOP_POLLUTING_CITIES.value:
        render_top_polluting_view(start_date, end_date)
    elif view_mode == ViewMode.HOURLY_VIEW.value:
        render_hourly_pollution_view(start_date, end_date)


def generate_streamlit_outline():
    view_mode = st.sidebar.selectbox("View Mode", [ViewMode.TOP_POLLUTING_CITIES.value, ViewMode.HOURLY_VIEW.value])

    start_date = st.sidebar.date_input("Start Date", datetime.now() - timedelta(days=1))
    end_date = st.sidebar.date_input("End Date", datetime.now())
    if (end_date - start_date).days > MAX_DAYS:
        st.error(f"Please select a date range of {MAX_DAYS} days or less.")
        st.stop()

    return view_mode, start_date, end_date


if __name__ == "__main__":
    start_pollution_app()



# TODO:
# - Have composite pollution parameter
# - Create views for hourly view per station instead of per city + a view for number of stations and location per city