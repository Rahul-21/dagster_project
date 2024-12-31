from dagster import repository, schedule, sensor, job
import os
from pathlib import Path
import logging
from assets import covid_weather_pipeline  # Import the pipeline job

# Define the directory to watch for new CSV files (inside Docker container)
WATCH_DIRECTORY = Path("/data")  # This is the '/data' directory inside the container
PROCESSED_FILES_FILE = "/data/processed_files.txt"  # File to track processed CSV files

# Setup logger for better visibility in production
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Schedule Definition: Runs the pipeline once every day at midnight UTC
@schedule(cron_schedule="0 0 * * *", job=covid_weather_pipeline)
def daily_covid_weather_pipeline_schedule():
    """
    A schedule to run the covid_weather_pipeline every day at midnight UTC.
    """
    return {}

# Sensor to watch for new CSV files in the specified directory
@sensor(job=covid_weather_pipeline)
def covid_weather_sensor(context):
    """
    This sensor monitors the `WATCH_DIRECTORY` for new CSV files.
    When a new file is found, it triggers the `covid_weather_pipeline` job.
    """
    try:
        # Get the list of existing CSV files in the directory
        existing_files = set(WATCH_DIRECTORY.glob("*.csv"))

        # Initialize the processed files list if the file doesn't exist
        if not os.path.exists(PROCESSED_FILES_FILE):
            with open(PROCESSED_FILES_FILE, "w") as f:
                f.write("\n")

        # Read previously processed files
        with open(PROCESSED_FILES_FILE, "r") as f:
            processed_files = set(f.read().splitlines())

        # Identify new files by comparing with previously processed ones
        new_files = existing_files - processed_files

        if new_files:
            # Log the new files found in the directory
            context.log.info(f"Found new files: {', '.join(str(f) for f in new_files)}")
            
            # Update the processed files list
            with open(PROCESSED_FILES_FILE, "a") as f:
                for new_file in new_files:
                    f.write(f"{new_file}\n")

            # Trigger the pipeline job to process the new files
            # Returning the job, Dagster will handle running it
            return covid_weather_pipeline()

        else:
            # Log when no new files are found
            context.log.info("No new files detected.")
            return None

    except Exception as e:
        logger.error(f"Error in covid_weather_sensor: {e}")
        context.log.error(f"Error processing files: {e}")
        return None

# Repository definition to tie everything together
@repository
def dagster_project_repo():
    """
    Defines the Dagster repository, including jobs, assets, and schedules.
    This repository ties together all jobs and schedules defined in this module.
    """
    return [
        covid_weather_pipeline,  # Include the pipeline job that processes the assets
        daily_covid_weather_pipeline_schedule,  # Add the schedule for the pipeline
    ]
