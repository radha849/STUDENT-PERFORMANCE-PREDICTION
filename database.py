import os
import mysql.connector
from dotenv import load_dotenv
from urllib.parse import urlparse, unquote

load_dotenv()


def get_connection():

    DATABASE_URL = os.getenv("DATABASE_URL")

    if DATABASE_URL:
        parsed = urlparse(DATABASE_URL)

        connection = mysql.connector.connect(
            host=parsed.hostname,
            user=unquote(parsed.username or ""),
            password=unquote(parsed.password or ""),
            database=parsed.path.lstrip("/"),
            port=parsed.port or 3306
        )

    else:
        DB_HOST = os.getenv("DB_HOST")
        DB_USER = os.getenv("DB_USER")
        DB_PASSWORD = os.getenv("DB_PASSWORD")
        DB_NAME = os.getenv("DB_NAME")
        DB_PORT = os.getenv("DB_PORT")

        if not all([DB_HOST, DB_USER, DB_PASSWORD, DB_NAME, DB_PORT]):
            raise RuntimeError(
                "Database configuration missing. "
                "Check Railway DB_HOST, DB_USER, "
                "DB_PASSWORD, DB_NAME and DB_PORT."
            )

        connection = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            port=int(DB_PORT)
        )

    return connection


if __name__ == "__main__":
    connection = get_connection()

    if connection.is_connected():
        print("Database connected successfully!")

    connection.close()