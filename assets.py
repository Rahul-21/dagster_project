import pandas as pd
from typing import Optional

import requests
from dagster import asset, job, op
from sqlalchemy import create_engine
from sqlalchemy.engine.base import Engine
import os


import warnings
warnings.filterwarnings('ignore', category=UserWarning, message=".*Could not infer format.*")

# Define the database location
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///data/pipeline.db')

# Asset 1: COVID-19 Data (from John Hopkins University)
@asset
def covid_data() -> pd.DataFrame:
    """
    Fetches and processes COVID-19 data from the public API.
    The data will be partitioned by hour for storage.
    """
    url = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv'
    
    try:
        covid_data = pd.read_csv(url)
    except requests.exceptions.RequestException as e:
        raise Exception(f"Failed to fetch COVID data: {e}")
    
    # Drop unnecessary columns only if they exist
    columns_to_drop = ['Province/State', 'Lat', 'Long']
    covid_data = covid_data.drop(columns=[col for col in columns_to_drop if col in covid_data.columns], errors='ignore')
    
    # Group by country and sum cases, retain timestamp for later use
    covid_data = covid_data.groupby('Country/Region').sum(numeric_only=True).T  # Group by country and sum cases
    covid_data = covid_data.reset_index().rename(columns={'index': 'timestamp'})

    # Handle mixed or uncertain formats
    # Example: normalizing date formats to '%m/%d/%y'
    covid_data['timestamp'] = covid_data['timestamp'].apply(lambda x: pd.to_datetime(x, errors='coerce') if isinstance(x, str) else x)

    covid_data['hour'] = covid_data['timestamp'].dt.floor('h')

    # Standardize the date format (YYYY-MM-DD) for joining
    covid_data['timestamp'] = covid_data['timestamp'].dt.strftime('%Y-%m-%d')
    
    return covid_data


# Asset 2: Weather Data (Simulated using a public NOAA weather API or any dataset)
@asset
def weather_data() -> pd.DataFrame:
    """
    Fetches and processes weather data.
    """
    url = 'https://www1.ncdc.noaa.gov/pub/data/cdo/samples/PRECIP_HLY_sample_csv.csv'  # Example URL
    
    try:
        weather_data = pd.read_csv(url)
    except requests.exceptions.RequestException as e:
        raise Exception(f"Failed to fetch weather data: {e}")
    
    # Rename the 'DATE' column to 'date' if it exists
    if 'DATE' in weather_data.columns:
        weather_data = weather_data.rename(columns={'DATE': 'date'})

    # Convert the 'date' column to datetime format, handling errors
    weather_data['date'] = weather_data['date'].apply(lambda x: pd.to_datetime(x, errors='coerce') if isinstance(x, str) else x)
    
    # Drop rows where 'date' could not be parsed (if needed)
    weather_data = weather_data.dropna(subset=['date'])
    
    # Standardize the date format (YYYY-MM-DD) for joining
    weather_data['date'] = weather_data['date'].dt.strftime('%Y-%m-%d')

    return weather_data



# Asset 3: Join COVID and Weather Data
@asset
def joined_data(covid_data: pd.DataFrame, weather_data: pd.DataFrame) -> pd.DataFrame:
    """
    Joins the COVID data with the weather data based on a common timestamp or date column.
    """
    # Join the two datasets on the appropriate columns: 'timestamp' from covid_data and 'date' from weather_data
    joined_df = pd.merge(covid_data, weather_data, left_on='timestamp', right_on='date', how='inner')
    
    return joined_df


# Asset 4: Persist the Data to a Relational Database (SQLite)
@asset
def persist_to_db(joined_data: pd.DataFrame, engine: Optional[Engine] = None) -> None:
    """
    Persists the joined and transformed data into an SQLite database.
    """
    # Use the passed engine, or create a new one if none is provided
    engine = engine or create_engine(DATABASE_URL)
    
    # Open a connection from the engine
    with engine.connect() as connection:
        # Write the data to the database, partitioned by hour
        joined_data.to_sql('covid_weather_data', connection, if_exists='replace', index=False)


# Define Jobs that combine the assets
@job
def covid_weather_pipeline():
    """
    The job that combines all assets: COVID-19 data, weather data, joining, and persisting.
    """
    # Execution order: Fetch COVID data, Weather data, join, and persist
    covid_data_result = covid_data()
    weather_data_result = weather_data()
    joined_data_result = joined_data(covid_data_result, weather_data_result)
    persist_to_db(joined_data_result)
