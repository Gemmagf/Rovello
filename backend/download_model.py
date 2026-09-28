"""
Descarrega els fitxers del model al BUILD de Render perquè quedin cuits dins
la imatge (cap descàrrega en temps d'execució, arrencades en fred ràpides).

Build Command recomanat al dashboard de Render:
  pip install -r backend/requirements.txt && python backend/download_model.py

Per defecte baixa del GitHub Release públic v1.0-model. Es pot sobreescriure
amb env vars:
  ROVELLO_ONNX_URL       — best.onnx  (model de producció, onnxruntime)
  ROVELLO_LABEL_MAP_URL  — label_map.json
  ROVELLO_PRIOR_URL      — geo_temporal_prior.pkl
  ROVELLO_MODEL_URL      — best.pt (opcional; només si es vol el backend torch)
  ROVELLO_CONFIG_URL     — config.json (opcional)
"""
import os
import pathlib
import sys
import urllib.request

_RELEASE = "https://github.com/Gemmagf/Rovello/releases/download/v1.0-model"

ROOT = pathlib.Path(__file__).resolve().parent.parent  # arrel del repo
MODEL_DIR = ROOT / "ml" / "models" / "best"
PRIOR_DIR = ROOT / "ml" / "priors"

# (url, destí, obligatori)
FILES = [
    (os.environ.get("ROVELLO_ONNX_URL") or f"{_RELEASE}/best.onnx",
     MODEL_DIR / "best.onnx", True),
    (os.environ.get("ROVELLO_LABEL_MAP_URL") or f"{_RELEASE}/label_map.json",
     MODEL_DIR / "label_map.json", True),
    (os.environ.get("ROVELLO_PRIOR_URL") or f"{_RELEASE}/geo_temporal_prior.pkl",
     PRIOR_DIR / "geo_temporal_prior.pkl", False),  # hi ha còpia a backend/models/
    (os.environ.get("ROVELLO_CONFIG_URL") or f"{_RELEASE}/config.json",
     MODEL_DIR / "config.json", False),
    # best.pt (torch) només si s'ha demanat explícitament: pesa 114 MB i no
    # s'usa en producció (onnxruntime).
    (os.environ.get("ROVELLO_MODEL_URL", ""), MODEL_DIR / "best.pt", False),
]


def download(url: str, dest: pathlib.Path) -> bool:
    if not url:
        print(f"[SKIP] {dest.name}: sense URL")
        return False
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() and dest.stat().st_size > 0:
        print(f"[OK] {dest.name} ja existeix ({dest.stat().st_size / 1e6:.1f} MB)")
        return True
    print(f"[DL] {url} → {dest}")
    tmp = dest.with_suffix(dest.suffix + ".part")
    try:
        urllib.request.urlretrieve(url, tmp)
        tmp.replace(dest)
        print(f"[OK] {dest.name} descarregat ({dest.stat().st_size / 1e6:.1f} MB)")
        return True
    except Exception as e:
        print(f"[ERR] {dest.name}: {e}", file=sys.stderr)
        tmp.unlink(missing_ok=True)
        return False


if __name__ == "__main__":
    ok = True
    for url, dest, required in FILES:
        got = download(url, dest)
        if required and not got:
            ok = False
    if not ok:
        print("\n⚠️  Falten fitxers obligatoris (best.onnx / label_map.json).", file=sys.stderr)
        sys.exit(1)
    print("\n✅ Model llest dins la imatge de build.")
