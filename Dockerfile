# Use a slim version of Python 3
FROM python:3-slim

# Expose the application port
EXPOSE 5002

# Environment variables to prevent Python from writing .pyc files and enable logging
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install dependencies
COPY requirements.txt .
RUN python -m pip install -r requirements.txt

# Set the working directory
WORKDIR /app

# Copy the application code
COPY . /app

# Ensure the Database directory exists and set permissions
RUN mkdir -p /app/Database


# Run the create_db.py file only if the database file doesn't exist, then start the application
ENTRYPOINT ["/bin/sh", "-c", "if [ ! -f /app/Database/ftp_server.db ]; then python create_db.py; fi && gunicorn --bind 0.0.0.0:5002 app:app"]
