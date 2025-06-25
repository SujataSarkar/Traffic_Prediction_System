# from flask import Flask, request, jsonify
# import joblib
# import numpy as np
# import pandas as pd

# app = Flask(__name__)

# import joblib
# import requests

# def download_model():
#     url = 'https://drive.google.com/file/d/14WeHHlbv_2Ae9RjAuALZZ0KEhkzbb8vX/view?usp=drive_link'
#     response = requests.get(url)
#     with open("rf_model.pkl", 'wb') as f:
#         f.write(response.content)

# try:
#     rf_model = joblib.load("rf_model.pkl")
# except:
#     print("Downloading model...")
#     download_model()
#     rf_model = joblib.load("rf_model.pkl")


# # Final feature columns used in training
# model_columns = [
#     'Length', 'temp', 'humidity', 'windspeed', 'Weekend Status',
#     'hour_sin', 'hour_cos', 'day_sin', 'day_cos',
#     'icon_cloudy', 'icon_partly-cloudy-day', 'icon_partly-cloudy-night', 'icon_rain'
# ]

# @app.route('/predict', methods=['POST'])
# def predict():
#     data = request.get_json()

#     # Extract input values
#     temp = data['temp']
#     humidity = data['humidity']
#     windspeed = data['windspeed']
#     length = data['Length']
#     hour = data['hour']
#     dayofweek = data['dayofweek']
#     icon = data['icon']  # e.g., 'clear-day', 'cloudy', etc.

#     # Feature engineering
#     weekend = 1 if dayofweek >= 5 else 0
#     hour_sin = np.sin(2 * np.pi * hour / 24)
#     hour_cos = np.cos(2 * np.pi * hour / 24)
#     day_sin = np.sin(2 * np.pi * dayofweek / 7)
#     day_cos = np.cos(2 * np.pi * dayofweek / 7)

#     # Construct base dataframe
#     row = {
#         'Length': length,
#         'temp': temp,
#         'humidity': humidity,
#         'windspeed': windspeed,
#         'Weekend Status': weekend,
#         'hour_sin': hour_sin,
#         'hour_cos': hour_cos,
#         'day_sin': day_sin,
#         'day_cos': day_cos,
#         'icon': icon
#     }

#     df = pd.DataFrame([row])

#     # One-hot encode the 'icon' column
#     df = pd.get_dummies(df, columns=['icon'], prefix='icon', drop_first=False)

#     # Add any missing icon columns
#     for col in model_columns:
#         if col not in df.columns:
#             df[col] = 0

#     # Ensure column order
#     df = df[model_columns]

#     # Predict
#     prediction = rf_model.predict(df)

from flask import Flask, request, jsonify
import joblib
import numpy as np
import pandas as pd
import os
import gdown  # install via pip install gdown

app = Flask(__name__)

# ----------------- Model Download -----------------
model_path = "rf_model.pkl"

def download_model_from_drive():
    file_id = "14WeHHlbv_2Ae9RjAuALZZ0KEhkzbb8vX"  # Your Google Drive file ID
    url = f"https://drive.google.com/uc?id={file_id}"
    gdown.download(url, model_path, quiet=False)

# Load or download model
if not os.path.exists(model_path):
    print("🔄 Downloading model from Google Drive...")
    download_model_from_drive()

rf_model = joblib.load(model_path)

# ----------------- Model Columns -----------------
model_columns = [
    'Length', 'temp', 'humidity', 'windspeed', 'Weekend Status',
    'hour_sin', 'hour_cos', 'day_sin', 'day_cos',
    'icon_cloudy', 'icon_partly-cloudy-day', 'icon_partly-cloudy-night', 'icon_rain'
]

# ----------------- Prediction Route -----------------
@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()

    temp = data['temp']
    humidity = data['humidity']
    windspeed = data['windspeed']
    length = data['Length']
    hour = data['hour']
    dayofweek = data['dayofweek']
    icon = data['icon']

    weekend = 1 if dayofweek >= 5 else 0
    hour_sin = np.sin(2 * np.pi * hour / 24)
    hour_cos = np.cos(2 * np.pi * hour / 24)
    day_sin = np.sin(2 * np.pi * dayofweek / 7)
    day_cos = np.cos(2 * np.pi * dayofweek / 7)

    row = {
        'Length': length,
        'temp': temp,
        'humidity': humidity,
        'windspeed': windspeed,
        'Weekend Status': weekend,
        'hour_sin': hour_sin,
        'hour_cos': hour_cos,
        'day_sin': day_sin,
        'day_cos': day_cos,
        'icon': icon
    }

    df = pd.DataFrame([row])

    # One-hot encode icon
    df = pd.get_dummies(df, columns=['icon'], prefix='icon', drop_first=False)

    # Ensure all expected columns are present
    for col in model_columns:
        if col not in df.columns:
            df[col] = 0

    df = df[model_columns]

    prediction = rf_model.predict(df)
    return jsonify({'predicted_avg_speed': round(float(prediction[0]), 2)})

# ----------------- Run Server -----------------
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

#     return jsonify({'predicted_avg_speed': round(float(prediction[0]), 2)})

# if __name__ == '__main__':
#     app.run(debug=True)
