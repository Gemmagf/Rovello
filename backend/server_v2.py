"""
Servidor Flask v2 amb:
  - Backend PyTorch (preferit) o TensorFlow (fallback).
  - Fusió bayesiana amb prior geo-temporal opcional.
  - Endpoint /predict accepta camps multipart: image, month, lat, lon, alpha, beta.

Variables d'entorn:
  ROVELLO_MODEL_BACKEND  = "torch" | "tf"        (default: "torch" si disponible)
  ROVELLO_MODEL_PATH     = path al checkpoint     (default: ml/models/best/best.pt)
  ROVELLO_PRIOR_PATH     = path al prior          (default: ml/priors/geo_temporal_prior.pkl)
  ROVELLO_DEFAULT_ALPHA  = pes de la imatge        (default: 1.0)
  ROVELLO_DEFAULT_BETA   = pes del prior           (default: 0.5)

Ús:
  python backend/server_v2.py
"""
from __future__ import annotations

import io
import os
import sys
import json
import logging
from pathlib import Path

import numpy as np
from PIL import Image
from flask import Flask, request, jsonify
from flask_cors import CORS

# ----------------------------------------------------------------------------
# Logging estructurat
# ----------------------------------------------------------------------------
logging.basicConfig(
    level=os.environ.get("ROVELLO_LOG_LEVEL", "INFO"),
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
log = logging.getLogger("rovello")

# ----------------------------------------------------------------------------
# Paths
# ----------------------------------------------------------------------------
BACKEND_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BACKEND_DIR.parent

DEFAULT_TORCH_MODEL = PROJECT_ROOT / "ml" / "models" / "best" / "best.pt"
DEFAULT_TF_MODEL = BACKEND_DIR / "models" / "mushroom_model.h5"
DEFAULT_LE = BACKEND_DIR / "models" / "label_encoder.pkl"
DEFAULT_PRIOR = PROJECT_ROOT / "ml" / "priors" / "geo_temporal_prior.pkl"

MODEL_BACKEND = os.environ.get("ROVELLO_MODEL_BACKEND", "torch").lower()
MODEL_PATH = Path(os.environ.get("ROVELLO_MODEL_PATH", DEFAULT_TORCH_MODEL))
PRIOR_PATH = Path(os.environ.get("ROVELLO_PRIOR_PATH", DEFAULT_PRIOR))
DEFAULT_ALPHA = float(os.environ.get("ROVELLO_DEFAULT_ALPHA", "1.0"))
DEFAULT_BETA = float(os.environ.get("ROVELLO_DEFAULT_BETA", "0.5"))

# ----------------------------------------------------------------------------
# Càrrega del model (lazy: detecta backend disponible)
# ----------------------------------------------------------------------------
class TorchInference:
    def __init__(self, ckpt_path: Path):
        import torch
        from torchvision import transforms
        sys.path.insert(0, str(PROJECT_ROOT))
        from ml.scripts.train_helpers import build_model_for_inference  # type: ignore

        self.torch = torch
        self.device = (
            torch.device("mps") if torch.backends.mps.is_available()
            else torch.device("cuda") if torch.cuda.is_available()
            else torch.device("cpu")
        )
        log.info(f"PyTorch device: {self.device}")

        ckpt = torch.load(ckpt_path, map_location=self.device)
        backbone = ckpt["backbone"]
        num_classes = ckpt["num_classes"]
        img_size = ckpt.get("img_size", 224)
        self.model = build_model_for_inference(backbone, num_classes)
        self.model.load_state_dict(ckpt["model"])
        self.model.eval().to(self.device)
        self.img_size = img_size

        # Carrega label_map per mapejar índex -> nom espècie
        lm_path = ckpt_path.parent / "label_map.json"
        if not lm_path.exists():
            raise FileNotFoundError(f"Falta label_map.json a {lm_path}")
        with open(lm_path) as f:
            label_map = json.load(f)
        # invertit: index -> nom (label_map és nom -> index)
        self.idx_to_class = [None] * len(label_map)
        for sp, i in label_map.items():
            self.idx_to_class[i] = sp

        self.transform = transforms.Compose([
            transforms.Resize(int(img_size * 1.14)),
            transforms.CenterCrop(img_size),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
        ])

    def predict_probs(self, pil_img: Image.Image) -> np.ndarray:
        x = self.transform(pil_img).unsqueeze(0).to(self.device)
        with self.torch.no_grad():
            logits = self.model(x)
            probs = self.torch.softmax(logits, dim=1)[0].cpu().numpy()
        return probs


class TFInference:
    """Fallback: utilitza el model EfficientNet .h5 antic."""
    def __init__(self, model_path: Path, le_path: Path):
        import tensorflow as tf  # type: ignore
        import pickle
        sys.path.insert(0, str(BACKEND_DIR))
        from utils.preprocess import preprocess_pil_image  # type: ignore

        self.model = tf.keras.models.load_model(str(model_path), compile=False)
        with open(le_path, "rb") as f:
            le = pickle.load(f)
        self.idx_to_class = list(le.classes_)
        self._preprocess = preprocess_pil_image
        log.info(f"TF model carregat: {len(self.idx_to_class)} classes")

    def predict_probs(self, pil_img: Image.Image) -> np.ndarray:
        inp = self._preprocess(pil_img)
        preds = self.model.predict(inp, verbose=0)
        return preds[0]


def load_inference():
    """Tria backend disponible. Prefereix Torch si MODEL_PATH existeix."""
    if MODEL_BACKEND == "torch" and MODEL_PATH.exists():
        log.info(f"Carregant Torch model: {MODEL_PATH}")
        return TorchInference(MODEL_PATH)
    if DEFAULT_TF_MODEL.exists():
        log.info(f"Carregant TF model (fallback): {DEFAULT_TF_MODEL}")
        return TFInference(DEFAULT_TF_MODEL, DEFAULT_LE)
    raise SystemExit(
        f"No hi ha cap model disponible. Esperava {MODEL_PATH} (torch) o "
        f"{DEFAULT_TF_MODEL} (tf)."
    )


def load_prior():
    if not PRIOR_PATH.exists():
        log.warning(f"Prior geo-temporal no trobat a {PRIOR_PATH} — la fusió estarà desactivada.")
        return None
    sys.path.insert(0, str(PROJECT_ROOT))
    from ml.priors.fusion import GeoTemporalPrior  # type: ignore
    log.info(f"Carregant prior geo-temporal: {PRIOR_PATH}")
    return GeoTemporalPrior.load(PRIOR_PATH)


# ----------------------------------------------------------------------------
# Inicialització
# ----------------------------------------------------------------------------
log.info("Inicialitzant servidor Rovello v2...")
INFER = load_inference()
PRIOR = load_prior()

# Verifica que prior i model usen el mateix label_map (si tots dos existeixen)
if PRIOR is not None and INFER.idx_to_class != PRIOR.species_list:
    log.warning(
        "ATENCIÓ: ordre de classes del model i del prior no coincideix. "
        "Re-entrena el prior amb el label_map.json del model."
    )

APP = Flask(__name__)
CORS(APP)


# ----------------------------------------------------------------------------
# Endpoints
# ----------------------------------------------------------------------------
@APP.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "backend": "torch" if isinstance(INFER, TorchInference) else "tf",
        "classes": len(INFER.idx_to_class),
        "prior_loaded": PRIOR is not None,
    })


@APP.route("/predict", methods=["POST"])
def predict():
    if "image" not in request.files:
        return jsonify({"error": "No image file in request (field 'image')"}), 400

    file = request.files["image"]
    try:
        img = Image.open(file.stream).convert("RGB")
    except Exception as e:
        log.exception("Imatge invàlida")
        return jsonify({"error": "Invalid image", "detail": str(e)}), 400

    # Camps opcionals de context
    def _opt_float(name):
        v = request.form.get(name)
        if v is None or v == "":
            return None
        try:
            return float(v)
        except ValueError:
            return None

    def _opt_int(name):
        v = request.form.get(name)
        if v is None or v == "":
            return None
        try:
            return int(v)
        except ValueError:
            return None

    month = _opt_int("month")
    lat = _opt_float("lat")
    lon = _opt_float("lon")
    alpha = _opt_float("alpha") or DEFAULT_ALPHA
    beta = _opt_float("beta")
    if beta is None:
        beta = DEFAULT_BETA

    try:
        image_probs = INFER.predict_probs(img)
    except Exception as e:
        log.exception("Error d'inferència")
        return jsonify({"error": "Inference error", "detail": str(e)}), 500

    use_prior = (
        PRIOR is not None
        and month is not None and lat is not None and lon is not None
        and beta > 0
    )

    if use_prior:
        try:
            fused = PRIOR.fuse(image_probs, month=month, lat=lat, lon=lon,
                               alpha=alpha, beta=beta)
            priors = PRIOR.prior_probs(month, lat, lon)
        except Exception as e:
            log.exception("Error en fusió bayesiana, retornant només imatge")
            fused = image_probs
            priors = None
    else:
        fused = image_probs
        priors = None

    k = min(5, len(fused))
    top_idx = np.argsort(-fused)[:k]
    predictions = []
    for i in top_idx:
        item = {
            "class_index": int(i),
            "class_name": INFER.idx_to_class[int(i)],
            "prob": float(fused[int(i)]),
            "image_prob": float(image_probs[int(i)]),
        }
        if priors is not None:
            item["prior_prob"] = float(priors[int(i)])
        predictions.append(item)

    response = {
        "predictions": predictions,
        "num_classes": len(INFER.idx_to_class),
        "context_used": use_prior,
    }
    if use_prior:
        response["context"] = {
            "month": month, "lat": lat, "lon": lon, "alpha": alpha, "beta": beta
        }
    log.info(
        f"predict: top1={predictions[0]['class_name']} "
        f"prob={predictions[0]['prob']:.3f} context={use_prior}"
    )
    return jsonify(response)


@APP.route("/species", methods=["GET"])
def species():
    """Llista de totes les espècies que el model pot predir."""
    return jsonify({"species": INFER.idx_to_class})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    APP.run(host="0.0.0.0", port=port, debug=False)
