#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
✅ КАТАЛОГ ДЛЯ ОЛЕГА - ТОЧНО ПОД ШАБЛОН OLEG-5.csv
18 колонок в правильном порядке
"""

import pandas as pd
import re
from pathlib import Path
from datetime import datetime
import sys

print("="*80)
print("✅ СОЗДАНИЕ КАТАЛОГА ДЛЯ ОЛЕГА (ПОД ШАБЛОН OLEG-5.csv)")
print("="*80)

# === ШАГ 1: ПОИСК CSV ===
print("\n📂 Поиск CSV файлов...")

current_dir = Path.cwd()
csv_files = list(current_dir.glob("*.csv"))

if not csv_files:
    print("❌ CSV файлы не найдены!")
    print(f"   Текущая папка: {current_dir}")
    print("\n💡 Запустите из папки catalogs:")
    print("   cd C:\\GitHub-Repositories\\Katalog-RSS\\catalogs")
    sys.exit(1)

print(f"✅ Найдено файлов: {len(csv_files)}")

# Приоритет файлов
priority = [
    'FINAL_TILDA_CATALOG.csv',
    'TOP-KATALOG-CAPILOT.csv',
    'Poslednij-yanvar.csv',
    'MASTER_WITH_HTML_LINKS copy.csv'
]

input_file = None
for p in priority:
    found = [f for f in csv_files if f.name == p]
    if found:
        input_file = found[0]
        break

if not input_file:
    input_file = max(csv_files, key=lambda f: f.stat().st_size)

print(f"✅ Выбран: {input_file.name}")

# === ШАГ 2: ЧТЕНИЕ ===
print("\n📖 Чтение данных...")

try:
    df = pd.read_csv(input_file, encoding='utf-8-sig')
    print(f"✅ Загружено: {len(df)} строк, {len(df.columns)} колонок")
except Exception as e:
    print(f"❌ Ошибка чтения: {e}")
    sys.exit(1)

# === ШАГ 3: ФУНКЦИИ ОБРАБОТКИ ===

def clean_html(text):
    """Удаляет HTML теги"""
    if pd.isna(text):
        return ""
    text = str(text)
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def get_type(title):
    """Определяет тип: machine или spare"""
    title = str(title).lower()
    if any(kw in title for kw in ['станок', 'machine', 'lathe']):
        return 'machine'
    return 'spare'

def get_brand(title):
    """Извлекает бренд"""
    title = str(title).lower()
    if '16к20' in title or '16k20' in title:
        return 'Красный Пролетарий'
    if '1к62' in title or '1k62' in title:
        return 'Красный Пролетарий'
    return 'РУССтанкоСбыт'

def format_category(cat):
    """Форматирует категорию с >>>"""
    if pd.isna(cat):
        return 'Станки >>> Прочее'
    cat = str(cat)
    if '>>>' in cat:
        return cat
    if '.' in cat:
        parts = cat.split('.')
        return ' >>> '.join(p.strip() for p in parts if p.strip())
    return f'Станки >>> {cat}'

def get_compat(text, sku):
    """Извлекает совместимость"""
    models = set()
    text = str(text) + ' ' + str(sku)
    text = text.upper()
    
    patterns = [
        r'\b16К?20\b',
        r'\b1К?62\b',
        r'\b1К?625\b'
    ]
    
    for p in patterns:
        found = re.findall(p, text)
        for m in found:
            m = m.replace('K', 'К')
            models.add(m)
    
    return ';'.join(sorted(models))

def extract_weight(text):
    """Извлекает вес в кг"""
    if pd.isna(text):
        return ''
    text = str(text).lower()
    match = re.search(r'(\d+(?:\.\d+)?)\s*кг', text)
    if match:
        return match.group(1)
    return ''

def extract_power(text):
    """Извлекает мощность в кВт"""
    if pd.isna(text):
        return ''
    text = str(text).lower()
    match = re.search(r'(\d+(?:\.\d+)?)\s*квт', text)
    if match:
        return match.group(1)
    return ''

def extract_dimensions(text):
    """Извлекает габариты"""
    if pd.isna(text):
        return ''
    text = str(text)
    match = re.search(r'(\d{3,4})\s*[xх×]\s*(\d{3,4})\s*[xх×]\s*(\d{3,4})', text)
    if match:
        return f"{match.group(1)}x{match.group(2)}x{match.group(3)}"
    return ''

def extract_voltage(text):
    """Извлекает напряжение"""
    if pd.isna(text):
        return ''
    text = str(text).lower()
    if '220/380' in text or '380/220' in text:
        return '220/380'
    if '380' in text:
        return '380'
    if '220' in text:
        return '220'
    return ''

# === ШАГ 4: СОЗДАНИЕ КАТАЛОГА ПОД ШАБЛОН ОЛЕГА ===
print("\n🔄 Создание каталога (18 колонок)...")

# Получаем данные из исходного файла
sku_col = df.get('SKU', df.get('Tilda UID', ''))
title_col = df.get('Title', '')
price_col = pd.to_numeric(df.get('Price', 0), errors='coerce').fillna(0)
text_col = df.get('Text', df.get('Description', ''))
photo_col = df.get('Photo', '')
category_col = df.get('Product Type', df.get('Category', ''))

# Создаем DataFrame ТОЧНО под шаблон Олега
oleg_data = {
    'ID': sku_col,
    'Title': title_col,
    'SKU': sku_col,
    'Type': title_col.apply(get_type),
    'Brand': title_col.apply(get_brand),
    'Category_Path': category_col.apply(format_category),
    'Price': price_col,
    'Currency': 'RUB',
    'Compatible_SKUs': df.apply(lambda r: get_compat(r.get('Text', ''), r.get('SKU', '')), axis=1),
    'Short_Description': text_col.apply(lambda x: clean_html(x)[:150] if pd.notna(x) else ''),
    'Full_Description': text_col.apply(clean_html),
    'Weight_KG': text_col.apply(extract_weight),
    'Power_KW': text_col.apply(extract_power),
    'Dimensions_MM': text_col.apply(extract_dimensions),
    'Voltage_V': text_col.apply(extract_voltage),
    'Main_Photo': photo_col,
    'Gallery_Photos': '',
    'Status': 'published'
}

oleg_df = pd.DataFrame(oleg_data)

print(f"✅ Создано: {len(oleg_df)} записей")

# === ШАГ 5: СТАТИСТИКА ===
print("\n📊 СТАТИСТИКА:")
print(f"   Станков (machine): {(oleg_df['Type'] == 'machine').sum()}")
print(f"   Запчастей (spare): {(oleg_df['Type'] == 'spare').sum()}")
print(f"   С ценой: {(oleg_df['Price'] > 0).sum()}")
print(f"   С фото: {(oleg_df['Main_Photo'] != '').sum()}")
print(f"   С описанием: {(oleg_df['Short_Description'] != '').sum()}")
print(f"   С весом: {(oleg_df['Weight_KG'] != '').sum()}")
print(f"   С мощностью: {(oleg_df['Power_KW'] != '').sum()}")
print(f"   С габаритами: {(oleg_df['Dimensions_MM'] != '').sum()}")

# === ШАГ 6: СОХРАНЕНИЕ ===
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
output_csv = f"CATALOG_FOR_OLEG_{timestamp}.csv"
output_excel = f"CATALOG_FOR_OLEG_{timestamp}.xlsx"

print("\n💾 Сохранение...")

# CSV (всегда)
oleg_df.to_csv(output_csv, index=False, encoding='utf-8-sig')
print(f"✅ CSV: {output_csv}")

# Excel (если можем)
try:
    oleg_df.to_excel(output_excel, index=False, engine='openpyxl')
    print(f"✅ Excel: {output_excel}")
except:
    print("⚠️  Excel не создан (нет openpyxl)")
    print("   Установите: pip install openpyxl")

# === ШАГ 7: ПРИМЕРЫ ===
print("\n📦 ПРИМЕРЫ (первые 3):")
for idx, row in oleg_df.head(3).iterrows():
    print(f"\n{idx+1}. {row['Title'][:60]}")
    print(f"   ID: {row['ID']}")
    print(f"   Type: {row['Type']}")
    print(f"   Brand: {row['Brand']}")
    print(f"   Price: {row['Price']} {row['Currency']}")

print("\n" + "="*80)
print("🎉 ГОТОВО! КАТАЛОГ ДЛЯ ОЛЕГА СОЗДАН!")
print("="*80)
print(f"\n📁 Файлы в: {current_dir}")
print(f"✉️  Отправьте Олегу: {output_csv}")
print("\n💡 Формат ТОЧНО соответствует шаблону OLEG-5.csv")
