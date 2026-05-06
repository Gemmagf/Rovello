"""
Crea splits estratificats train/val/test a partir de inat_observations.parquet.

Sortida: ml/data/splits.parquet amb columna 'split' ∈ {train, val, test}
        ml/data/label_map.json amb {species: index}
"""
from __future__ import annotations

import json
import argparse
from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split

ROOT = Path(__file__).resolve().parents[2]
META = ROOT / "ml" / "data" / "inat_observations.parquet"
SPLITS = ROOT / "ml" / "data" / "splits.parquet"
LABEL_MAP = ROOT / "ml" / "data" / "label_map.json"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--val-frac", type=float, default=0.10)
    parser.add_argument("--test-frac", type=float, default=0.10)
    parser.add_argument("--min-per-species", type=int, default=10)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--require-images", action="store_true",
                        help="Filtra files on local_path no existeix al disc")
    args = parser.parse_args()

    df = pd.read_parquet(META)
    print(f"Carregat: {len(df):,} files, {df['species'].nunique():,} espècies")

    if args.require_images:
        before = len(df)
        df = df[df["local_path"].apply(lambda p: (ROOT / p).exists())].copy()
        print(f"Amb imatge present: {len(df):,} (descartades {before - len(df):,})")

    # Re-filtra mínim per espècie després de comprovar imatges
    counts = df.groupby("species").size()
    keep = counts[counts >= args.min_per_species].index
    df = df[df["species"].isin(keep)].copy()
    print(f"Després min {args.min_per_species}: {len(df):,} files, {df['species'].nunique():,} espècies")

    # Mapa d'etiquetes
    species_sorted = sorted(df["species"].unique())
    label_map = {sp: i for i, sp in enumerate(species_sorted)}
    df["label"] = df["species"].map(label_map)

    # Split estratificat
    train_val, test = train_test_split(
        df, test_size=args.test_frac, stratify=df["label"], random_state=args.seed
    )
    val_size = args.val_frac / (1 - args.test_frac)
    train, val = train_test_split(
        train_val, test_size=val_size, stratify=train_val["label"], random_state=args.seed
    )

    train["split"] = "train"
    val["split"] = "val"
    test["split"] = "test"
    out = pd.concat([train, val, test], ignore_index=True)

    out.to_parquet(SPLITS, index=False)
    with open(LABEL_MAP, "w") as f:
        json.dump(label_map, f, indent=2, ensure_ascii=False)

    print(f"\nTrain: {len(train):,} | Val: {len(val):,} | Test: {len(test):,}")
    print(f"Classes: {len(label_map):,}")
    print(f"Guardat: {SPLITS}, {LABEL_MAP}")


if __name__ == "__main__":
    main()
