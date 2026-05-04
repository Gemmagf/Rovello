"""
Descàrrega d'imatges + metadades d'iNaturalist (research-grade) per Fungi
a Catalunya i Suïssa.

iNaturalist API: https://api.inaturalist.org/v1/observations

Place IDs:
    Catalonia: 7204
    Switzerland: 7236

Sortida:
    ml/data/inat_observations.parquet  (índex amb metadades)
    ml/data/images/<species>/<obs_id>.jpg  (imatges)

Ús:
    python ml/scripts/02_download_inaturalist.py --max-per-species 200
    python ml/scripts/02_download_inaturalist.py --species "Boletus edulis"
"""
from __future__ import annotations

import os
import sys
import time
import argparse
import hashlib
import json
import re
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
import pandas as pd
from tqdm import tqdm

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "ml" / "data"
IMG_DIR = DATA_DIR / "images"
META_OUT = DATA_DIR / "inat_observations.parquet"

INAT_BASE = "https://api.inaturalist.org/v1/observations"
PLACES = {
    "catalunya": 61614,    # iNat: "Catalunya, ES" — verificat 11.454 obs research+photos
    "switzerland": 7236,   # iNat: "Switzerland"  — verificat 52.864 obs research+photos
}
PER_PAGE = 200
TAXON_FUNGI = 47170  # Kingdom Fungi
USER_AGENT = "RovelloML/1.0 (educational mushroom classifier)"

session = requests.Session()
session.headers.update({"User-Agent": USER_AGENT})


def safe_name(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9_-]+", "_", name).strip("_")


def fetch_observations(place_id: int, max_records: int | None = None):
    """Fetch llista d'observacions metadades (paginació via id_above)."""
    id_above = 0
    pbar = None
    fetched = 0
    while True:
        params = {
            "place_id": place_id,
            "taxon_id": TAXON_FUNGI,
            "quality_grade": "research",
            "photos": "true",
            "per_page": PER_PAGE,
            "order_by": "id",
            "order": "asc",
            "id_above": id_above,
        }
        for attempt in range(5):
            try:
                r = session.get(INAT_BASE, params=params, timeout=60)
                if r.status_code == 429:
                    time.sleep(60)
                    continue
                r.raise_for_status()
                break
            except requests.RequestException as e:
                wait = 2 ** attempt
                print(f"  [retry {attempt+1}/5 in {wait}s] {e}", file=sys.stderr)
                time.sleep(wait)
        else:
            print("  Falla persistent.", file=sys.stderr)
            return

        data = r.json()
        results = data.get("results", [])
        if not results:
            break
        if pbar is None:
            total_count = data.get("total_results", 0)
            cap = total_count if max_records is None else min(total_count, max_records)
            pbar = tqdm(total=cap, desc=f"iNat place={place_id}", unit="obs")

        for obs in results:
            yield obs
            id_above = max(id_above, obs["id"])
            fetched += 1
            pbar.update(1)
            if max_records is not None and fetched >= max_records:
                pbar.close()
                return

        # iNat respect: max ~60 req/min
        time.sleep(1.0)

    if pbar:
        pbar.close()


def extract_meta(obs: dict) -> dict | None:
    taxon = obs.get("taxon") or {}
    if not taxon.get("name"):
        return None
    rank = taxon.get("rank")
    if rank not in ("species", "subspecies", "variety"):
        return None  # només espècies (i sota)
    species = taxon["name"]

    geo = obs.get("geojson") or {}
    coords = geo.get("coordinates") if geo else None
    if not coords or len(coords) != 2:
        return None
    lon, lat = coords

    observed_on = obs.get("observed_on_details") or {}
    month = observed_on.get("month")
    year = observed_on.get("year")
    if month is None:
        return None

    photos = obs.get("photos", [])
    if not photos:
        return None

    # URL de mida 'medium' (~500px) per balanç qualitat/mida
    photo_urls = []
    for p in photos:
        url = p.get("url")
        if not url:
            continue
        # iNat retorna mida 'square'; canviem a 'medium'
        url = url.replace("/square.", "/medium.")
        photo_urls.append(url)

    if not photo_urls:
        return None

    return {
        "obs_id": obs["id"],
        "species": species,
        "taxon_id": taxon.get("id"),
        "lat": float(lat),
        "lon": float(lon),
        "month": int(month),
        "year": int(year) if year else None,
        "photo_urls": photo_urls,
    }


def download_image(url: str, dest: Path) -> bool:
    if dest.exists() and dest.stat().st_size > 1000:
        return True
    try:
        r = session.get(url, timeout=30, stream=True)
        if r.status_code != 200:
            return False
        dest.parent.mkdir(parents=True, exist_ok=True)
        with open(dest, "wb") as f:
            for chunk in r.iter_content(8192):
                f.write(chunk)
        return dest.stat().st_size > 1000
    except Exception:
        return False


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-per-place", type=int, default=None,
                        help="Límit total observacions per lloc (debug)")
    parser.add_argument("--max-per-species", type=int, default=200,
                        help="Màxim imatges per espècie (per evitar desbalanceig)")
    parser.add_argument("--workers", type=int, default=8,
                        help="Threads per descarregar imatges")
    parser.add_argument("--skip-images", action="store_true",
                        help="Només metadades, sense descarregar imatges")
    parser.add_argument("--min-per-species", type=int, default=10,
                        help="Espècies amb menys exemples es descarten")
    args = parser.parse_args()

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    IMG_DIR.mkdir(parents=True, exist_ok=True)

    # 1) Recol·lectar metadades
    metas = []
    for place_name, place_id in PLACES.items():
        print(f"\n>>> Lloc: {place_name} (id={place_id})")
        for obs in fetch_observations(place_id, max_records=args.max_per_place):
            meta = extract_meta(obs)
            if meta:
                meta["place"] = place_name
                metas.append(meta)

    df = pd.DataFrame(metas)
    print(f"\nObs. amb metadades vàlides: {len(df):,}")
    print(f"Espècies úniques: {df['species'].nunique():,}")

    # 2) Filtrar espècies amb pocs exemples
    counts = df.groupby("species").size()
    keep = counts[counts >= args.min_per_species].index
    df = df[df["species"].isin(keep)].copy()
    print(f"Després filtre min {args.min_per_species}: {len(df):,} obs / {df['species'].nunique():,} espècies")

    # 3) Cap per espècie (anti-desbalanceig)
    df = df.groupby("species", group_keys=False).apply(
        lambda g: g.head(args.max_per_species)
    ).reset_index(drop=True)
    print(f"Després cap {args.max_per_species}/sp: {len(df):,} obs")

    # Guarda metadades (1 fila per imatge a descarregar)
    rows = []
    for _, r in df.iterrows():
        # Una fila per foto (sols la primera de cada obs per defecte)
        url = r["photo_urls"][0]
        species = r["species"]
        sp_dir = IMG_DIR / safe_name(species)
        local = sp_dir / f"{r['obs_id']}.jpg"
        rows.append({
            "obs_id": r["obs_id"],
            "species": species,
            "lat": r["lat"],
            "lon": r["lon"],
            "month": r["month"],
            "year": r["year"],
            "place": r["place"],
            "photo_url": url,
            "local_path": str(local.relative_to(ROOT)),
        })
    df_out = pd.DataFrame(rows)
    df_out.to_parquet(META_OUT, index=False)
    print(f"\nMetadades guardades: {META_OUT}")

    if args.skip_images:
        print("--skip-images: no descarrego imatges.")
        return

    # 4) Descarregar imatges en paral·lel
    print(f"\n>>> Descarregant {len(df_out):,} imatges amb {args.workers} workers...")
    todo = [(r["photo_url"], ROOT / r["local_path"]) for _, r in df_out.iterrows()]
    success = 0
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futures = {ex.submit(download_image, url, dest): (url, dest) for url, dest in todo}
        for fut in tqdm(as_completed(futures), total=len(futures), desc="imatges"):
            if fut.result():
                success += 1
    print(f"\nImatges descarregades amb èxit: {success:,}/{len(todo):,}")


if __name__ == "__main__":
    main()
