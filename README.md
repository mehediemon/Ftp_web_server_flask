# FTP Web Application Flask

A Flask-based web application that simulates an FTP server for uploading and downloading files. This project uses SQLite as its database and Docker for containerization.

# Table of Contents
- [Features](#features)
- [Installation](#installation)
  - [Local Development](#local-development)
  - [Docker](#docker)
- [Usage](#usage)
- [Configuration](#configuration)
- [Contributing](#contributing)

# Features 
- User authentication
- File uploading and downloading
- Public and private file visibility
- Pagination and search functionality
- Docker support for easy deployment

# Installation

# Local Development

To run the application locally, follow these steps:

1. **Create a Virtual Environment**
   
  ```
  python3 -m venv ftp_app_env

  ```
   
3. **Install Dependencies**
  
  ```
  pip install -r requirements.txt

  ```

5. **Run the Application**
  ```
    python app.py

  ```
The application will be accessible at http://127.0.0.1:5000.
   
# Docker
To run the application using Docker, follow these steps:

Install Docker:

Ensure Docker is installed on your system. You can download Docker from Docker's official website.

Build and Run the Docker Container:

Navigate to the directory containing docker-compose.yml and run:

    docker compose up -d

This command will build the Docker image (if not already built) and start the container in detached mode. The application will be accessible at http://localhost:5002.


**Configuration:**

Configuration settings can be modified in config.py. For example, you can change the secret key or database URI.
