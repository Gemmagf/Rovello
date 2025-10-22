# test_mushroom.py
import numpy as np
import pickle
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.efficientnet import preprocess_input

# -------------------------------
# Rutes als fitxers del model
# -------------------------------
MODEL_PATH = "backend/models/mushroom_model.h5"
ENCODER_PATH = "backend/models/label_encoder.pkl"
TEST_IMAGE_PATH = "rovello2.jpg"  # canvia-ho a la imatge que vols provar

# -------------------------------
# Carrega model i label encoder
# -------------------------------
model = load_model(MODEL_PATH)
with open(ENCODER_PATH, "rb") as f:
    le = pickle.load(f)

# -------------------------------
# Carrega i preprocessa la imatge
# -------------------------------
img = image.load_img(TEST_IMAGE_PATH, target_size=(224, 224))
x = image.img_to_array(img)
x = np.expand_dims(x, axis=0)
x = preprocess_input(x * 255.0)  # Important: mateix preprocess que entrenament

# -------------------------------
# Predicció
# -------------------------------
preds = model.predict(x)
top1_idx = np.argmax(preds[0])
top1_class = le.inverse_transform([top1_idx])[0]

# Top-5
top5_idx = preds[0].argsort()[-5:][::-1]
top5_classes = le.inverse_transform(top5_idx)

print(f"Top-1 Predicció: {top1_class} ({preds[0][top1_idx]:.2f})")
print("Top-5 Prediccions:")
for i, idx in enumerate(top5_idx):
    print(f"  {i+1}: {le.inverse_transform([idx])[0]} ({preds[0][idx]:.2f})")