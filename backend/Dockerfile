FROM python:3.11.4

WORKDIR /app

COPY . /app

RUN pip install gunicorn

# Install any needed packages specified in requirements.txt
RUN pip install --trusted-host pypi.python.org -r requirements.txt

# Expose port 5000 for Gunicorn
EXPOSE 8000

# Run Gunicorn with the specified configuration file
CMD ["gunicorn", "-c", "gunicorn_config.py", "run:app"]