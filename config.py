import os

class Config:
    API_ID = int(os.getenv("API_ID", "20758781"))
    API_HASH = os.getenv("API_HASH", "5bd4b1625d8324b5083459d41a32b11a")
    BOT_TOKEN = os.getenv("BOT_TOKEN", "7133806779:AAGTjLq4UWwpqW5bjfvixBkKA8hodKr5hAI")
    DATABASE_URI = os.getenv("DATABASE_URI", "mongodb+srv://dabbukarki:eiXlC27PtzEO4lRc@kobramovies.hrrze8l.mongodb.net/?retryWrites=true&w=majority&appName=kobramovies")
    DATABASE_NAME = os.getenv("DATABASE_NAME", "kobramovies")
    AUTH_CHANNEL = int(os.getenv("AUTH_CHANNEL", "-1002241432509"))
    FILE_CHANNEL = int(os.getenv("FILE_CHANNEL", "-1002205797851"))
    LOGIN_CHANNEL = int(os.getenv("LOGIN_CHANNEL", "-1002181757874"))
    LOG_CHANNEL = int(os.getenv("LOG_CHANNEL", "-1002241432509"))
    ADMINS = [int(x) for x in os.getenv("ADMINS", "1033348373").split()]
    PICS = os.getenv("PICS", "https://i.ibb.co/VSLt4Xs/Whats-App-Image-2024-07-30-at-14-16-01-5055b0b2.jpg")



