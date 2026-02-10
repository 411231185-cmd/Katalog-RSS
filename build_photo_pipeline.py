#!/usr/bin/env python3
import csv
import re
from pathlib import Path
from typing import Dict, List, Tuple

BASE = Path(r"C:\GitHub-Repositories\Katalog-RSS")
PREFIKSY_TXT = BASE / "ПРЕФИКСЫ ВСЕ.txt"
SPISOK_FOTO_CSV = BASE / "список_фото_для_тильды.csv"
SLOVAR_PREF_TXT = BASE / "slovari" / "SLOVAR-PREFIKSOV-offery.txt"
OFFERS_KIR_DIR = Path(r"C:\Users\User\OneDrive\Рабочий стол\Офферы-подписанные")

OUTPUT_MATCHED = BASE / "photos_matched.csv"
OUTPUT_UNMATCHED = BASE / "photos_unmatched.csv"

PLACEHOLDER_PATTERNS = [
    "black", "stub", "placeholder", "no-photo", "nopicture", "noimage",
    "generated-image", "generated_image", "default", "sample", "tmp"
]

def load_prefix_descriptions(path: Path) -> Dict[str, str]:
    prefix_desc = {}
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if " - " in line:
                pref, desc = line.split(" - ", 1)
                prefix_desc[pref.strip()] = desc.strip()
    return prefix_desc

def load_prefix_offers(path: Path) -> Dict[str, str]:
    prefix_offer = {}
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if ";" in line:
                pref, uid = line.split(";", 1)
                prefix_offer[pref.strip()] = uid.strip()
    return prefix_offer

def load_tilda_photos(path: Path) -> List[Dict[str, str]]:
    rows = []
    with path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=";")
        for row in reader:
            rows.append(row)
    return rows

def is_placeholder(filename: str) -> bool:
    name = filename.lower()
    return any(pat in name for pat in PLACEHOLDER_PATTERNS)

def extract_prefix(filename: str, known_prefixes: List[str]) -> str:
    base = Path(filename).stem
    for pref in sorted(known_prefixes, key=len, reverse=True):
        if base.startswith(pref + "-") or base.startswith(pref + "_") or base.startswith(pref + "."):
            return pref
    return ""

def load_manual_titles(offers_dir: Path) -> Dict[str, str]:
    manual = {}
    if not offers_dir.exists():
        return manual
    for p in offers_dir.glob("*"):
        if p.is_file():
            stem = p.stem
            manual[stem] = p.name
    return manual

def main():
    print("Загружаем префиксы...")
    prefix_desc = load_prefix_descriptions(PREFIKSY_TXT)
    prefix_offer = load_prefix_offers(SLOVAR_PREF_TXT)
    known_prefixes = list(prefix_desc.keys() | prefix_offer.keys())

    print("Загружаем список фото Тильды...")
    photos = load_tilda_photos(SPISOK_FOTO_CSV)

    print("Загружаем ручные подписи (Офферы-подписанные)...")
    manual_titles = load_manual_titles(OFFERS_KIR_DIR)

    matched_rows: List[Dict[str, str]] = []
    unmatched_rows: List[Dict[str, str]] = []

    for row in photos:
        filename = row.get("filename", "") or row.get("rel_path", "")
        rel_path = row.get("rel_path", "")
        source = row.get("source", "")
        file_hash = row.get("hash", "")

        if not filename:
            continue

        if is_placeholder(filename):
            unmatched_rows.append({
                "source": source,
                "filename": filename,
                "rel_path": rel_path,
                "hash": file_hash,
                "prefix": "",
                "offer_uid": "",
                "prefix_desc": "",
                "title_ru_manual": "",
                "status": "placeholder"
            })
            continue

        pref = extract_prefix(filename, known_prefixes)
        offer_uid = prefix_offer.get(pref, "")
        pref_desc = prefix_desc.get(pref, "")

        stem = Path(filename).stem
        title_ru_manual = manual_titles.get(stem, "")

        base_record = {
            "source": source,
            "filename": filename,
            "rel_path": rel_path,
            "hash": file_hash,
            "prefix": pref,
            "offer_uid": offer_uid,
            "prefix_desc": pref_desc,
            "title_ru_manual": title_ru_manual
        }

        if pref or title_ru_manual or offer_uid:
            base_record["status"] = "matched"
            matched_rows.append(base_record)
        else:
            base_record["status"] = "unmatched"
            unmatched_rows.append(base_record)

    print(f"Сохраняем {len(matched_rows)} сопоставленных → {OUTPUT_MATCHED}")
    with OUTPUT_MATCHED.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "source", "filename", "rel_path", "hash",
                "prefix", "offer_uid", "prefix_desc",
                "title_ru_manual", "status"
            ],
            delimiter=";"
        )
        writer.writeheader()
        writer.writerows(matched_rows)

    print(f"Сохраняем {len(unmatched_rows)} несопоставленных → {OUTPUT_UNMATCHED}")
    with OUTPUT_UNMATCHED.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "source", "filename", "rel_path", "hash",
                "prefix", "offer_uid", "prefix_desc",
                "title_ru_manual", "status"
            ],
            delimiter=";"
        )
        writer.writeheader()
        writer.writerows(unmatched_rows)

    print("Готово.")

if __name__ == "__main__":
    main()
