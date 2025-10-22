# backend/server.py
import io
import os
import json
from PIL import Image
from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
import tensorflow as tf
import pickle

from utils.preprocess import preprocess_pil_image  # veure fitxer a continuació

APP = Flask(__name__)
CORS(APP)

# Rutes als fitxers (ajusta si cal)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "models", "mushroom_model.h5")
LE_PATH = os.path.join(BASE_DIR, "models", "label_encoder.pkl")

print("Carregant model i label encoder...")
# Carrega model (.h5) sense compilar (només per inferència)
model = tf.keras.models.load_model(MODEL_PATH, compile=False)

with open(LE_PATH, "rb") as f:
    le = pickle.load(f)

NUM_CLASSES = len(le.classes_)
print(f"Model carregat: {MODEL_PATH} | classes: {NUM_CLASSES}")

# Endpoint health
@APP.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "classes": int(NUM_CLASSES)})

# Endpoint predict: accepta multipart/form-data amb camp 'image'
@APP.route("/predict", methods=["POST"])
def predict():
    if "image" not in request.files:
        return jsonify({"error": "No image file in request (field 'image')"}), 400
    file = request.files["image"]
    try:
        img = Image.open(file.stream).convert("RGB")
    except Exception as e:
        return jsonify({"error": "Invalid image", "detail": str(e)}), 400

    # Preprocessa i inferència
    try:
        inp = preprocess_pil_image(img)  # retorna array shape (1,H,W,3)
        preds = model.predict(inp)  # shape (1, C)
        probs = preds[0]
        # top-3
        topk = int(min(3, len(probs)))
        top_idx = np.argsort(-probs)[:topk]
        results = []
        for idx in top_idx:
            results.append({
                "class_index": int(idx),
                "class_name": str(le.classes_[idx]),
                "prob": float(probs[idx])
            })
        return jsonify({
            "predictions": results,
            "num_classes": NUM_CLASSES
        })
    except Exception as e:
        return jsonify({"error": "Inference error", "detail": str(e)}), 500

if __name__ == "__main__":
    # Executa localment: python backend/server.py
    APP.run(host="0.0.0.0", port=5000, debug=False)