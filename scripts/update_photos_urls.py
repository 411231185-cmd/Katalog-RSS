#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import csv
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def local_path_to_dropbox_url(local_path):
    path = Path(local_path)
    return f"file:///{path.as_posix()}"

def main():
    root = Path(__file__).parent.parent
    csv_file = root / "tests" / "catalog_test.csv"  # ТЕСТОВЫЙ файл
    mapping_file = root / "data" / "mappings" / "offer_to_photos.json"
    output_file = root / "data" / "normalized" / "catalog_with_photos.csv"

    output_file.parent.mkdir(parents=True, exist_ok=True)

    logger.info(f"Читаю маппинг: {mapping_file}")
    with open(mapping_file, 'r', encoding='utf-8-sig') as f:
        mapping = json.load(f)

    logger.info(f"Читаю тестовый CSV: {csv_file}")
    rows = []
    fieldnames = []
    
    with open(csv_file, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f, delimiter=';')
        fieldnames = list(reader.fieldnames) if reader.fieldnames else []
        
        # Добавляем колонку Фото, если её нет
        if 'Фото' not in fieldnames:
            fieldnames.append('Фото')
        
        for row in reader:
            uid = row.get('UID', '').strip()
            
            # Инициализируем значение Фото пустой строкой
            if 'Фото' not in row:
                row['Фото'] = ''
            
            if uid in mapping and mapping[uid]['photos']:
                first_photo = mapping[uid]['photos'][0]
                photo_url = local_path_to_dropbox_url(first_photo['fullPath'])
                row['Фото'] = photo_url
                logger.info(f"  {uid}: добавлено фото")
            
            rows.append(row)

    logger.info(f"Сохраняю: {output_file}")
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=';')
        writer.writeheader()
        writer.writerows(rows)

    logger.info(f"Готово!")

if __name__ == "__main__":
    main()
