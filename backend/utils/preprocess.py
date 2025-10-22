# backend/utils/preprocess.py
from PIL import Image
import numpy as np
from tensorflow.keras.applications.efficientnet import preprocess_input

TARGET_SIZE = (224, 224)

def preprocess_pil_image(pil_img):
    """
    Rep un PIL.Image (RGB) i retorna un numpy array shape (1, H, W, 3)
    ja preprocessat amb preprocess_input (0..255 -> model expectation).
    """
    # redimensiona mantenint ratio (a l'entrenament vas fer resize directament a (224,224))
    img = pil_img.resize(TARGET_SIZE, Image.BILINEAR)
    arr = np.array(img).astype("float32")  # 0..255
    # EfficientNet preprocess_input espera valors 0..255 i farà la seva normalització
    arr = preprocess_input(arr)
    arr = np.expand_dims(arr, axis=0)
    return arr