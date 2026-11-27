import os
import mysql.connector
from dotenv import load_dotenv
from urllib.parse import urlparse, unquote

load_dotenv()


def get_connection():
    db_url = os.getenv("DATABASE_URL")

    if not db_url:
        raise RuntimeError("DATABASE_URL is not configured")

    parsed = urlparse(db_url)

    return mysql.connector.connect(
        host=parsed.hostname,
        port=parsed.port or 3306,
        user=unquote(parsed.username or ""),
        password=unquote(parsed.password or ""),
        database=parsed.path.lstrip("/")
    )


def init_db():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(100) NOT NULL UNIQUE,
            password VARCHAR(255) NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            student_id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            age INT NOT NULL,
            gender VARCHAR(20) NOT NULL,
            study_hours FLOAT NOT NULL,
            attendance FLOAT NOT NULL,
            previous_marks FLOAT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS predictions (
            prediction_id INT AUTO_INCREMENT PRIMARY KEY,
            student_id INT NOT NULL,
            predicted_score FLOAT NOT NULL,
            performance_level VARCHAR(50) NOT NULL,
            prediction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES students(student_id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS marks (
            mark_id INT AUTO_INCREMENT PRIMARY KEY,
            student_id INT NOT NULL,
            subject VARCHAR(100) NOT NULL,
            marks_obtained FLOAT NOT NULL,
            total_marks FLOAT NOT NULL,
            FOREIGN KEY (student_id) REFERENCES students(student_id)
        )
    """)

    connection.commit()
    cursor.close()
    connection.close()