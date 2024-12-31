# Use the official Python image as the base image
FROM python:3.9-slim

RUN mkdir -p /opt/dagster/dagster_home

# Set environment variables
ENV DAGSTER_HOME=/opt/dagster/dagster_home

# Create working directory
WORKDIR /opt/dagster/app

# Copy your project files into the container
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install pytest (if not already installed in requirements.txt)
RUN pip install pytest

# Expose the required ports for the webserver and the Dagster job
EXPOSE 3000

# Command to run the tests (for now, as we’re focusing on tests in this step)
CMD ["pytest"]
