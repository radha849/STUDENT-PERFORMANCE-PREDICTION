import mysql.connector ,os

connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password=,
    database="student_performance"
)

cursor = connection.cursor()

name = input("Enter student name: ")
age = int(input("Enter student age: "))
gender = input("Enter gender: ")
study_hours = float(input("Enter daily study hours: "))
attendance = float(input("Enter attendance percentage: "))
previous_marks = float(input("Enter previous marks: "))

query = """
INSERT INTO students
(student id, name, age, gender, study_hours, attendance, previous_marks)
VALUES (%s,%s, %s, %s, %s, %s, %s)
"""

values = (student id, name, age, gender, study_hours, attendance, previous_marks)

cursor.execute(query, values)
connection.commit()

print("Student registered successfully!")

cursor.close()
connection.close()