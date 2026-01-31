#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎯 КОНВЕРТАЦИЯ КАТАЛОГА В ФОРМАТ ОЛЕГА (18 КОЛОНОК)
Источник: FINAL_TILDA_CATALOG.csv
Выход: CATALOG_FOR_OLEG.xlsx и .csv
"""

import pandas as pd
import re
from pathlib import Path
from datetime import datetime

print("="*80)
print("🎯 СОЗДАНИЕ КАТАЛОГА ДЛЯ ОЛЕГА (18 КОЛОНОК)")
print("="*80)

# === НАСТРОЙКИ ===
INPUT_CSV = "FINAL_TILDA_CATALOG.csv"
OUTPUT_EXCEL = f"CATALOG_FOR_OLEG_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
OUTPUT_CSV = f"CATALOG_FOR_OLEG_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

# === ФУНКЦИИ ОБРАБОТКИ ===

def clean_html(text):
    """Удаляет HTML-теги из текста"""
    if pd.isna(text) or not text:
        return ""
    text = str(text)
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'&[a-z]+;', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def extract_short_description(text, max_len=150):
    """Извлекает краткое описание (1-2 предложения)"""
    if pd.isna(text) or not text:
        return ""
    
    text = clean_html(text)
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 10]
    
    if not sentences:
        return text[:max_len]
    
    short = sentences[0]
    if len(short) < 80 and len(sentences) > 1:
        short += ". " + sentences[1]
    
    if len(short) > max_len:
        short = short[:max_len-3] + "..."
    elif not short.endswith('.'):
        short += '.'
    
    return short

def determine_type(row):
    """Определяет тип объекта: machine или spare"""
    title = str(row.get('Title', '')).lower()
    category = str(row.get('Product Type', '')).lower()
    
    # Ключевые слова для станков
    machine_keywords = ['станок', 'machine', 'lathe', 'токарн', 'фрезерн', 'шлифовал']
    
    text = title + " " + category
    
    for kw in machine_keywords:
        if kw in text:
            return "machine"
    
    return "spare"

def extract_brand(title):
    """Извлекает бренд из названия товара"""
    if pd.isna(title):
        return "РУССтанкоСбыт"
    
    title = str(title).lower()
    
    # Словарь брендов
    brands = {
        'красный пролетарий': 'Красный Пролетарий',
        '16к20': 'Красный Пролетарий',
        '1к62': 'Красный Пролетарий',
        '1к625': 'Красный Пролетарий',
        'рязан': 'Рязанский',
        'саста': 'САСТА',
        'китай': 'Китай',
        'саратов': 'Саратовский'
    }
    
    for keyword, brand_name in brands.items():
        if keyword in title:
            return brand_name
    
    return "РУССтанкоСбыт"

def format_category_path(category):
    """Форматирует путь категории с разделителем >>>"""
    if pd.isna(category) or not category:
        return "Станки >>> Прочее"
    
    category = str(category)
    
    # Если уже есть разделитель, оставляем как есть
    if '>>>' in category:
        return category
    
    # Если есть точка или слеш, конвертируем
    if '.' in category:
        parts = category.split('.')
        return " >>> ".join(p.strip() for p in parts if p.strip())
    
    if '/' in category:
        parts = category.split('/')
        return " >>> ".join(p.strip() for p in parts if p.strip())
    
    # По умолчанию добавляем "Станки >>>" перед категорией
    return f"Станки >>> {category}"

def extract_compatibility(text):
    """Извлекает совместимые модели из текста (через ;)"""
    if pd.isna(text) or not text:
        return ""
    
    text = str(text)
    
    # Паттерны для поиска моделей станков
    patterns = [
        r'\b1[6К]К?\d{2}[А-Я]?\b',  # 16К20, 1К62 и т.д.
        r'\b\d{1,2}[А-Я]\d{2,3}[А-Я]?\b',  # 2М614, 3М151 и т.д.
    ]
    
    models = set()
    for pattern in patterns:
        found = re.findall(pattern, text, re.IGNORECASE)
        models.update(found)
    
    return ";".join(sorted(models)) if models else ""

def extract_dimensions(text):
    """Извлекает габариты в формате ДхШхВ"""
    if pd.isna(text) or not text:
        return ""
    
    text = str(text)
    
    # Паттерны для поиска размеров
    patterns = [
        r'(\d{2,4})\s*[xхXХ×]\s*(\d{2,4})\s*[xхXХ×]\s*(\d{2,4})',
        r'габариты?\s*:?\s*(\d{2,4})\s*[xхXХ×]\s*(\d{2,4})\s*[xхXХ×]\s*(\d{2,4})',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return f"{match.group(1)}x{match.group(2)}x{match.group(3)}"
    
    return ""

def extract_weight(text):
    """Извлекает вес в кг"""
    if pd.isna(text) or not text:
        return ""
    
    text = str(text)
    
    patterns = [
        r'(\d+(?:[\.,]\d+)?)\s*кг',
        r'вес\s*:?\s*(\d+(?:[\.,]\d+)?)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).replace(',', '.')
    
    return ""

def extract_power(text):
    """Извлекает мощность в кВт"""
    if pd.isna(text) or not text:
        return ""
    
    text = str(text)
    
    patterns = [
        r'(\d+(?:[\.,]\d+)?)\s*квт',
        r'мощность\s*:?\s*(\d+(?:[\.,]\d+)?)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).replace(',', '.')
    
    return ""

def extract_voltage(text):
    """Извлекает напряжение в В"""
    if pd.isna(text) or not text:
        return ""
    
    text = str(text)
    
    patterns = [
        r'(\d{2,3})\s*в(?:ольт)?',
        r'напряжение\s*:?\s*(\d{2,3})',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1)
    
    return ""

# === ОСНОВНАЯ ЛОГИКА ===

print("\n📂 Чтение входного файла...")
df = pd.read_csv(INPUT_CSV, encoding='utf-8-sig')
print(f"✅ Загружено записей: {len(df)}")

print("\n🔄 Преобразование данных...")

# Создаем DataFrame с 18 колонками для Олега
oleg_df = pd.DataFrame({
    # 1. ИДЕНТИФИКАТОР (SKU)
    'ИДЕНТИФИКАТОР': df.get('SKU', ''),
    
    # 2. НАЗВАНИЕ ТОВАРА
    'НАЗВАНИЕ ТОВАРА': df.get('Title', ''),
    
    # 3. АРТИКУЛ (дублируем SKU)
    'АРТИКУЛ': df.get('SKU', ''),
    
    # 4. ТИП ОБЪЕКТА (machine/spare)
    'ТИП ОБЪЕКТА': df.apply(determine_type, axis=1),
    
    # 5. БРЕНД
    'БРЕНД': df['Title'].apply(extract_brand),
    
    # 6. ПУТЬ КАТЕГОРИИ (Разделитель >>>)
    'ПУТЬ КАТЕГОРИИ': df.get('Product Type', '').apply(format_category_path),
    
    # 7. ЦЕНА
    'ЦЕНА': df.get('Price', 0),
    
    # 8. ВАЛЮТА (по умолчанию RUB)
    'ВАЛЮТА': 'RUB',
    
    # 9. СОВМЕСТИМОСТЬ (Артикулы через ;)
    'СОВМЕСТИМОСТЬ': df.get('Text', '').apply(extract_compatibility),
    
    # 10. КРАТКОЕ ОПИСАНИЕ (1-2 предл.)
    'КРАТКОЕ ОПИСАНИЕ': df.get('Description', '').apply(lambda x: extract_short_description(x, 150)),
    
    # 11. ПОЛНОЕ ОПИСАНИЕ (Текст без тегов)
    'ПОЛНОЕ ОПИСАНИЕ': df.get('Text', '').apply(clean_html),
    
    # 12. ВЕС (КГ)
    'ВЕС (КГ)': df.get('Text', '').apply(extract_weight),
    
    # 13. МОЩНОСТЬ (КВТ)
    'МОЩНОСТЬ (КВТ)': df.get('Text', '').apply(extract_power),
    
    # 14. ГАБАРИТЫ (ММ) - ДхШхВ
    'ГАБАРИТЫ (ММ)': df.get('Text', '').apply(extract_dimensions),
    
    # 15. НАПРЯЖЕНИЕ (В)
    'НАПРЯЖЕНИЕ (В)': df.get('Text', '').apply(extract_voltage),
    
    # 16. ГЛАВНОЕ ФОТО
    'ГЛАВНОЕ ФОТО': df.get('Photo', ''),
    
    # 17. ГАЛЕРЕЯ ФОТО (через ;) - пока пустое
    'ГАЛЕРЕЯ ФОТО': '',
    
    # 18. СТАТУС (published/draft)
    'СТАТУС': 'published'
})

print(f"✅ Преобразовано {len(oleg_df)} записей")

# Статистика
print("\n📊 СТАТИСТИКА:")
print(f"   Станков (machine): {(oleg_df['ТИП ОБЪЕКТА'] == 'machine').sum()}")
print(f"   Запчастей (spare): {(oleg_df['ТИП ОБЪЕКТА'] == 'spare').sum()}")
print(f"   С ценой: {(oleg_df['ЦЕНА'] > 0).sum()}")
print(f"   С фото: {oleg_df['ГЛАВНОЕ ФОТО'].notna().sum()}")
print(f"   С кратким описанием: {(oleg_df['КРАТКОЕ ОПИСАНИЕ'] != '').sum()}")
print(f"   С полным описанием: {(oleg_df['ПОЛНОЕ ОПИСАНИЕ'] != '').sum()}")

# Сохранение
print("\n💾 Сохранение результатов...")

# Excel
oleg_df.to_excel(OUTPUT_EXCEL, index=False, engine='openpyxl')
print(f"✅ Excel: {OUTPUT_EXCEL}")

# CSV
oleg_df.to_csv(OUTPUT_CSV, index=False, encoding='utf-8-sig')
print(f"✅ CSV: {OUTPUT_CSV}")

# Превью первых 3 строк
print("\n👁️ ПРЕВЬЮ ПЕРВЫХ 3 СТРОК:")
print("="*80)
for idx, row in oleg_df.head(3).iterrows():
    print(f"\n📦 Товар #{idx+1}:")
    print(f"   SKU: {row['ИДЕНТИФИКАТОР']}")
    print(f"   Название: {row['НАЗВАНИЕ ТОВАРА']}")
    print(f"   Тип: {row['ТИП ОБЪЕКТА']}")
    print(f"   Бренд: {row['БРЕНД']}")
    print(f"   Категория: {row['ПУТЬ КАТЕГОРИИ']}")
    print(f"   Цена: {row['ЦЕНА']} {row['ВАЛЮТА']}")
    print(f"   Краткое описание: {row['КРАТКОЕ ОПИСАНИЕ'][:80]}...")

print("\n" + "="*80)
print("🎉 ГОТОВО! Каталог для Олега создан!")
print("="*80)
