from flask import Flask, request, jsonify
from tensorflow.keras.models import load_model
import numpy as np
import pickle
import os
from utils.preprocess import load_and_preprocess_image

app = Flask(__name__)

# 🔹 Carrega del model i del LabelEncoder
MODEL_PATH = os.path.join("backend", "models", "mushroom_model.h5")
ENCODER_PATH = os.path.join("backend", "models", "label_encoder.pkl")

print("Carregant model i etiquetes...")
model = load_model(MODEL_PATH)
with open(ENCODER_PATH, "rb") as f:
    label_encoder = pickle.load(f)
print("✅ Model i etiquetes carregats correctament.")

@app.route("/predict", methods=["POST"])
def predict():
    if "file" not in request.files:
        return jsonify({"error": "No s'ha enviat cap fitxer"}), 400

    file = request.files["file"]
    if not file:
        return jsonify({"error": "Fitxer buit"}), 400

    # Desa temporalment
    temp_path = "temp_image.jpg"
    file.save(temp_path)

    # Prepara imatge
    img = load_and_preprocess_image(temp_path)

    # Predicció
    preds = model.predict(img)
    pred_idx = np.argmax(preds, axis=1)[0]
    pred_class = label_encoder.inverse_transform([pred_idx])[0]
    confidence = float(np.max(preds))

    result = {
        "name": pred_class,
        "confidence": round(confidence, 3)
    }

    return jsonify(result)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
