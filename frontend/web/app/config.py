import os


class Config:
    API_BASE_URL = os.getenv("API_BASE_URL", "http://flask:5000")
