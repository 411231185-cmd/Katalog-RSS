#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import csv
from pathlib import Path
import logging
import re

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

# Словарь сокращений префиксов
PHOTO_PREFIXES = {
    'kzul': ['KOLZUB', 'KUZL'],
    'krols': ['KROLS', 'ROL'],
    'krolu': ['KROLU', 'ROL'],
    'kuzl': ['KUZL', 'KOLZUB'],
    'mo': ['MUFTAOBGON', 'MUFTA'],
    'rg': ['REVOLGOL', 'REVOL'],
    'zb': ['ZADNBABKA', 'ZADNBABK'],
    'k': ['KOLZUB', 'KUZL', 'KROLS'],
}

def extract_first_letters(filename):
    """Извлекает первые буквы из имени фото"""
    clean_name = filename.replace('-watermarked', '').replace('.jpg', '').lower()
    # Первые буквы до первого подчёркивания
    first_part = clean_name.split('_')[0].split('-')[0]
    return first_part

def extract_last_numbers(filename):
    """Извлекает ПОСЛЕДОВАТЕЛЬНОСТЬ последних чисел"""
    clean_name = filename.replace('-watermarked', '').replace('.jpg', '')
    # Находим все числа
    numbers = re.findall(r'\d+', clean_name)
    if numbers:
        return numbers[-1]  # Последовательность
    return None

def extract_all_numbers(filename):
    """Извлекает все числа"""
    clean_name = filename.replace('-watermarked', '').replace('.jpg', '')
    return re.findall(r'\d+', clean_name)

def score_match(photo_name, sku):
    """Рассчитывает score совпадения с ПРИОРИТЕТОМ на последние числа и префиксы"""
    photo_prefix = extract_first_letters(photo_name)
    photo_last_num = extract_last_numbers(photo_name)
    photo_all_nums = extract_all_numbers(photo_name)
    sku_upper = sku.upper()
    sku_lower = sku.lower()
    
    score = 0
    
    # 1. ПРИОРИТЕТ: Последние числа совпадают в конце SKU (вес 10)
    if photo_last_num and sku_lower.endswith(photo_last_num.lower()):
        score += 10
    elif photo_last_num and photo_last_num in sku_lower:
        score += 5
    
    # 2. Проверяем префикс фото с префиксом SKU (вес 3)
    for prefix_short, prefix_list in PHOTO_PREFIXES.items():
        if photo_prefix.startswith(prefix_short):
            for prefix_sku in prefix_list:
                if prefix_sku.upper() in sku_upper:
                    score += 3
                    break
    
    # 3. Совпадение других чисел (вес 1)
    for num in photo_all_nums:
        if num in sku_lower and num != photo_last_num:
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
        logger.info(f" {photo_name}")
        prefix = extract_first_letters(photo_name)
        last_num = extract_last_numbers(photo_name)
        logger.info(f"   Префикс: {prefix} | Последнее число: {last_num}")
        
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
            top_match = best_matches[0]
            logger.info(f"    UID: {top_match['uid']} | SKU: {top_match['sku']} | Score: {top_match['score']}")
            
            if len(best_matches) > 1 and best_matches[1]['score'] == best_matches[0]['score']:
                logger.info(f"      Также подходит: {best_matches[1]['sku']} (score={best_matches[1]['score']})")
            
            results[photo_name] = top_match
        else:
            logger.info(f"    Совпадений не найдено")
        
        logger.info("")
    
    # Итоговый отчёт
    logger.info("=" * 120)
    logger.info("ИТОГОВЫЙ ОТЧЁТ (ПРИОРИТЕТ НА ПОСЛЕДНИЕ ЧИСЛА И ПРЕФИКСЫ)")
    logger.info("=" * 120)
    
    output_file = root / "data" / "manual_mapping_v2.csv"
    
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f, delimiter=';')
        writer.writerow(['Фото', 'UID', 'SKU', 'Score'])
        
        for photo_name in photo_names:
            if photo_name in results:
                match = results[photo_name]
                writer.writerow([photo_name, match['uid'], match['sku'], match['score']])
                logger.info(f"{photo_name:40}  {match['sku']:50} (score={match['score']})")
            else:
                logger.info(f"{photo_name:40}   НЕ НАЙДЕН")
    
    logger.info(f"\n Результаты сохранены: {output_file}")

if __name__ == "__main__":
    main()
