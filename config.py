import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    API_ID = int(os.getenv("API_ID"))
    API_HASH = os.getenv("API_HASH")
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    DATABASE_URI = os.getenv("DATABASE_URI")
    DATABASE_NAME = os.getenv("DATABASE_NAME")
    AUTH_CHANNEL = int(os.getenv("AUTH_CHANNEL"))
    FILE_CHANNEL = int(os.getenv("FILE_CHANNEL"))
    LOGIN_CHANNEL = int(os.getenv("LOGIN_CHANNEL"))
    LOG_CHANNEL = int(os.getenv("LOG_CHANNEL"))
    ADMINS = [int(x) for x in os.getenv("ADMINS").split()]
    PICS = os.getenv("PICS")


