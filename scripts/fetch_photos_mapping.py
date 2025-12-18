#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import csv
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def extract_model_code(text):
    if not text:
        return None
    parts = str(text).split('.')
    for part in parts:
        if any(c.isdigit() for c in part) and len(part) > 2:
            return part.upper()
    return None

def main():
    root = Path(__file__).parent.parent
    csv_file = root / "data" / "source" / "ETALONNYI-est-UID-i-SKU.csv"
    registry_file = root / "data" / "mappings" / "photos_registry_full.json"
    output_file = root / "data" / "mappings" / "offer_to_photos.json"

    logger.info(f"Читаю CSV: {csv_file}")
    offers = {}
    with open(csv_file, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            uid = row.get('UID', '').strip()
            sku = row.get('SKU', '').strip()
            if uid:
                offers[uid] = {
                    'sku': sku,
                    'title': row.get('Название', ''),
                    'model_code': extract_model_code(uid)
                }

    logger.info(f"Загружено офферов: {len(offers)}")

    logger.info(f"Читаю реестр фото: {registry_file}")
    with open(registry_file, 'r', encoding='utf-8-sig') as f:
        photos_registry = json.load(f)

    mapping = {}
    
    for uid, offer_data in offers.items():
        model_code = offer_data['model_code']
        sku = offer_data['sku']
        
        photos_for_offer = []
        
        for prefix, photos_list in photos_registry.items():
            for photo in photos_list:
                file_name = photo['baseName'].upper()
                model_upper = model_code.upper() if model_code else ""
                sku_upper = sku.upper()
                
                if (model_upper and model_upper in file_name) or (sku_upper and sku_upper in file_name):
                    photos_for_offer.append({
                        'fileName': photo['fileName'],
                        'prefix': prefix,
                        'folder': photo['folder'],
                        'fullPath': photo['fullPath']
                    })
        
        if photos_for_offer:
            mapping[uid] = {
                'sku': sku,
                'title': offer_data['title'],
                'model_code': model_code,
                'photos': photos_for_offer,
                'photo_count': len(photos_for_offer)
            }

    logger.info(f"Найдено офферов с фото: {len(mapping)}")
    logger.info(f"Сохраняю маппинг: {output_file}")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(mapping, f, ensure_ascii=False, indent=2)
    
    logger.info(f"Готово!")

if __name__ == "__main__":
    main()
