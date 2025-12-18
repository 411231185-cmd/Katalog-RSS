#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import csv
from pathlib import Path
import logging
import re

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def extract_tokens_from_filename(filename):
    """Извлекает ключевые токены из имени фото"""
    # Удаляем расширение и водяной знак
    clean_name = filename.replace('-watermarked', '').replace('.jpg', '').lower()
    
    # Разделяем на части по подчёркиванию
    tokens = clean_name.split('_')
    
    return [t for t in tokens if t]  # убираем пустые

def main():
    root = Path(__file__).parent.parent
    csv_file = root / "catalogs" / "ЭТАЛОННЫЙ есть UID и SKU!!!.csv"
    
    # Ищемые фото
    search_photos = [
        'kuzl_ks_vint_',
        'Kuzl_pb_val_1m63',
        'kzul_gk_1H65_50_101',
        'kzul_val_1M63_21_236',
        'kzul_val_1M63Y_20_181',
        'kzul_val_1M63Y_20_182',
        'kzul_vk_1H65_50_179'
    ]
    
    logger.info(f"Читаю каталог: {csv_file}\n")
    
    offers = {}
    with open(csv_file, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            uid = row.get('UID', '').strip()
            sku = row.get('SKU', '').strip()
            if uid:
                offers[uid.lower()] = {
                    'uid': uid,
                    'sku': sku,
                    'row': row
                }
    
    logger.info(f"Загружено офферов: {len(offers)}\n")
    
    # Ищем каждое фото
    results = {}
    for photo_name in search_photos:
        logger.info(f" Ищу: {photo_name}")
        tokens = extract_tokens_from_filename(photo_name)
        logger.info(f"   Токены: {tokens}")
        
        matched_offers = []
        
        # Ищем офферы содержащие эти токены
        for uid_lower, offer_data in offers.items():
            uid = offer_data['uid'].lower()
            sku = offer_data['sku'].lower()
            
            # Считаем совпадения токенов
            matches = 0
            for token in tokens:
                if token in uid or token in sku:
                    matches += 1
            
            if matches > 0:
                matched_offers.append({
                    'uid': offer_data['uid'],
                    'sku': offer_data['sku'],
                    'matches': matches,
                    'match_rate': (matches / len(tokens)) * 100
                })
        
        # Сортируем по количеству совпадений
        matched_offers.sort(key=lambda x: x['matches'], reverse=True)
        
        if matched_offers:
            logger.info(f"    Найдено совпадений: {len(matched_offers)}")
            for i, offer in enumerate(matched_offers[:5], 1):  # Показываем топ 5
                logger.info(f"     {i}. UID: {offer['uid']} | SKU: {offer['sku']} | Совпадений: {offer['matches']}/{len(tokens)} ({offer['match_rate']:.0f}%)")
            results[photo_name] = matched_offers[0]  # Берём лучший матч
        else:
            logger.info(f"    Не найдено совпадений")
        
        logger.info("")
    
    # Итоговый отчёт
    logger.info("=" * 80)
    logger.info("ИТОГОВЫЙ ОТЧЁТ СОПОСТАВЛЕНИЯ")
    logger.info("=" * 80)
    for photo_name, best_match in results.items():
        logger.info(f"{photo_name:40}  UID: {best_match['uid']:30} SKU: {best_match['sku']}")

if __name__ == "__main__":
    main()
