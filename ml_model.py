from sklearn.linear_model import LinearRegression
import numpy as np

# Sample training data
X = np.array([
    [2, 60, 50],
    [3, 70, 60],
    [4, 75, 65],
    [5, 80, 70],
    [6, 85, 80],
    [7, 90, 90],
    [8, 95, 95]
])

y = np.array([45, 55, 60, 70, 80, 90, 95])

# Train the model
model = LinearRegression()
model.fit(X, y)

def predict_performance(student_data):
    prediction = model.predict([student_data])
    return float(prediction[0])