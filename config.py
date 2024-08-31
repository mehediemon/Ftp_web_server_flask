import os

# Define the base directory and the database directory
basedir = os.path.abspath(os.path.dirname(__file__))
db_dir = os.path.join(basedir, 'Database')

# Ensure the Database directory exists
os.makedirs(db_dir, exist_ok=True)

class Config:
    SECRET_KEY = os.urandom(24)
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(db_dir, 'ftp_server.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
