#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import csv
import re
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def extract_first_letters(filename):
    """Извлекает первые буквы из имени фото"""
    clean_name = filename.replace('-watermarked', '').replace('.jpg', '').lower()
    first_part = clean_name.split('_')[0].split('-')[0]
    return first_part

def extract_last_numbers(filename):
    """Извлекает ПОСЛЕДНЕЕ число"""
    clean_name = filename.replace('-watermarked', '').replace('.jpg', '')
    numbers = re.findall(r'\d+', clean_name)
    if numbers:
        return numbers[-1]
    return None

def score_match(photo_name, sku):
    """Рассчитывает score совпадения"""
    photo_prefix = extract_first_letters(photo_name)
    photo_last_num = extract_last_numbers(photo_name)
    photo_all_nums = re.findall(r'\d+', photo_name)
    sku_lower = sku.lower()
    
    score = 0
    
    # ПРИОРИТЕТ: Последние числа в конце SKU
    if photo_last_num and sku_lower.endswith(photo_last_num.lower()):
        score += 10
    elif photo_last_num and photo_last_num in sku_lower:
        score += 5
    
    # Другие числа
    for num in photo_all_nums:
        if num in sku_lower and num != photo_last_num:
            score += 1
    
    return score

def main():
    root = Path(__file__).parent.parent
    csv_file = root / "tests" / "catalog_test.csv"
    registry_file = root / "data" / "mappings" / "photos_registry_full.json"
    output_file = root / "tests" / "catalog_with_photos_test.csv"
    
    # Загружаем каталог офферов
    logger.info(f"Читаю тестовый CSV: {csv_file}")
    offers_dict = {}
    fieldnames = []
    
    with open(csv_file, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f, delimiter=';')
        fieldnames = list(reader.fieldnames) if reader.fieldnames else []
        
        for row in reader:
            uid = row.get('UID', '').strip()
            sku = row.get('SKU', '').strip()
            if uid:
                offers_dict[uid] = {
                    'uid': uid,
                    'sku': sku,
                    'row': row
                }
    
    logger.info(f"Загружено офферов: {len(offers_dict)}\n")
    
    # Добавляем колонку Фото если её нет
    if 'Фото' not in fieldnames:
        fieldnames.append('Фото')
    
    # Загружаем реестр фото
    logger.info(f"Читаю реестр фото: {registry_file}")
    with open(registry_file, 'r', encoding='utf-8-sig') as f:
        photos_registry = json.load(f)
    
    # Считаем все фото
    all_photos = []
    for folder_prefix, photos_list in photos_registry.items():
        all_photos.extend(photos_list)
    
    logger.info(f"Всего фото в реестре: {len(all_photos)}\n")
    
    # Сопоставляем фото с офферами
    logger.info(" Ищу совпадения фото с офферами...\n")
    
    photo_matches = {}  # uid -> список фото
    matched_photos = 0
    
    for photo in all_photos:
        photo_name = photo.get('baseName', photo.get('fileName', ''))
        
        # Ищем лучший матч среди офферов
        best_match = None
        best_score = 0
        
        for uid, offer_data in offers_dict.items():
            sku = offer_data['sku']
            match_score = score_match(photo_name, sku)
            
            if match_score > best_score:
                best_score = match_score
                best_match = uid
        
        # Если score >= 5, добавляем фото
        if best_score >= 5:
            if best_match not in photo_matches:
                photo_matches[best_match] = []
            
            photo_matches[best_match].append({
                'fileName': photo_name,
                'fullPath': photo.get('fullPath', ''),
                'score': best_score
            })
            matched_photos += 1
    
    logger.info(f" Найдено совпадений фото: {matched_photos}")
    logger.info(f" Офферов с фото: {len(photo_matches)}\n")
    
    # Обновляем CSV с фото
    logger.info(f"Сохраняю: {output_file}")
    
    rows = []
    for uid, offer_data in offers_dict.items():
        row = offer_data['row'].copy()
        
        # Добавляем фото если найдено
        if uid in photo_matches and photo_matches[uid]:
            # Берём первое фото (лучший матч)
            first_photo = photo_matches[uid][0]
            # Сохраняем как локальный путь
            row['Фото'] = first_photo['fullPath']
        else:
            row['Фото'] = ''  # Пусто = будет черное фото из Tilda
        
        rows.append(row)
    
    # Сохраняем CSV
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=';')
        writer.writeheader()
        writer.writerows(rows)
    
    logger.info(f" Готово!")
    logger.info(f"\nСтатистика:")
    logger.info(f"  Всего офферов: {len(offers_dict)}")
    logger.info(f"  Офферов с фото: {len(photo_matches)}")
    logger.info(f"  Офферов без фото: {len(offers_dict) - len(photo_matches)}")
    logger.info(f"\nТестовый файл: {output_file}")
    logger.info(f"Загрузи на тестовый сайт Tilda для проверки!")

if __name__ == "__main__":
    main()
