#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для сбора ВСЕХ офферов из CSV-каталогов в едином формате:
№) АРТИКУЛ — Название (Категория)
Без дублей, с нумерацией, результат в catalogs/TXT/Vse-OFFERY-RSS.txt
"""
import pandas as pd
from pathlib import Path
import re


# === Параметры ===
CATALOGS_DIR = Path('catalogs')
OUTPUT_PATH = Path('catalogs/TXT/Vse-OFFERY-RSS.txt')


def normalize_article(art):
    """Нормализация артикула для дедупликации"""
    if pd.isna(art) or not art:
        return ''
    # Приведение к верхнему регистру и удаление лишних пробелов
    return str(art).strip().upper()


def clean_text(text):
    """Очистка текста от None, nan и лишних пробелов"""
    if pd.isna(text) or text in ['nan', 'None', 'null', '']:
        return ''
    return str(text).strip()


# === Создание выходной директории ===
OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)


# === Поиск всех CSV-файлов ===
csv_files = sorted(CATALOGS_DIR.glob('*.csv'))

print('=' * 80)
print('🔍 СБОР ОФФЕРОВ ИЗ CSV-КАТАЛОГОВ')
print('=' * 80)
print(f'📂 Найдено CSV-файлов: {len(csv_files)}')
print()


# === Словарь для хранения офферов (ключ = нормализованный артикул) ===
offers_dict = {}
stats = {
    'total_rows': 0,
    'valid_offers': 0,
    'duplicates': 0,
    'errors': 0
}


# === Обработка каждого CSV-файла ===
for csv_file in csv_files:
    print(f'📄 Обработка: {csv_file.name}')
    
    try:
        # Попытка чтения с разными кодировками
        try:
            df = pd.read_csv(csv_file, encoding='utf-8-sig')
        except:
            try:
                df = pd.read_csv(csv_file, encoding='cp1251')
            except:
                df = pd.read_csv(csv_file, encoding='latin1')
        
        stats['total_rows'] += len(df)
        
        # Автоматический поиск колонок
        art_cols = [c for c in df.columns if any(kw in c.lower() for kw in ['артикул', 'sku', 'id', 'uid', 'article'])]
        name_cols = [c for c in df.columns if any(kw in c.lower() for kw in ['назв', 'title', 'имя', 'name'])]
        cat_cols = [c for c in df.columns if any(kw in c.lower() for kw in ['катег', 'category', 'группа', 'group'])]
        
        if not art_cols or not name_cols:
            print(f'   ⚠️  Пропущен (нет нужных колонок)')
            continue
        
        art_col = art_cols[0]
        name_col = name_cols[0]
        cat_col = cat_cols[0] if cat_cols else None
        
        file_offers = 0
        file_duplicates = 0
        
        # Обработка строк
        for _, row in df.iterrows():
            art_raw = row.get(art_col, '')
            art_normalized = normalize_article(art_raw)
            name = clean_text(row.get(name_col, ''))
            category = clean_text(row.get(cat_col, '')) if cat_col else ''
            
            # Валидация
            if not art_normalized or not name:
                continue
            
            # Проверка на дубли
            if art_normalized in offers_dict:
                file_duplicates += 1
                stats['duplicates'] += 1
                continue
            
            # Сохранение оффера
            offers_dict[art_normalized] = {
                'article': str(art_raw).strip(),  # Оригинальный артикул
                'name': name,
                'category': category
            }
            
            file_offers += 1
            stats['valid_offers'] += 1
        
        print(f'   ✅ Добавлено: {file_offers} | Дублей: {file_duplicates}')
        
    except Exception as e:
        print(f'   ❌ Ошибка: {e}')
        stats['errors'] += 1


print()
print('=' * 80)
print('💾 СОХРАНЕНИЕ РЕЗУЛЬТАТА')
print('=' * 80)


# === Сортировка по артикулу ===
sorted_offers = sorted(offers_dict.values(), key=lambda x: x['article'])


# === Запись в файл ===
with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
    for idx, offer in enumerate(sorted_offers, 1):
        article = offer['article']
        name = offer['name']
        category = offer['category']
        
        # Формирование строки в формате: №) АРТИКУЛ — Название (Категория)
        if category:
            line = f"{idx}) {article} — {name} ({category})"
        else:
            line = f"{idx}) {article} — {name}"
        
        f.write(line + '\n')


# === Статистика ===
print(f'✅ Всего уникальных офферов: {len(sorted_offers)}')
print(f'📊 Статистика:')
print(f'   • Обработано строк:     {stats["total_rows"]}')
print(f'   • Валидных офферов:     {stats["valid_offers"]}')
print(f'   • Дублей (пропущено):   {stats["duplicates"]}')
print(f'   • Ошибок при чтении:    {stats["errors"]}')
print()
print(f'💾 Файл сохранён: {OUTPUT_PATH}')
print('=' * 80)
