import os
import numpy as np

try:
    import joblib
    from tensorflow.keras.models import load_model
except Exception:
    joblib = None
    load_model = None

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "ml_model", "predictx_lstm.keras")
SCALER_PATH = os.path.join(BASE_DIR, "ml_model", "scaler.pkl")

_model = None
_scaler = None

def _load_lstm():
    global _model, _scaler
    if _model is not None and _scaler is not None:
        return True
    if load_model is None or joblib is None:
        return False
    if not (os.path.exists(MODEL_PATH) and os.path.exists(SCALER_PATH)):
        return False
    try:
        _model = load_model(MODEL_PATH)
        _scaler = joblib.load(SCALER_PATH)
        return True
    except Exception:
        _model = None
        _scaler = None
        return False

def predict_machine(temperature, vibration, speed):
    # Run the trained LSTM when available. Its forecast is used as an
    # additional model check; the health score remains interpretable.
    lstm_available = _load_lstm()
    lstm_forecast = None

    if lstm_available:
        values = np.array([[temperature, vibration, speed]], dtype=float)
        scaled = _scaler.transform(values)
        lstm_input = scaled.reshape(1, 1, 3)
        forecast_scaled = _model.predict(lstm_input, verbose=0)
        lstm_forecast = _scaler.inverse_transform(forecast_scaled)[0]

    temp_risk = min(max((temperature - 50) / 45, 0), 1)
    vibration_risk = min(max((vibration - 1) / 5, 0), 1)
    speed_risk = min(max((1500 - speed) / 300, 0), 1)

    risk = (
        temp_risk * 0.4
        + vibration_risk * 0.4
        + speed_risk * 0.2
    )

    health_score = round((1 - risk) * 100)
    health_score = max(0, min(health_score, 100))

    if health_score >= 70:
        alert = "Healthy"
        recommendation = (
            "Machine is operating normally. Continue regular monitoring."
        )
    elif health_score >= 40:
        alert = "Warning"
        recommendation = (
            "Schedule inspection and monitor sensor values."
        )
    else:
        alert = "Critical"
        recommendation = (
            "Immediate maintenance inspection is recommended."
        )

    rul = max(1, health_score)

    return {
        "health_score": health_score,
        "rul": rul,
        "alert": alert,
        "recommendation": recommendation,
        "lstm_available": lstm_available,
        "lstm_forecast": lstm_forecast
    }
