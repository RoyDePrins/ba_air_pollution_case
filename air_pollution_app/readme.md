# Air Quality Explorer – Flanders & Brussels

This Streamlit application allows users to explore and analyze hourly air pollution data from monitoring stations across Flanders and Brussels. The app fetches real-time data from the IRCELINE API and provides interactive visualizations for:

- **Top Polluting Cities:** View and compare the most polluted cities over a selected period.
- **Hourly Pollution View:** Inspect pollution levels by city and pollutant type per hour.
- **Station Details View:** Get an overview of the different stations per city and their details.

## Run the app

First, make sure all dependencies have been installed, then run:

```bash
streamlit run app.py
```

## Data Source

All pollution data is retrieved from [IRCELINE](https://www.irceline.be/en/documentation/open-data).
