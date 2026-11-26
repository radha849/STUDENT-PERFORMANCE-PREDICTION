from flask import Flask, render_template, request, redirect, session, send_file
from openpyxl import Workbook
from io import BytesIO
import os
from dotenv import load_dotenv
from database import get_connection

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")
@app.route('/dashboard')
def dashboard():
    if not session.get('logged_in'):
        return redirect('/')
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT COUNT(*) FROM students")
    total_students = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM predictions")
    total_predictions = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM predictions WHERE performance_level = 'Excellent'")
    excellent = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM predictions WHERE performance_level = 'Average'")
    average = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM predictions WHERE performance_level = 'Needs Improvement'")
    needs_improvement = cursor.fetchone()[0]

    cursor.close()
    connection.close()

    return render_template(
        'dashboard.html',
        total_students=total_students,
        total_predictions=total_predictions,
        excellent=excellent,
        average=average,
        needs_improvement=needs_improvement
    )


@app.route('/add_student', methods=['GET', 'POST'])
def add_student():
    if not session.get('logged_in'):
        return redirect('/')

    message = ""

    if request.method == 'POST':
        try:
            name = request.form['name'].strip()
            age = int(request.form['age'])
            gender = request.form['gender'].strip()
            study_hours = float(request.form['study_hours'])
            attendance = float(request.form['attendance'])
            previous_marks = float(request.form['previous_marks'])

            # Backend validation
            if len(name) < 2 or len(name) > 100:
                message = "Name must be between 2 and 100 characters."

            elif age < 1 or age > 100:
                message = "Age must be between 1 and 100."

            elif not gender in ['Male', 'Female', 'Other']:
                message = "Please select a valid gender."

            elif study_hours < 0 or study_hours > 24:
                message = "Study hours must be between 0 and 24."

            elif attendance < 0 or attendance > 100:
                message = "Attendance must be between 0 and 100."

            elif previous_marks < 0 or previous_marks > 100:
                message = "Previous marks must be between 0 and 100."

            else:
                connection = get_connection()
                cursor = connection.cursor()

                query = """
                INSERT INTO students
                (name, age, gender, study_hours, attendance, previous_marks)
                VALUES (%s, %s, %s, %s, %s, %s)
                """

                values = (
                    name,
                    age,
                    gender,
                    study_hours,
                    attendance,
                    previous_marks
                )

                cursor.execute(query, values)
                connection.commit()

                cursor.close()
                connection.close()

                message = "Student registered successfully!"

        except ValueError:
            message = "Please enter valid numeric values."

        except Exception as e:
            message = "Unable to register student. Please try again."
            print("Registration error:", e)

    return render_template('add_student.html', message=message)
@app.route('/view_students')
def view_students():
    if not session.get('logged_in'):
        return redirect('/')
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("SELECT * FROM students")
    students = cursor.fetchall()

    cursor.close()
    connection.close()

    message = request.args.get('message', '')

    return render_template(
        'view_students.html',
        students=students,
        message=message
    )
@app.route('/edit_student/<int:student_id>', methods=['GET', 'POST'])
def edit_student(student_id):
    if not session.get('logged_in'):
        return redirect('/')
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    if request.method == 'POST':

        query = """
        UPDATE students
        SET name = %s,
            age = %s,
            gender = %s,
            study_hours = %s,
            attendance = %s,
            previous_marks = %s
        WHERE student_id = %s
        """

        values = (
            request.form['name'],
            request.form['age'],
            request.form['gender'],
            request.form['study_hours'],
            request.form['attendance'],
            request.form['previous_marks'],
            student_id
        )

        cursor.execute(query, values)
        connection.commit()

        cursor.close()
        connection.close()

        return redirect('/view_students?message=Student%20updated%20successfully!')

    cursor.execute(
        "SELECT * FROM students WHERE student_id = %s",
        (student_id,)
    )

    student = cursor.fetchone()

    cursor.close()
    connection.close()

    if student is None:
        return redirect('/view_students?message=Student%20not%20found!')

    return render_template('edit_student.html', student=student)
@app.route('/delete_student/<int:student_id>', methods=['POST'])
def delete_student(student_id):
    if not session.get('logged_in'):
        return redirect('/')
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        "SELECT COUNT(*) AS total FROM predictions WHERE student_id = %s",
        (student_id,)
    )
    prediction_count = cursor.fetchone()['total']

    cursor.execute(
        "SELECT COUNT(*) AS total FROM marks WHERE student_id = %s",
        (student_id,)
    )
    marks_count = cursor.fetchone()['total']

    if prediction_count > 0 or marks_count > 0:
        message = "Cannot delete student because marks or prediction history exists."
    else:
        cursor.execute(
            "DELETE FROM students WHERE student_id = %s",
            (student_id,)
        )
        connection.commit()
        message = "Student deleted successfully!"

    cursor.close()
    connection.close()

    return redirect('/view_students?message=' + message.replace(' ', '%20'))
@app.route('/predict', methods=['GET', 'POST'])
def predict():
    if not session.get('logged_in'):
        return redirect('/')
    message = ""

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    # Get all registered students
    cursor.execute("SELECT * FROM students")
    students = cursor.fetchall()

    if request.method == 'POST':
        student_id = request.form['student_id']

        # Fetch selected student's details
        cursor.execute(
            "SELECT * FROM students WHERE student_id = %s",
            (student_id,)
        )
        student = cursor.fetchone()

        if student:
            from ml_model import predict_performance

            study_hours = float(student['study_hours'])
            attendance = float(student['attendance'])
            previous_marks = float(student['previous_marks'])

            predicted_score = predict_performance([
                study_hours,
                attendance,
                previous_marks
            ])

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

            message = (
                f"Student: {student['name']} | "
                f"Predicted Score: {predicted_score:.2f} | "
                f"Performance: {performance_level}"
            )
        else:
            message = "Student not found!"

    cursor.close()
    connection.close()

    return render_template(
        'predict.html',
        students=students,
        message=message
    )
@app.route('/', methods=['GET', 'POST'])
def login():
    message = ""

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE username=%s AND password=%s",
            (username, password)
        )

        user = cursor.fetchone()

        cursor.close()
        connection.close()

        if user:
            session['logged_in'] = True
            return redirect('/dashboard')
        else:
            message = "Invalid username or password!"

    return render_template('login.html', message=message)
@app.route('/prediction_history')
def prediction_history():
    if not session.get('logged_in'):
        return redirect('/')
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            p.prediction_id,
            p.student_id,
            s.name,
            p.predicted_score,
            p.performance_level,
            p.prediction_date
        FROM predictions p
        JOIN students s ON p.student_id = s.student_id
        ORDER BY p.prediction_id DESC
    """)

    predictions = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        'prediction_history.html',
        predictions=predictions
    )
@app.route('/logout')
def logout():
    session.clear
    return redirect('/')
@app.route('/export_students')
def export_students():

    if not session.get('logged_in'):
        return redirect('/')

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT student_id, name, age, gender,
               study_hours, attendance, previous_marks
        FROM students
    """)

    students = cursor.fetchall()
    columns = [column[0] for column in cursor.description]

    cursor.close()
    connection.close()

    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Student Records"

    sheet.append(columns)

    for student in students:
        sheet.append(list(student))

    output = BytesIO()
    workbook.save(output)
    output.seek(0)

    return send_file(
        output,
        as_attachment=True,
        download_name="Student_Records.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
@app.route('/export_predictions')
def export_predictions():

    if not session.get('logged_in'):
        return redirect('/')

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            p.prediction_id,
            p.student_id,
            s.name,
            p.predicted_score,
            p.performance_level,
            p.prediction_date
        FROM predictions p
        JOIN students s ON p.student_id = s.student_id
        ORDER BY p.prediction_id DESC
    """)

    predictions = cursor.fetchall()
    columns = [column[0] for column in cursor.description]

    cursor.close()
    connection.close()

    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Prediction History"

    sheet.append(columns)

    for prediction in predictions:
        sheet.append(list(prediction))

    output = BytesIO()
    workbook.save(output)
    output.seek(0)

    return send_file(
        output,
        as_attachment=True,
        download_name="Prediction_History.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
if __name__ == '__main__':
    app.run(debug=True)