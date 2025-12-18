#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import csv
from pathlib import Path
import logging
import re

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def extract_keywords(filename):
    """Извлекает ключевые слова из имени фото"""
    # Удаляем расширение и водяной знак
    clean_name = filename.replace('-watermarked', '').replace('.jpg', '').lower()
    
    # Разделяем по подчёркиванию и дефису
    words = re.split(r'[_\-\.]+', clean_name)
    
    # Фильтруем пустые
    return [w for w in words if w and len(w) > 1]

def extract_numbers(filename):
    """Извлекает все числовые последовательности"""
    clean_name = filename.replace('-watermarked', '').replace('.jpg', '')
    return re.findall(r'\d+', clean_name)

def score_match(photo_name, sku):
    """Рассчитывает score совпадения photo vs SKU"""
    photo_keywords = extract_keywords(photo_name)
    photo_numbers = extract_numbers(photo_name)
    sku_lower = sku.lower()
    
    score = 0
    
    # 1. Совпадение ключевых слов (вес 2)
    for keyword in photo_keywords:
        if keyword in sku_lower:
            score += 2
    
    # 2. Совпадение чисел (вес 1)
    for number in photo_numbers:
        if number in sku_lower:
            score += 1
    
    return score

def main():
    root = Path(__file__).parent.parent
    csv_file = root / "catalogs" / "ЭТАЛОННЫЙ есть UID и SKU!!!.csv"
    
    photo_names = [
        'kzul_gk_1H65_50_101',
        'kzul_val_1M63_21_236',
        'kzul_val_1M63Y_20_181',
        'kzul_val_1M63Y_20_182',
        'kzul_vk_1H65_50_179',
        'krols_f130_rt301.41.151',
        'Krols_f150_cm2348.510.302-1',
        'kuzl_f_vilka1M63_04_028',
        'Kuzl__val_kz_165.02.410',
        'krols_f150_KG.1841.02.000',
        'Krols_f165_cm2349.510.302-1',
        'Kuzl_pb_val_1m63',
        'krols-KG1844-02-400-050',
        'krols-LKT1181-7040-',
        'krolu_f130_rt301.41.150',
        'Krolu_f150_cm2348.510.301-',
        'k-zb-shpindel-1658-03-198',
        'Kuzl_rez_dip500',
        'Kuzl_rez_1H65',
        'kuzl_patron_f1000'
    ]
    
    logger.info(f"Читаю каталог: {csv_file}\n")
    
    offers = {}
    with open(csv_file, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            uid = row.get('UID', '').strip()
            sku = row.get('SKU', '').strip()
            if uid:
                offers[uid] = {
                    'uid': uid,
                    'sku': sku,
                    'row': row
                }
    
    logger.info(f"Загружено офферов: {len(offers)}\n")
    
    # Результаты
    results = {}
    
    for photo_name in photo_names:
        logger.info(f" Ищу: {photo_name}")
        keywords = extract_keywords(photo_name)
        numbers = extract_numbers(photo_name)
        logger.info(f"   Ключевые слова: {keywords}")
        logger.info(f"   Числа: {numbers}")
        
        # Ищем лучший матч
        best_matches = []
        for uid, offer_data in offers.items():
            sku = offer_data['sku']
            match_score = score_match(photo_name, sku)
            
            if match_score > 0:
                best_matches.append({
                    'uid': uid,
                    'sku': sku,
                    'score': match_score
                })
        
        # Сортируем по score
        best_matches.sort(key=lambda x: x['score'], reverse=True)
        
        if best_matches:
            logger.info(f"    Найдено совпадений: {len(best_matches)}")
            for i, match in enumerate(best_matches[:3], 1):
                logger.info(f"     {i}. UID: {match['uid']} | SKU: {match['sku']} | Score: {match['score']}")
            
            results[photo_name] = best_matches[0]
        else:
            logger.info(f"    Совпадений не найдено")
        
        logger.info("")
    
    # Итоговый отчёт
    logger.info("=" * 100)
    logger.info("ИТОГОВЫЙ ОТЧЁТ")
    logger.info("=" * 100)
    
    output_file = root / "data" / "manual_mapping.csv"
    
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f, delimiter=';')
        writer.writerow(['Фото', 'UID', 'SKU', 'Score'])
        
        for photo_name in photo_names:
            if photo_name in results:
                match = results[photo_name]
                writer.writerow([photo_name, match['uid'], match['sku'], match['score']])
                logger.info(f"{photo_name:40}  {match['uid']:20} | {match['sku']}")
            else:
                logger.info(f"{photo_name:40}   НЕ НАЙДЕН")
    
    logger.info(f"\n Результаты сохранены: {output_file}")

if __name__ == "__main__":
    main()
