import os
from dotenv import load_dotenv
from datetime import timedelta

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY")
    SALT = os.getenv("SALT")
    MYSQL_HOST = os.getenv("MYSQL_HOST")
    MYSQL_USER = os.getenv("MYSQL_USER")
    MYSQL_DB = os.getenv("MYSQL_DB")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER")
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_PORT = int(os.getenv("MAIL_PORT", 465))
    MAIL_SERVER = os.getenv("MAIL_SERVER")
    REMEMBER_COOKIE_DURATION = timedelta(days=7)
