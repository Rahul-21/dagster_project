# Dagster Data Pipeline Project

## Overview
This project implements a data pipeline using **Dagster**, an open-source data orchestrator. The pipeline performs data ingestion, transformation, and materialization into a PostgreSQL database, ensuring reproducibility and efficient data processing. The pipeline utilizes publicly available datasets and applies transformations using **Pandas**.

### Key Features:
- **Hourly Partitioned Table**: Data is partitioned hourly for efficient processing.
- **Data Transformations with Pandas**: Raw data from public datasets is transformed using Pandas.
- **PostgreSQL Storage**: Results are stored in a PostgreSQL database.
- **Automated Job Scheduling**: Jobs are scheduled automatically using Dagster’s scheduling feature.
- **Testing and Validation**: The project includes automated testing to ensure pipeline correctness.

## Project Structure
Here is a breakdown of the key files and directories in this project:

### `docker-compose.yml`:
- Sets up a Docker environment for the project.
- Configures the Dagster workspace and Python path.
- Exposes port 3000 for the Dagster webserver.
- Mounts the local directory to the container for development.

### `dagster.yaml`:
- Contains the Dagster instance configuration.
    - **PostgreSQL Storage**: Stores pipeline metadata in PostgreSQL.
    - **S3 Compute Logs (Optional)**: Logs are stored in an S3 bucket (optional configuration).
    - **Local Artifact Storage**: Stores artifacts locally under `/opt/dagster/local/`.

### `repo.py`:
- Defines the Dagster repository and connects jobs and assets to the Dagster instance.
- **Schedules**: Configures an optional daily schedule for the pipeline.
- **Sensors**: Monitors the `/data` directory for new files and triggers pipeline execution.

### `assets.py`:
- Implements the data pipeline using Dagster assets.
    - **table_1**: Fetches and partitions data hourly from a public dataset.
    - **table_2**: Loads another public dataset and applies necessary transformations.
    - **joined_table_1_2**: Joins `table_1` and `table_2` on a common key and computes additional metrics.

### `requirements.txt`:
- Lists the Python dependencies for the project, including:
    - **Dagster**: for orchestrating the pipeline.
    - **Pandas**: for data processing.
    - **SQLAlchemy**: for interacting with PostgreSQL.
    - **Pytest**: for testing pipeline functionality.

### `workspace.yaml`:
- Configures the Dagster workspace and loads the repository from `repo.py`.

### Data Directory:
- Expected to contain the public datasets used for the pipeline (e.g., `/path/to/data/`).
- The sensor monitors this directory for new `.csv` files to trigger the pipeline.

### Tests Directory (Not included, but recommended):
- Contains pytest tests to validate the correctness of data transformations, pipeline execution, and job schedules.

## Running the Dagster Project Using Docker

### 1. Prerequisites
Ensure you have the following installed on your machine:
- **Docker**: Download and install Docker from [here](https://www.docker.com/get-started).
- **Docker Compose (Optional)**: Install Docker Compose from [here](https://docs.docker.com/compose/install/).

### 2. Building the Docker Image
In the root directory of the project, build the Docker image:

```bash
docker build -t dagster-project .


## Running the Dagster Project Using Docker

### 1. Building the Docker Image
This command will build the Docker image using the Dockerfile and tag it as `dagster-project`.

```bash
docker build -t dagster-project .

## 2. Running Dagster in Docker
Once the Docker image is built, run the Dagster instance inside a Docker container:

```bash
docker run -p 3000:3000 -v $(pwd):/opt/dagster/app dagster-project

# Running the Dagster Project with Docker

## 1. Running the Dagster Project Docker Image

The following command runs the Dagster project Docker image:

- It maps the current directory (`$(pwd)`) to `/opt/dagster/app` inside the container.
- Exposes the Dagster UI on port 3000, accessible at [http://localhost:3000](http://localhost:3000) on your local machine.

```bash
docker run -it -p 3000:3000 -v $(pwd):/opt/dagster/app dagster/dagster-project


## 2. Accessing the Dagster UI

After the container is running, navigate to [http://localhost:3000](http://localhost:3000) in your browser. The Dagster UI will be available where you can:

- Monitor the status of your pipelines.
- Trigger pipeline runs manually.
- View logs and results of your pipeline executions.
- View schedules and sensor activities.

## 3. Testing the Dagster Pipeline

### 3.1. Test the Pipeline Manually

You can manually trigger the pipeline using the Dagster UI:

1. From the Dagster UI, navigate to the **"Jobs"** section.
2. Find and select the `covid_weather_pipeline` job.
3. Click **"Launch Run"** to manually trigger the pipeline.
4. Check the logs to ensure the pipeline runs successfully.

### 3.2. Test the Sensor

To test the sensor, which monitors new `.csv` files in the `/data` directory:

#### Option 1: Mount the Local `data/` Directory to the Docker Container

```bash
docker run -it -p 3000:3000 -v $(pwd)/data:/opt/dagster/app/data dagster/dagster-project


This mounts your local data/ directory to the /opt/dagster/app/data directory in the container, allowing the sensor to monitor new .csv files and trigger the pipeline accordingly.

```bash
docker run -p 3000:3000 -v $(pwd)/data:/data dagster-project



Testing the Dagster Pipeline
4.1. Test the Pipeline Manually
You can manually trigger the pipeline using the Dagster UI:

From the Dagster UI, navigate to the "Jobs" section.
Find and select the covid_weather_pipeline job.
Click "Launch Run" to manually trigger the pipeline.
Check the logs to ensure the pipeline runs successfully.
4.2. Test the Sensor
To test the sensor, which monitors new .csv files in the /data directory:

Option 1: Mount the local data/ directory to the Docker container:
bash
Copy code
docker run -p 3000:3000 -v $(pwd)/data:/data dagster-project
Then add new .csv files to the data/ directory. The sensor will automatically detect the new files and trigger the pipeline.

Option 2: Alternatively, enter the Docker container and add .csv files directly inside the container:
bash
Copy code
docker exec -it <container_id> /bin/bash
touch /data/test_file.csv
Once the sensor detects the new file, the pipeline will be triggered automatically, and you can view the logs in the Dagster UI.

4.3. Test the Schedule
The schedule will automatically trigger the pipeline based on the cron expression defined in repo.py. By default, it runs once a day at midnight UTC.

To test more frequently:

Modify the cron expression in repo.py (e.g., change "0 0 * * *" to "*/5 * * * *" to run every 5 minutes).
Rebuild the Docker image:
bash
Copy code
docker build -t dagster-project .
Re-run the container:
bash
Copy code
docker run -p 3000:3000 -v $(pwd)/data:/data dagster-project
The schedule will now trigger the pipeline every 5 minutes.

Using Docker Compose (Optional)
For easier orchestration of multi-container environments, you can use Docker Compose.

Example docker-compose.yml:
yaml
Copy code
version: '3.8'

services:
  dagster:
    build: .
    ports:
      - "3000:3000"
    volumes:
      - .:/opt/dagster/app
      - ./data:/data
    environment:
      - DAGSTER_HOME=/opt/dagster/dagster_home
    command: dagster dev -h 0.0.0.0 -p 3000
Starting the Services
Run all services defined in docker-compose.yml with a single command:

bash
Copy code
docker-compose up
Access the Dagster UI at http://localhost:3000 and interact with the pipelines, sensors, and schedules.

Stopping the Services
Stop all services using:

bash
Copy code
docker-compose down
Testing the Workflow in the Container
7.1. Verify Sensor Behavior
Add .csv files to the /data directory (either through mounting or directly inside the container).
The sensor will detect the new files and trigger the pipeline automatically.
Verify pipeline execution in the Dagster UI.
7.2. Verify the Schedule
Modify the cron expression in repo.py to test different intervals.
Ensure the schedule correctly triggers the pipeline at the defined intervals.
File Structure Overview
Here’s an overview of the project file structure:

bash
Copy code
dagster-project/
├── assets.py              # Implements the data pipeline assets
├── repo.py                # Defines repository, schedules, and sensors
├── Dockerfile             # Dockerfile for building the container
├── docker-compose.yml     # Docker Compose config (optional)
├── dagster.yaml           # Dagster instance configuration
├── workspace.yaml         # Configures the Dagster workspace
├── requirements.txt       # Lists the Python dependencies
├── data/                  # Directory for the monitored CSV files
└── tests/                 # (Recommended) Pytest tests for validation
Conclusion
This Dagster Data Pipeline project provides a flexible, reproducible framework for transforming and materializing public datasets into a PostgreSQL database. Using Docker, you can easily set up and test the pipeline, ensuring its smooth operation in a controlled environment.
