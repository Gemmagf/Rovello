"""
Descarrega el model i el prior des d'URLs configurables via env vars.
S'executa durant el build de Render (buildCommand).

Env vars necessàries al dashboard de Render:
  ROVELLO_MODEL_URL  — URL directa al best.pt (GitHub Release asset, etc.)
  ROVELLO_PRIOR_URL  — URL directa al geo_temporal_prior.pkl
"""
import os
import pathlib
import urllib.request
import sys

MODEL_URL = os.environ.get("ROVELLO_MODEL_URL", "")
PRIOR_URL = os.environ.get("ROVELLO_PRIOR_URL", "")

MODEL_PATH = pathlib.Path("ml/models/best/best.pt")
LABEL_MAP_PATH = pathlib.Path("ml/models/best/label_map.json")
CONFIG_PATH = pathlib.Path("ml/models/best/config.json")
PRIOR_PATH = pathlib.Path("ml/priors/geo_temporal_prior.pkl")

LABEL_MAP_URL = os.environ.get("ROVELLO_LABEL_MAP_URL", "")
CONFIG_URL = os.environ.get("ROVELLO_CONFIG_URL", "")


def download(url: str, dest: pathlib.Path) -> bool:
    if not url:
        print(f"[SKIP] No URL configurada per a {dest.name}")
        return False
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        print(f"[OK] {dest.name} ja existeix ({dest.stat().st_size // 1024 // 1024} MB)")
        return True
    print(f"[DL] {url} → {dest}")
    try:
        urllib.request.urlretrieve(url, dest)
        mb = dest.stat().st_size / 1024 / 1024
        print(f"[OK] {dest.name} descarregat ({mb:.1f} MB)")
        return True
    except Exception as e:
        print(f"[ERR] No s'ha pogut descarregar {dest.name}: {e}", file=sys.stderr)
        return False


if __name__ == "__main__":
    ok = True
    ok &= download(MODEL_URL, MODEL_PATH)
    ok &= download(PRIOR_URL, PRIOR_PATH)
    download(LABEL_MAP_URL, LABEL_MAP_PATH)
    download(CONFIG_URL, CONFIG_PATH)

    if not ok:
        print("\n⚠️  Configura ROVELLO_MODEL_URL i ROVELLO_PRIOR_URL al dashboard de Render.")
        sys.exit(1)

    print("\n✅ Model i prior llestos.")
