"""Build the price snapshot used by the app.

Reads one day of OpenCesta price data (a Parquet file) and keeps only the
products listed in data/staples.csv. The result is a small CSV that we commit,
so the app never depends on a live supermarket API.

Usage:
    python3 scripts/build_price_snapshot.py data/raw/prices.parquet

See data/README.md for where the Parquet file comes from.
"""

import sys
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parent.parent
STAPLES_PATH = REPO_ROOT / "data" / "staples.csv"


def build_snapshot(parquet_path: Path) -> Path:
    prices = pd.read_parquet(parquet_path)
    staples = pd.read_csv(STAPLES_PATH, dtype=str, keep_default_na=False)

    # Every product we chose must exist in the price file. If one is missing
    # (Mercadona removed it, or we typed the SKU wrong) we stop instead of
    # silently producing a snapshot with holes in it.
    missing = sorted(set(staples["sku"]) - set(prices["sku"]))
    if missing:
        raise SystemExit(f"SKUs not found in {parquet_path.name}: {missing}")

    merged = staples.merge(prices, on="sku", how="left", validate="one_to_one")

    snapshot = pd.DataFrame(
        {
            "ingredient_id": merged["ingredient_id"],
            "name_en": merged["name_en"],
            "name_es": merged["name_es"],
            "category": merged["category_x"],
            "diet": merged["diet"],
            "allergens": merged["allergens"],
            "package_price_eur": merged["unit_price"].round(2),
            "package_size": merged["unit_size"],
            "package_unit": merged["size_format"],
            "supermarket": merged["chain"],
            "zone": merged["zone"],
            "sku": merged["sku"],
            "product_name": merged["display_name"],
            "captured_at": merged["captured_at"],
            "product_url": merged["url"],
        }
    )

    chain = snapshot["supermarket"].iloc[0]
    zone = snapshot["zone"].iloc[0]
    date = snapshot["captured_at"].iloc[0]
    out_path = REPO_ROOT / "data" / f"prices_{chain}_{zone}_{date}.csv"
    snapshot.to_csv(out_path, index=False)
    return out_path


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    out = build_snapshot(Path(sys.argv[1]))
    print(f"Wrote {out.relative_to(REPO_ROOT)}")
