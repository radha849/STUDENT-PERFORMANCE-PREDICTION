import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    connection = mysql.connector.connect(
        host=os.getenv("DB_HOST", "mysql.railway.internal"),
        user=str(os.getenv("DB_USER") or "root"),
        password=str(os.getenv("DB_PASSWORD") or"aEUhpNqPLRhKICURemUjtWhZohtIdOhv"),
        database=str(os.getenv("DB_NAME") or "railway"),
        port=int(os.getenv("DB_PORT")  or "3306")
    )

    return connection


if __name__ == "__main__":
    connection = get_connection()

    if connection.is_connected():
        print("Database connected successfully!")

    connection.close()