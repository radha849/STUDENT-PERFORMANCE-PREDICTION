import os
import mysql.connector
from dotenv import load_dotenv
from urllib.parse import urlparse, unquote

load_dotenv()

def get_connection():
    db_url = os.getenv("DATABASE_URL")

    if db_url:
        parsed = urlparse(db_url)

        connection = mysql.connector.connect(
            host=parsed.hostname,
            user=unquote(parsed.username or ""),
            password=unquote(parsed.password or ""),
            database=parsed.path.lstrip("/"),
            port=parsed.port or 3306
        )
    else:
        connection = mysql.connector.connect(
            host=os.getenv("DB_HOST", "localhost"),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME", "student_performance"),
            port=int(os.getenv("DB_PORT") or "3306")
        )

    return connection


if __name__ == "__main__":
    connection = get_connection()

    if connection.is_connected():
        print("Database connected successfully!")

    connection.close()