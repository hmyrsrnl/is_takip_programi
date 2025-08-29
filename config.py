# config.py
import os
from decouple import config as decouple_config

DATABASE_URI = decouple_config("DATABASE_URL", default="sqlite:///db.sqlite")

class Config:
    DEBUG = False
    TESTING = False
    SECRET_KEY = decouple_config("SECRET_KEY", default="guess-me")
    SQLALCHEMY_DATABASE_URI = DATABASE_URI
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = False
