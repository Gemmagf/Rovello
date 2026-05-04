# Rovello ML — Pipeline d'entrenament

Pipeline complet d'entrenament i inferència per Rovello. Cobreix Catalunya i Suïssa,
amb fusió bayesiana entre la predicció del CNN i un prior geo-temporal.

## Estructura

```
ml/
├── BENCHMARK.md          # estudi comparatiu d'arquitectures
├── README.md             # aquest fitxer
├── requirements.txt      # dependències Python
├── data/                 # datasets (no versionats)
│   ├── gbif_observations.parquet
│   ├── inat_observations.parquet
│   ├── splits.parquet
│   ├── label_map.json
│   └── images/<species>/<obs_id>.jpg
├── models/               # checkpoints entrenats
│   └── <run_name>/
│       ├── best.pt
│       ├── last.pt
│       ├── label_map.json
│       ├── config.json
│       └── metrics.json
├── priors/
│   ├── fusion.py                       # GeoTemporalPrior (reusable backend)
│   └── geo_temporal_prior.pkl          # KDE serialitzat
└── scripts/
    ├── 01_download_gbif.py
    ├── 02_download_inaturalist.py
    ├── 03_prepare_splits.py
    ├── 04_train.py
    ├── 05_build_prior.py
    └── train_helpers.py                # construcció de models compartida
```

## Setup (un sol cop)

```bash
# Crea entorn virtual
python3 -m venv .venv
source .venv/bin/activate

# Instal·la dependències
pip install -r ml/requirements.txt

# Verifica MPS
python -c "import torch; print('MPS:', torch.backends.mps.is_available())"
```

## Pipeline complet

### 1. Descàrrega de dades

```bash
# GBIF (només coords + data, ràpid, ~30 min)
python ml/scripts/01_download_gbif.py

# iNaturalist (imatges + meta, lent, 4-8h)
python ml/scripts/02_download_inaturalist.py --max-per-species 250 --workers 8
```

Per fer una prova ràpida:
```bash
python ml/scripts/02_download_inaturalist.py --max-per-place 500 --max-per-species 50
```

### 2. Splits estratificats

```bash
python ml/scripts/03_prepare_splits.py --require-images
```

### 3. Entrenament

**Baseline ràpid (recomanat per primer pas, 2-4h):**
```bash
python ml/scripts/04_train.py \
    --backbone convnext_tiny \
    --epochs 50 \
    --batch-size 32 \
    --num-workers 4
```

**Top performance (8-12h):**
```bash
python ml/scripts/04_train.py \
    --backbone dinov2_vitb14_lc \
    --epochs 50 \
    --batch-size 16 \
    --num-workers 4
```

**Si tens menys de 50k imatges, congela el backbone DINOv2:**
```bash
python ml/scripts/04_train.py \
    --backbone dinov2_vitb14_lc \
    --freeze-backbone \
    --epochs 30 \
    --batch-size 32 \
    --lr-head 1e-3
```

Sortida: `ml/models/<backbone>_<timestamp>/`. Crea un symlink `ml/models/best/`
apuntant al millor run per a inferència automàtica.

### 4. Construcció del prior geo-temporal

```bash
python ml/scripts/05_build_prior.py --bandwidth 0.5 --use-inat
```

### 5. Servir model + prior

```bash
# Apunta el backend al model entrenat
ln -s "$(pwd)/ml/models/convnext_tiny_XXXXXXXX_XXXXXX" ml/models/best

# Llança el servidor v2
python backend/server_v2.py
```

## Verificació ràpida

```bash
# Health
curl http://localhost:5000/health

# Predicció amb context geogràfic + temporal
curl -X POST http://localhost:5000/predict \
    -F "image=@test.jpg" \
    -F "month=10" \
    -F "lat=41.6" \
    -F "lon=2.3" \
    -F "alpha=1.0" \
    -F "beta=0.5"
```

## Hyperparàmetres ràpids per a debug

Reduir `--epochs 5` i `--max-per-species 50` per validar el pipeline en pocs minuts
abans de l'entrenament real.

## Notes sobre Apple Silicon (M4)

- PyTorch usa Metal Performance Shaders (MPS) automàticament si `torch.backends.mps.is_available()`.
- Si veus errors `MPSNDArray ... unsupported`, redueix `batch-size` o usa `--num-workers 0`.
- Mixed precision (bfloat16) està disponible a MPS via `torch.amp`. Si hi ha NaN,
  desactiva-ho o passa a `float32` complet.
- DataLoader: `pin_memory=False` és intencional (no aplica a MPS).
