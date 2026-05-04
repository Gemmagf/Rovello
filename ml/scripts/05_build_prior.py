"""
Construeix el prior P(espècie | mes, lat, lon) a partir d'observacions GBIF.

Mètode: KDE per espècie sobre [lat, lon, sin(mes), cos(mes)] amb suavitzat
        de Laplace per espècies amb poques observacions.

Sortida: ml/priors/geo_temporal_prior.npz
        - species: array de noms (ordenat segons label_map.json)
        - kde_models: KDE serialitzat per espècie
        - global_density: KDE global (per a denominador / fallback)
        - laplace_alpha: param d'estabilització
"""
from __future__ import annotations

import json
import argparse
import pickle
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.neighbors import KernelDensity
from tqdm import tqdm

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "ml" / "data"
PRIORS_DIR = ROOT / "ml" / "priors"

GBIF_FILE = DATA_DIR / "gbif_observations.parquet"
INAT_FILE = DATA_DIR / "inat_observations.parquet"
LABEL_MAP_FILE = DATA_DIR / "label_map.json"


def encode(df: pd.DataFrame) -> np.ndarray:
    """[lat, lon, sin(2π·mes/12), cos(2π·mes/12)]."""
    angle = 2 * np.pi * df["month"].astype(float).to_numpy() / 12.0
    return np.column_stack([
        df["lat"].to_numpy(),
        df["lon"].to_numpy(),
        np.sin(angle),
        np.cos(angle),
    ])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--bandwidth", type=float, default=0.5,
                        help="Bandwidth KDE (graus aprox. + freq. mensual)")
    parser.add_argument("--min-obs", type=int, default=5,
                        help="Espècies amb menys observacions usen prior global suavitzat")
    parser.add_argument("--laplace-alpha", type=float, default=1e-3,
                        help="Suavitzat additiu sobre densitats")
    parser.add_argument("--use-inat", action="store_true", default=True,
                        help="(default) Inclou observacions iNaturalist")
    parser.add_argument("--no-inat", dest="use_inat", action="store_false",
                        help="Desactiva ús d'iNaturalist (només GBIF)")
    parser.add_argument("--use-gbif", action="store_true", default=False,
                        help="Inclou GBIF (si està disponible)")
    args = parser.parse_args()

    PRIORS_DIR.mkdir(parents=True, exist_ok=True)

    with open(LABEL_MAP_FILE) as f:
        label_map = json.load(f)
    species_list = sorted(label_map, key=lambda s: label_map[s])
    species_set = set(species_list)

    # Carregar observacions
    dfs = []
    if args.use_gbif and GBIF_FILE.exists():
        gdf = pd.read_parquet(GBIF_FILE)
        gdf = gdf[gdf["species"].isin(species_set)].copy()
        print(f"GBIF: {len(gdf):,} obs en classes objectiu")
        dfs.append(gdf[["species", "lat", "lon", "month"]])
    if args.use_inat and INAT_FILE.exists():
        idf = pd.read_parquet(INAT_FILE)
        idf = idf[idf["species"].isin(species_set)].copy()
        print(f"iNat:  {len(idf):,} obs en classes objectiu")
        dfs.append(idf[["species", "lat", "lon", "month"]])

    if not dfs:
        raise SystemExit("No hi ha dades GBIF ni iNat per construir el prior.")

    df = pd.concat(dfs, ignore_index=True).dropna()

    # KDE global (fallback per espècies amb poques observacions)
    X_all = encode(df)
    print(f"\nAjustant KDE global ({len(X_all):,} punts)...")
    kde_global = KernelDensity(bandwidth=args.bandwidth, kernel="gaussian")
    kde_global.fit(X_all)

    # KDE per espècie
    kdes = {}
    counts = {}
    print(f"Ajustant KDE per espècie...")
    for sp in tqdm(species_list):
        sub = df[df["species"] == sp]
        counts[sp] = len(sub)
        if len(sub) >= args.min_obs:
            X = encode(sub)
            kde = KernelDensity(bandwidth=args.bandwidth, kernel="gaussian")
            kde.fit(X)
            kdes[sp] = kde
        else:
            kdes[sp] = None  # senyala usar el global

    out = {
        "species_list": species_list,
        "kdes": kdes,
        "kde_global": kde_global,
        "counts": counts,
        "bandwidth": args.bandwidth,
        "laplace_alpha": args.laplace_alpha,
    }
    out_path = PRIORS_DIR / "geo_temporal_prior.pkl"
    with open(out_path, "wb") as f:
        pickle.dump(out, f)

    n_with_kde = sum(1 for v in kdes.values() if v is not None)
    print(f"\nPrior guardat a: {out_path}")
    print(f"Espècies amb KDE propi: {n_with_kde}/{len(species_list)}")
    print(f"Espècies amb fallback global: {len(species_list) - n_with_kde}")


if __name__ == "__main__":
    main()
