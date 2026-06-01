import multiprocessing

# Gunicorn configuration for running Django with async workers (Uvicorn worker)
workers = (multiprocessing.cpu_count() or 1) * 2 + 1
worker_class = "uvicorn.workers.UvicornWorker"
bind = "0.0.0.0:8000"
timeout = 120
keepalive = 2
accesslog = "-"
errorlog = "-"
loglevel = "info"

# Recommended: set environment variables for DJANGO_SETTINGS_MODULE and other secrets
