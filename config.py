import os
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database   (it should be added later)


SQLALCHEMY_DATABASE_URI = 'postgresql://yongxingnie:@localhost:5432/art'

# set and designate a datebase named as 'art'