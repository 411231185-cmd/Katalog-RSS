# -*- coding: utf-8 -*-
"""
Скрипт для создания ТОП-КАТАЛОГА с префиксами и фото
"""

import pandas as pd
import re
from pathlib import Path

# КОНФИГУРАЦИЯ
BASE_DIR = Path(r"C:\Dev\Katalog-RSS\catalogs")
ETALON_FILE = BASE_DIR / "ЭТАЛОННЫЙ есть UID и SKU22.12.csv"
IMAGES_DIR = BASE_DIR / "images"
OUTPUT_FILE = BASE_DIR / "TOP-KATALOG-s-prefiksami-i-foto.csv"

# СЛОВАРИ ПРЕФИКСОВ
PREFIX_OFFERS = [
    "ZADNBABKAZBOR", "SPINDELBABKAZBOR", "VALSPINDEL.BABKI",
    "KOLZUB.BABKA", "KOLZUB.KOROBKA", "KOLZUB.KARETKA",
    "KOLZUB.FARTUK", "KOLZUB.SMENSHEST", "KOLZUB", "SHESTERN", "VAL", "VILKA",
    "VINTY", "FARTUK", "KOMPLEKT", "ROLUPR", "ROLSGLA",
    "SPINDELBABKA", "SHPINDEL", "REVOLVGOLOV", "ZADNBABKA", "KOROBPODACH"
]
PREFIX_OFFERS = sorted(PREFIX_OFFERS, key=len, reverse=True)

OFFER_TO_PHOTO = {
    "FARTUK": "kuzl_f", "KOLZUB.FARTUK": "kuzl_f",
    "KOROBPODACH": "kuzl_kp", "SPINDELBABKA": "kuzl_pb",
    "ZADNBABKA": "kuzl_zb", "KOLZUB": "kuzl_",
    "VAL": "kuzl_val", "REVOLVGOLOV": "kuzl_rev"
}

# ФУНКЦИИ
def find_offer_prefix(sku, uid):
    text = str(sku).upper() if pd.notna(sku) else str(uid).upper()
    for prefix in PREFIX_OFFERS:
        if prefix in text:
            return prefix
    return ""

def find_photo_prefix(offer_prefix):
    if not offer_prefix:
        return ""
    if offer_prefix in OFFER_TO_PHOTO:
        return OFFER_TO_PHOTO[offer_prefix]
    for key, value in OFFER_TO_PHOTO.items():
        if key in offer_prefix:
            return value
    return ""

def find_photo_file(photo_prefix, sku, uid, images_dir):
    if not photo_prefix or not images_dir.exists():
        return ""
    
    text = str(sku).upper() if pd.notna(sku) else str(uid).upper()
    machine_codes = re.findall(r'\b(\d+[A-Z]?\d+)\b', text)
    
    all_files = [f.name for f in images_dir.iterdir() if f.is_file()]
    matching = [f for f in all_files if 'resizeb' not in f.lower() and photo_prefix in f.lower()]
    
    if machine_codes:
        for code in machine_codes:
            for fname in matching:
                if code.lower() in fname.lower():
                    return fname
    
    return matching[0] if matching else ""

# ОСНОВНАЯ ФУНКЦИЯ
def process_catalog():
    print("=" * 80)
    print("СОЗДАНИЕ ТОП-КАТАЛОГА")
    print("=" * 80)
    
    print(f"\n1. Загрузка: {ETALON_FILE.name}")
    df = pd.read_csv(ETALON_FILE, sep=';', encoding='utf-8')
    print(f"   ✅ Загружено {len(df)} товаров")
    
    print("\n2. Префиксы офферов...")
    df['PrefixOffer'] = df.apply(lambda r: find_offer_prefix(r.get('SKU'), r.get('UID')), axis=1)
    print(f"   ✅ Найдено: {(df['PrefixOffer'] != '').sum()}")
    
    print("\n3. Префиксы фото...")
    df['PrefixPhoto'] = df['PrefixOffer'].apply(find_photo_prefix)
    print(f"   ✅ Найдено: {(df['PrefixPhoto'] != '').sum()}")
    
    print("\n4. Привязка фото...")
    df['PhotoFile'] = df.apply(lambda r: find_photo_file(r['PrefixPhoto'], r.get('SKU'), r.get('UID'), IMAGES_DIR), axis=1)
    print(f"   ✅ Привязано фото: {(df['PhotoFile'] != '').sum()}")
    
    print(f"\n5. Сохранение: {OUTPUT_FILE.name}")
    df.to_csv(OUTPUT_FILE, sep=';', encoding='utf-8-sig', index=False)
    print(f"   ✅ Готово!")
    
    print("\n" + "=" * 80)
    print(f"Всего: {len(df)} | С фото: {(df['PhotoFile'] != '').sum()}")
    print("=" * 80)

if __name__ == "__main__":
    process_catalog()
