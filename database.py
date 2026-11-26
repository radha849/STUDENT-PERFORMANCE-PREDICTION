import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    print("DB HOST:", os.getenv("DB_HOST"))
    connection = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        port=int(os.getenv("DB_PORT") or "3306")
    )
    return connection

if __name__ == "__main__":
    connection = get_connection()

    if connection.is_connected():
        print("Database connected successfully!")

    connection.close()