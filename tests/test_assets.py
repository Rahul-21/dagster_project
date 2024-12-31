import pytest
from unittest.mock import patch, MagicMock
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.engine.base import Engine
from assets import covid_data, weather_data, joined_data, persist_to_db

# Mock Data for testing
mock_covid_data = pd.DataFrame({
    'timestamp': pd.to_datetime(['2020-01-01 00:00:00', '2020-01-01 01:00:00']),
    'Country/Region': ['CountryA', 'CountryB'],
    '1/22/20': [100, 200],
    '1/23/20': [150, 250]
})

mock_weather_data = pd.DataFrame({
    'date': pd.to_datetime(['2020-01-01 00:00:00', '2020-01-01 01:00:00']),
    'temperature': [20, 25],
    'precipitation': [0.5, 0.7]
})

# Test covid_data asset
@patch('pandas.read_csv')
def test_covid_data(mock_read_csv):
    # Mock the return value of pd.read_csv
    mock_read_csv.return_value = mock_covid_data

    # Run the asset function
    covid_df = covid_data()

    # Check if the output is a DataFrame
    assert isinstance(covid_df, pd.DataFrame)
    
    # Check if the 'timestamp' column exists
    assert 'timestamp' in covid_df.columns
    
    # Check if the 'timestamp' column is of datetime type
    assert pd.api.types.is_datetime64_any_dtype(covid_df['timestamp'])
    
    # Check the hour column
    assert 'hour' in covid_df.columns


# Test weather_data asset
@patch('pandas.read_csv')
def test_weather_data(mock_read_csv):
    # Mock the return value of pd.read_csv
    mock_read_csv.return_value = mock_weather_data

    # Run the asset function
    weather_df = weather_data()

    # Check if the output is a DataFrame
    assert isinstance(weather_df, pd.DataFrame)
    
    # Check if the 'date' column exists
    assert 'date' in weather_df.columns
    
    # Check if the 'date' column is of datetime type
    assert pd.api.types.is_datetime64_any_dtype(weather_df['date'])


# Test the join operation
def test_joined_data():
    # Run the asset function with mocked data
    joined_df = joined_data(mock_covid_data, mock_weather_data)

    # Check if the output is a DataFrame
    assert isinstance(joined_df, pd.DataFrame)
    
    # Check that the join was done on the correct columns
    assert 'timestamp' in joined_df.columns
    assert 'date' in joined_df.columns
    assert 'temperature' in joined_df.columns
    assert 'precipitation' in joined_df.columns
    
    # Ensure the data is correctly merged
    assert len(joined_df) == 2  # Should have 2 rows if the join was successful


@patch('sqlalchemy.create_engine')
@patch('pandas.DataFrame.to_sql')  # Mock the to_sql method to avoid actual database interaction
def test_persist_to_db(mock_to_sql, mock_create_engine):
    # Mock the engine and the connection
    mock_engine = MagicMock(spec=Engine)
    
    # Mock the connection returned by the engine
    mock_connection = MagicMock()
    
    # Mock the behavior of engine.connect() returning the mock connection
    mock_engine.connect.return_value.__enter__.return_value = mock_connection
    
    # Create a mock DataFrame for testing
    mock_covid_data = pd.DataFrame({
        'timestamp': pd.to_datetime(['2021-01-01 00:00:00', '2021-01-01 01:00:00']),
        'Country/Region': ['Country A', 'Country B'],
        'case_1': [100, 200]
    })
    
    # Mock the behavior of the 'to_sql' function
    mock_to_sql.return_value = None  # Avoid actually trying to save anything
    
    # Call the persist_to_db asset with the mock engine
    persist_to_db(mock_covid_data, engine=mock_engine)
    
    # Check that the to_sql method was called with the correct parameters
    mock_to_sql.assert_called_once_with('covid_weather_data', mock_connection, if_exists='replace', index=False)
    
    # Ensure that engine.connect() was called once
    mock_engine.connect.assert_called_once()
    
    # Ensure that the connection's execute method was not called (because we're mocking it)
    mock_connection.execute.assert_not_called()





# Run the tests
if __name__ == "__main__":
    pytest.main()
