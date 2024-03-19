# # Use an official Python runtime as a parent image
# FROM python:3.9-slim

# # Set the working directory in the container
# WORKDIR /app

# # Copy the requirements file into the container at /app
# COPY requirements.txt /app

# # Install any needed packages specified in requirements.txt
# RUN pip install --no-cache-dir -r requirements.txt

# # Copy the current directory contents into the container at /app
# COPY . /app

# # Make port 5000 available to the world outside this container
# EXPOSE 8000
 
# # Run main.py when the container launches
# CMD ["python3", "run.py"]

FROM python:3.11

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app/

# Create a virtual environment
RUN python3 -m venv venv

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies in the virtual environment
RUN /app/venv/bin/pip install --upgrade pip
RUN /app/venv/bin/pip install -r requirements.txt

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Run run.py when the container launches, using the virtual environment
CMD ["/app/venv/bin/python", "run.py"]
