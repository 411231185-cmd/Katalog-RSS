#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎯 КАТАЛОГ ДЛЯ ОЛЕГА - ТОЧНО ПО ЕГО ШАБЛОНУ
С тремя служебными строками: English Headers, Russian Headers, Format Description
"""

import pandas as pd
import re
from pathlib import Path
from datetime import datetime
import sys

print("="*80)
print("🎯 СОЗДАНИЕ КАТАЛОГА ДЛЯ ОЛЕГА - ТОЧНЫЙ ФОРМАТ ШАБЛОНА")
print("="*80)

# === ШАГ 1: ПОИСК CSV ===
print("\n📂 Поиск CSV файлов...")

current_dir = Path.cwd()
csv_files = list(current_dir.glob("*.csv"))

if not csv_files:
    print("❌ CSV файлы не найдены!")
    sys.exit(1)

# Приоритет файлов
priority = [
    'FINAL_TILDA_CATALOG.csv',
    'TOP-KATALOG-CAPILOT.csv',
    'Poslednij-yanvar.csv',
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
df = pd.read_csv(input_file, encoding='utf-8-sig')
print(f"✅ Загружено: {len(df)} строк")

# === ШАГ 3: ФУНКЦИИ ОБРАБОТКИ ===

def clean_html(text):
    if pd.isna(text):
        return ""
    text = str(text)
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def get_type(title):
    title = str(title).lower()
    if any(kw in title for kw in ['станок', 'machine', 'lathe']):
        return 'machine'
    return 'spare'

def get_brand(title):
    title = str(title).lower()
    if '16к20' in title or '16k20' in title:
        return 'Красный Пролетарий'
    if '1к62' in title or '1k62' in title:
        return 'Красный Пролетарий'
    return 'РУССтанкоСбыт'

def format_category(cat):
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
    models = set()
    text = str(text) + ' ' + str(sku)
    text = text.upper()
    
    patterns = [
        r'\b16К?20\b',
        r'\b1К?62\b',
        r'\b1М63\b',
        r'\b1Н65\b',
    ]
    
    for p in patterns:
        found = re.findall(p, text)
        for m in found:
            m = m.replace('K', 'К')
            models.add(m)
    
    return ';'.join(sorted(models)) if models else ''

def extract_weight(text):
    if pd.isna(text):
        return ''
    text = str(text).lower()
    match = re.search(r'(\d+(?:\.\d+)?)\s*кг', text)
    if match:
        return match.group(1)
    return ''

def extract_power(text):
    if pd.isna(text):
        return ''
    text = str(text).lower()
    match = re.search(r'(\d+(?:\.\d+)?)\s*квт', text)
    if match:
        return match.group(1)
    return ''

def extract_dimensions(text):
    if pd.isna(text):
        return ''
    text = str(text)
    match = re.search(r'(\d{3,4})\s*[xх×]\s*(\d{3,4})\s*[xх×]\s*(\d{3,4})', text)
    if match:
        return f"{match.group(1)}x{match.group(2)}x{match.group(3)}"
    return ''

def extract_voltage(text):
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

# === ШАГ 4: СОЗДАНИЕ ДАННЫХ ===
print("\n🔄 Создание каталога...")

sku_col = df.get('SKU', df.get('Tilda UID', ''))
title_col = df.get('Title', '')
price_col = pd.to_numeric(df.get('Price', 0), errors='coerce').fillna(0)
text_col = df.get('Text', df.get('Description', ''))
photo_col = df.get('Photo', '')
category_col = df.get('Product Type', df.get('Category', ''))

# Создаем данные товаров
data_rows = []
for idx in range(len(df)):
    row = {
        'ID': str(sku_col.iloc[idx]) if pd.notna(sku_col.iloc[idx]) else '',
        'Title': str(title_col.iloc[idx]) if pd.notna(title_col.iloc[idx]) else '',
        'SKU': str(sku_col.iloc[idx]) if pd.notna(sku_col.iloc[idx]) else '',
        'Type': get_type(title_col.iloc[idx]) if pd.notna(title_col.iloc[idx]) else 'spare',
        'Brand': get_brand(title_col.iloc[idx]) if pd.notna(title_col.iloc[idx]) else 'РУССтанкоСбыт',
        'Category_Path': format_category(category_col.iloc[idx]),
        'Price': int(price_col.iloc[idx]) if price_col.iloc[idx] > 0 else '',
        'Currency': 'RUB',
        'Compatible_SKUs': get_compat(text_col.iloc[idx] if pd.notna(text_col.iloc[idx]) else '', 
                                       sku_col.iloc[idx] if pd.notna(sku_col.iloc[idx]) else ''),
        'Short_Description': clean_html(text_col.iloc[idx])[:150] if pd.notna(text_col.iloc[idx]) else '',
        'Full_Description': clean_html(text_col.iloc[idx]) if pd.notna(text_col.iloc[idx]) else '',
        'Weight_KG': extract_weight(text_col.iloc[idx]) if pd.notna(text_col.iloc[idx]) else '',
        'Power_KW': extract_power(text_col.iloc[idx]) if pd.notna(text_col.iloc[idx]) else '',
        'Dimensions_MM': extract_dimensions(text_col.iloc[idx]) if pd.notna(text_col.iloc[idx]) else '',
        'Voltage_V': extract_voltage(text_col.iloc[idx]) if pd.notna(text_col.iloc[idx]) else '',
        'Main_Photo': str(photo_col.iloc[idx]) if pd.notna(photo_col.iloc[idx]) else '',
        'Gallery_Photos': '',
        'Status': 'published'
    }
    data_rows.append(row)

# Создаем DataFrame с данными
data_df = pd.DataFrame(data_rows)

# === ШАГ 5: СОЗДАЕМ ФАЙЛ С ТРЕМЯ СЛУЖЕБНЫМИ СТРОКАМИ ===

# Строка 1: Английские заголовки (как есть)
header_en = {
    'ID': 'ID',
    'Title': 'Title',
    'SKU': 'SKU',
    'Type': 'Type',
    'Brand': 'Brand',
    'Category_Path': 'Category_Path',
    'Price': 'Price',
    'Currency': 'Currency',
    'Compatible_SKUs': 'Compatible_SKUs',
    'Short_Description': 'Short_Description',
    'Full_Description': 'Full_Description',
    'Weight_KG': 'Weight_KG',
    'Power_KW': 'Power_KW',
    'Dimensions_MM': 'Dimensions_MM',
    'Voltage_V': 'Voltage_V',
    'Main_Photo': 'Main_Photo',
    'Gallery_Photos': 'Gallery_Photos',
    'Status': 'Status'
}

# Строка 2: Русские заголовки
header_ru = {
    'ID': 'ИДЕНТИФИКАТОР',
    'Title': 'НАЗВАНИЕ ТОВАРА',
    'SKU': 'АРТИКУЛ',
    'Type': 'ТИП ОБЪЕКТА',
    'Brand': 'БРЕНД',
    'Category_Path': 'ПУТЬ КАТЕГОРИИ',
    'Price': 'ЦЕНА',
    'Currency': 'ВАЛЮТА',
    'Compatible_SKUs': 'СОВМЕСТИМОСТЬ',
    'Short_Description': 'КРАТКОЕ ОПИСАНИЕ',
    'Full_Description': 'ПОЛНОЕ ОПИСАНИЕ',
    'Weight_KG': 'ВЕС (КГ)',
    'Power_KW': 'МОЩНОСТЬ (КВТ)',
    'Dimensions_MM': 'ГАБАРИТЫ (ММ)',
    'Voltage_V': 'НАПРЯЖЕНИЕ (В)',
    'Main_Photo': 'ГЛАВНОЕ ФОТО',
    'Gallery_Photos': 'ГАЛЕРЕЯ ФОТО',
    'Status': 'СТАТУС'
}

# Строка 3: Описание формата
format_desc = {
    'ID': '(системное)',
    'Title': 'Текст',
    'SKU': 'Уникальный код',
    'Type': 'machine / spare',
    'Brand': 'Текст',
    'Category_Path': 'Разделитель >>>',
    'Price': 'Число',
    'Currency': 'RUB / USD',
    'Compatible_SKUs': 'Артикулы через ;',
    'Short_Description': '1-2 предл.',
    'Full_Description': 'Текст без тегов',
    'Weight_KG': 'Число',
    'Power_KW': 'Число',
    'Dimensions_MM': 'ДхШхВ',
    'Voltage_V': 'Число',
    'Main_Photo': '{SKU}_main.jpg',
    'Gallery_Photos': 'через ;',
    'Status': 'published / draft'
}

# Объединяем все строки
final_df = pd.DataFrame([header_en, header_ru, format_desc] + data_rows)

print(f"✅ Создано: {len(data_rows)} записей + 3 служебные строки")

# === ШАГ 6: СТАТИСТИКА ===
print("\n📊 СТАТИСТИКА:")
machines = sum(1 for row in data_rows if row['Type'] == 'machine')
spares = sum(1 for row in data_rows if row['Type'] == 'spare')
with_price = sum(1 for row in data_rows if row['Price'] != '')
with_photo = sum(1 for row in data_rows if row['Main_Photo'] != '')

print(f"   Станков: {machines}")
print(f"   Запчастей: {spares}")
print(f"   С ценой: {with_price}")
print(f"   С фото: {with_photo}")

# === ШАГ 7: СОХРАНЕНИЕ ===
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
output_excel = f"CATALOG_FOR_OLEG_EXACT_{timestamp}.xlsx"
output_csv = f"CATALOG_FOR_OLEG_EXACT_{timestamp}.csv"

print("\n💾 Сохранение...")

# Excel
try:
    final_df.to_excel(output_excel, index=False, header=False, engine='openpyxl')
    print(f"✅ Excel: {output_excel}")
except Exception as e:
    print(f"⚠️ Excel ошибка: {e}")

# CSV
final_df.to_csv(output_csv, index=False, header=False, encoding='utf-8-sig')
print(f"✅ CSV: {output_csv}")

# === ШАГ 8: ПРИМЕРЫ ===
print("\n📦 ПРИМЕРЫ первых 3 товаров (после служебных строк):")
for i, row in enumerate(data_rows[:3], 1):
    print(f"\n{i}. {row['Title'][:60]}")
    print(f"   SKU: {row['SKU']}")
    print(f"   Type: {row['Type']}")
    print(f"   Price: {row['Price']} {row['Currency']}")

print("\n" + "="*80)
print("🎉 ГОТОВО! КАТАЛОГ С 3 СЛУЖЕБНЫМИ СТРОКАМИ СОЗДАН!")
print("="*80)
print(f"\n📁 Файлы в: {current_dir}")
print(f"✉️ Отправьте Олегу: {output_excel}")
print("\n💡 Формат:")
print("   Строка 1: English Headers")
print("   Строка 2: Russian Headers")
print("   Строка 3: Format Description")
print("   Строка 4+: Data")
