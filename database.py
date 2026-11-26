import os
import mysql.connector
from dotenv import load_dotenv
from urllib.parse import urlparse, unquote

load_dotenv()

def get_connection():
    db_url = os.getenv("DATABASE_URL")

    if db_url:
        parsed = urlparse(db_url)

        return mysql.connector.connect(
            host=parsed.hostname,
            user=unquote(parsed.username or ""),
            password=unquote(parsed.password or ""),
            database=parsed.path.lstrip("/"),
            port=parsed.port or 3306
        )

    db_host = os.getenv("DB_HOST")
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_name = os.getenv("DB_NAME")
    db_port = os.getenv("DB_PORT")

    if not all([db_host, db_user, db_password, db_name, db_port]):
        raise RuntimeError(
            "Database configuration missing: check Railway DB_HOST, "
            "DB_USER, DB_PASSWORD, DB_NAME and DB_PORT variables."
        )

    return mysql.connector.connect(
        host=db_host,
        user=db_user,
        password=db_password,
        database=db_name,
        port=int(db_port)
    )


if __name__ == "__main__":
    connection = get_connection()

    if connection.is_connected():
        print("Database connected successfully!")

    connection.close()