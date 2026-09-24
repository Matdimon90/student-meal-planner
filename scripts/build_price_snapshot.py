"""Build the price snapshot used by the app, for one supermarket.

Reads one day of OpenCesta price data (a Parquet file) and keeps only the
products listed in data/skus_<chain>.csv, described in data/staples.csv.
The result is a small CSV that we commit, so the app never depends on a live
supermarket API.

Usage:
    python3 scripts/build_price_snapshot.py data/raw/data/chain=mercadona/zone=mad1/date=2026-09-21/prices.parquet
    python3 scripts/build_price_snapshot.py data/raw/data/chain=dia/zone=es-default/date=2026-09-21/prices.parquet

The chain is read from the Parquet file, and the matching data/skus_<chain>.csv
must exist. An ingredient with an empty SKU is left out of that supermarket's
snapshot (the shop does not sell it): the app then says so instead of guessing.

See data/README.md for where the Parquet files come from.
"""

import sys
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parent.parent
STAPLES_PATH = REPO_ROOT / "data" / "staples.csv"

# OpenCesta writes reference prices per "kg", "L" or "ud". Our snapshot uses lower case.
FORMAT_NAMES = {"kg": "kg", "l": "l", "ud": "ud"}


def build_snapshot(parquet_path: Path) -> Path:
    prices = pd.read_parquet(parquet_path)
    prices["sku"] = prices["sku"].astype(str)
    chain = str(prices["chain"].iloc[0])
    zone = str(prices["zone"].iloc[0])
    date = str(prices["captured_at"].iloc[0])

    skus_path = REPO_ROOT / "data" / f"skus_{chain}.csv"
    if not skus_path.exists():
        raise SystemExit(f"No SKU mapping for chain '{chain}': expected {skus_path.relative_to(REPO_ROOT)}")
    staples = pd.read_csv(STAPLES_PATH, dtype=str, keep_default_na=False)
    skus = pd.read_csv(skus_path, dtype=str, keep_default_na=False)
    skus = skus[skus["sku"] != ""]

    # Every SKU we chose must exist in the price file. If one is missing
    # (the shop removed it, or we typed it wrong) we stop instead of silently
    # producing a snapshot with holes in it.
    missing = sorted(set(skus["sku"]) - set(prices["sku"]))
    if missing:
        raise SystemExit(f"SKUs not found in {parquet_path.name}: {missing}")

    merged = staples.merge(skus, on="ingredient_id", how="inner").merge(prices, on="sku", how="left", validate="one_to_one")

    # Package size: from the file when it has one (Mercadona), otherwise derived
    # from the price per kg / L / unit (Dia), otherwise from our mapping file.
    # Dia gives no package size, only the price per kg / L / unit: 0.55 EUR at 1.38 EUR/kg
    # is a 0.399 kg can, which is the 400 g can everyone knows. Round to the cent of a kg
    # above 100 g, to the gram below (spices).
    derived_size = merged["unit_price"] / merged["reference_price"]
    derived_size = derived_size.where(derived_size < 0.1, derived_size.round(2)).round(3)
    derived_unit = merged["reference_format"].astype(str).str.lower().map(FORMAT_NAMES)
    size = merged["unit_size"].astype(float)
    unit = merged["size_format"].astype(str).str.lower().replace({"nan": None, "": None})
    size = size.where(size.notna(), derived_size)
    unit = unit.where(unit.notna(), derived_unit)
    override = merged["package_size"] != ""
    size = size.where(~override, pd.to_numeric(merged["package_size"], errors="coerce"))
    unit = unit.where(~override, merged["package_unit"])

    bad = merged[size.isna() | unit.isna() | ~unit.isin(FORMAT_NAMES)]
    if len(bad):
        raise SystemExit("Could not work out a package size for: " + ", ".join(bad["ingredient_id"]))

    snapshot = pd.DataFrame(
        {
            "ingredient_id": merged["ingredient_id"],
            "name_en": merged["name_en"],
            "name_es": merged["name_es"],
            "category": merged["category_x"],
            "diet": merged["diet"],
            "allergens": merged["allergens"],
            "piece_grams": merged["piece_grams"],
            "package_price_eur": merged["unit_price"].round(2),
            "package_size": size,
            "package_unit": unit,
            "supermarket": chain,
            "zone": zone,
            "sku": merged["sku"],
            "product_name": merged["display_name"],
            "captured_at": date,
            "product_url": merged["url"],
        }
    )

    out_path = REPO_ROOT / "data" / f"prices_{chain}_{zone}_{date}.csv"
    snapshot.to_csv(out_path, index=False)
    return out_path


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    out = build_snapshot(Path(sys.argv[1]))
    print(f"Wrote {out.relative_to(REPO_ROOT)}")
