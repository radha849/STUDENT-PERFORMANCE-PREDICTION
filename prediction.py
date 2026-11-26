from database import get_connection
from ml_model import predict_performance

def predict_student(student_id):

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM students WHERE student_id = %s",
        (student_id,)
    )

    student = cursor.fetchone()

    if student is None:
        print("Student not found!")
        cursor.close()
        connection.close()
        return

    student_data = [
        float(student['study_hours']),
        float(student['attendance']),
        float(student['previous_marks'])
    ]

    predicted_score = predict_performance(student_data)

    if predicted_score >= 75:
        performance_level = "Excellent"
    elif predicted_score >= 50:
        performance_level = "Average"
    else:
        performance_level = "Needs Improvement"

    cursor.execute(
        """INSERT INTO predictions
        (student_id, predicted_score, performance_level)
        VALUES (%s, %s, %s)""",
        (student_id, predicted_score, performance_level)
    )

    connection.commit()

    print("Student:", student['name'])
    print("Predicted Score:", round(predicted_score, 2))
    print("Performance:", performance_level)

    cursor.close()
    connection.close()


if __name__ == "__main__":
    student_id = int(input("Enter Student ID: "))
    predict_student(student_id)