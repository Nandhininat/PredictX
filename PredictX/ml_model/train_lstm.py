import os
import numpy as np
import pandas as pd
import joblib

from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "dataset", "machine_sensor_data.csv")
MODEL_PATH = os.path.join(
    BASE_DIR, "ml_model", "predictx_lstm.keras"
)
SCALER_PATH = os.path.join(
    BASE_DIR, "ml_model", "scaler.pkl"
)

data = pd.read_csv(DATA_PATH)
features = ["temperature", "vibration", "speed"]
X = data[features].values.astype(float)

scaler = MinMaxScaler()
X_scaled = scaler.fit_transform(X)

X_sequence = []
y_sequence = []

for i in range(len(X_scaled) - 1):
    X_sequence.append(X_scaled[i])
    y_sequence.append(X_scaled[i + 1])

X_sequence = np.array(X_sequence).reshape(-1, 1, 3)
y_sequence = np.array(y_sequence)

model = Sequential([
    LSTM(32, input_shape=(1, 3)),
    Dense(16, activation="relu"),
    Dense(3)
])

model.compile(optimizer="adam", loss="mse")

model.fit(
    X_sequence,
    y_sequence,
    epochs=50,
    batch_size=4,
    verbose=1
)

model.save(MODEL_PATH)
joblib.dump(scaler, SCALER_PATH)

print("LSTM model trained successfully!")
print("Model:", MODEL_PATH)
print("Scaler:", SCALER_PATH)
