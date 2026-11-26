import mysql.connector , os

connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password=os.getenv("DB_PASSWORD"),
    database="student_performance"
)

cursor = connection.cursor()

student_id = int(input("Enter student ID: "))
subject = input("Enter subject name: ")
marks = float(input("Enter marks obtained: "))
total = float(input("Enter total marks: "))

query = """
INSERT INTO marks
(student_id, subject, marks_obtained, total_marks)
VALUES (%s, %s, %s, %s)
"""

values = (student_id, subject, marks, total)

cursor.execute(query, values)
connection.commit()

print("Student marks added successfully!")

cursor.close()
connection.close()