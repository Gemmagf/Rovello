"""
Descàrrega d'observacions GBIF de Fungi a Catalunya + Suïssa.
Usat per construir el prior geo-temporal P(espècie | mes, lat, lon).

GBIF API docs: https://www.gbif.org/developer/occurrence

Sortida: ml/data/gbif_observations.parquet
        amb columnes: species, lat, lon, month, year, country, basisOfRecord

Ús:
    python ml/scripts/01_download_gbif.py
"""
from __future__ import annotations

import os
import sys
import time
import json
import argparse
from pathlib import Path
from typing import Iterator

import requests
import pandas as pd
from tqdm import tqdm

GBIF_BASE = "https://api.gbif.org/v1/occurrence/search"
PAGE_SIZE = 300  # màxim permès
ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "ml" / "data" / "gbif_observations.parquet"

# Filtres: Fungi, Catalunya (bbox, perquè stateProvince no està normalitzat) + Suïssa
# Bbox Catalunya: lon 0.15..3.4, lat 40.5..42.9
QUERIES = [
    {
        "name": "Catalunya (bbox)",
        "kingdomKey": 5,
        "country": "ES",
        "decimalLongitude": "0.15,3.4",
        "decimalLatitude": "40.5,42.9",
        "hasCoordinate": "true",
        "hasGeospatialIssue": "false",
    },
    {
        "name": "Switzerland",
        "kingdomKey": 5,
        "country": "CH",
        "hasCoordinate": "true",
        "hasGeospatialIssue": "false",
    },
]


def gbif_iter(params: dict, max_records: int | None = None) -> Iterator[dict]:
    """Itera per totes les pàgines GBIF respectant la quota."""
    params = dict(params)  # còpia per no mutar l'original
    name = params.pop("name", params.get("country", "?"))
    offset = 0
    total = None
    pbar = None
    while True:
        q = {**params, "limit": PAGE_SIZE, "offset": offset}
        for attempt in range(5):
            try:
                r = requests.get(GBIF_BASE, params=q, timeout=60)
                r.raise_for_status()
                break
            except requests.RequestException as e:
                wait = 2 ** attempt
                print(f"  [retry {attempt+1}/5 in {wait}s] {e}", file=sys.stderr)
                time.sleep(wait)
        else:
            print("  Falla persistent, abandonant aquest filtre.", file=sys.stderr)
            return

        data = r.json()
        if total is None:
            total = data.get("count", 0)
            cap = total if max_records is None else min(total, max_records)
            pbar = tqdm(total=cap, desc=f"GBIF {name}", unit="obs")

        for rec in data.get("results", []):
            yield rec
            if pbar is not None:
                pbar.update(1)
            if max_records is not None and pbar is not None and pbar.n >= max_records:
                pbar.close()
                return

        if data.get("endOfRecords", True):
            break
        offset += PAGE_SIZE

    if pbar is not None:
        pbar.close()


def parse_record(rec: dict) -> dict | None:
    """Extreu camps rellevants. Retorna None si falten dades crítiques."""
    species = rec.get("species") or rec.get("acceptedScientificName")
    lat = rec.get("decimalLatitude")
    lon = rec.get("decimalLongitude")
    month = rec.get("month")
    year = rec.get("year")
    country = rec.get("countryCode")
    basis = rec.get("basisOfRecord")
    if not species or lat is None or lon is None or month is None:
        return None
    return {
        "species": species,
        "lat": float(lat),
        "lon": float(lon),
        "month": int(month),
        "year": int(year) if year else None,
        "country": country,
        "basisOfRecord": basis,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-per-query", type=int, default=None,
                        help="Limit registres per query (debug)")
    parser.add_argument("--year-from", type=int, default=1990)
    parser.add_argument("--year-to", type=int, default=2026)
    parser.add_argument("--year-chunk", type=int, default=5,
                        help="Mida del bucket d'anys (per saltar el límit 100k de GBIF)")
    args = parser.parse_args()

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    # Fragmentar per any per saltar el límit de 100k registres de l'API search
    rows = []
    for q in QUERIES:
        for y0 in range(args.year_from, args.year_to + 1, args.year_chunk):
            y1 = min(y0 + args.year_chunk - 1, args.year_to)
            year_q = {**q, "year": f"{y0},{y1}", "name": f"{q['name']} {y0}-{y1}"}
            print(f"\n>>> Query: {year_q}")
            for rec in gbif_iter(year_q, max_records=args.max_per_query):
                parsed = parse_record(rec)
                if parsed is not None:
                    rows.append(parsed)

    df = pd.DataFrame(rows)
    print(f"\nTotal observacions vàlides: {len(df):,}")
    print(f"Espècies úniques: {df['species'].nunique():,}")
    print(f"Per país: {df['country'].value_counts().to_dict()}")

    df.to_parquet(OUTPUT, index=False)
    print(f"\nGuardat a: {OUTPUT}")


if __name__ == "__main__":
    main()
