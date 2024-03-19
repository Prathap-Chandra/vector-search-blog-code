# gunicorn configuration
# run command "gunicorn -c gunicorn_config.py run:app"

bind = "0.0.0.0:8000"
workers = 4
timeout = 18000