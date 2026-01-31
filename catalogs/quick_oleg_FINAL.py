#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎯 БЫСТРЫЙ КАТАЛОГ ДЛЯ ОЛЕГА - ФИНАЛЬНАЯ ВЕРСИЯ
Автоматически находит CSV и создаёт 18-колоночный каталог
"""

import pandas as pd
import re
from pathlib import Path
from datetime import datetime
import sys

print("="*80)
print("🎯 БЫСТРОЕ СОЗДАНИЕ КАТАЛОГА ДЛЯ ОЛЕГА")
print("="*80)

# === ШАГ 1: ПОИСК CSV ФАЙЛОВ ===
print("\n📂 Поиск CSV файлов...")

current_dir = Path.cwd()
csv_files = list(current_dir.glob("*.csv"))

if not csv_files:
    print("❌ Не найдено ни одного CSV файла в текущей директории!")
    print(f"   Текущая папка: {current_dir}")
    print("\n💡 Убедитесь что вы в папке catalogs:")
    print("   cd C:\\GitHub-Repositories\\Katalog-RSS\\catalogs")
    sys.exit(1)

print(f"✅ Найдено CSV файлов: {len(csv_files)}")

# Показываем список
for i, f in enumerate(csv_files, 1):
    size_mb = f.stat().st_size / (1024*1024)
    print(f"   {i}. {f.name} ({size_mb:.1f} MB)")

# Приоритетный список файлов для поиска
priority_files = [
    'FINAL_TILDA_CATALOG.csv',
    'MASTER_WITH_HTML_LINKS copy.csv',
    'TOP-KATALOG-CAPILOT.csv',
    'Poslednij-yanvar.csv'
]

input_file = None

# Ищем по приоритету
for priority in priority_files:
    found = [f for f in csv_files if f.name == priority]
    if found:
        input_file = found[0]
        print(f"\n✅ Выбран файл: {input_file.name}")
        break

# Если не нашли приоритетный - берём самый большой
if not input_file:
    input_file = max(csv_files, key=lambda f: f.stat().st_size)
    print(f"\n✅ Выбран самый большой файл: {input_file.name}")

# === ШАГ 2: ЧТЕНИЕ ФАЙЛА ===
print("\n📖 Чтение данных...")

try:
    df = pd.read_csv(input_file, encoding='utf-8-sig')
    print(f"✅ Загружено записей: {len(df)}")
    print(f"   Колонок: {len(df.columns)}")
except Exception as e:
    print(f"❌ Ошибка чтения файла: {e}")
    sys.exit(1)

# === ШАГ 3: ПРОСТЫЕ ФУНКЦИИ ===

def clean_html(text):
    if pd.isna(text) or not text:
        return ""
    text = str(text)
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def get_type(row):
    title = str(row.get('Title', '')).lower()
    if any(kw in title for kw in ['станок', 'machine', 'lathe']):
        return "machine"
    return "spare"

def format_category(cat):
    if pd.isna(cat) or not cat:
        return "Станки >>> Прочее"
    cat = str(cat)
    if '>>>' in cat:
        return cat
    if '.' in cat:
        return " >>> ".join(cat.split('.'))
    return f"Станки >>> {cat}"

def get_compat(text):
    if pd.isna(text) or not text:
        return ""
    models = set()
    patterns = [r'\b1[6К]К?20\b', r'\b1К62\b', r'\b1К625\b']
    for p in patterns:
        models.update(re.findall(p, str(text).upper()))
    return ';'.join(sorted(models))

# === ШАГ 4: СОЗДАНИЕ КАТАЛОГА ===
print("\n🔄 Создание каталога с 18 колонками...")

oleg_df = pd.DataFrame({
    'ИДЕНТИФИКАТОР': df.get('SKU', df.get('Tilda UID', '')),
    'НАЗВАНИЕ ТОВАРА': df.get('Title', ''),
    'АРТИКУЛ': df.get('SKU', df.get('Tilda UID', '')),
    'ТИП ОБЪЕКТА': df.apply(get_type, axis=1),
    'БРЕНД': 'РУССтанкоСбыт',
    'ПУТЬ КАТЕГОРИИ': df.get('Product Type', df.get('Category', '')).apply(format_category),
    'ЦЕНА': pd.to_numeric(df.get('Price', 0), errors='coerce').fillna(0),
    'ВАЛЮТА': 'RUB',
    'СОВМЕСТИМОСТЬ': df.get('Text', df.get('Description', '')).apply(get_compat),
    'КРАТКОЕ ОПИСАНИЕ': df.get('Description', '').apply(lambda x: clean_html(x)[:150] if pd.notna(x) else ''),
    'ПОЛНОЕ ОПИСАНИЕ': df.get('Text', '').apply(clean_html),
    'ВЕС (КГ)': '',
    'МОЩНОСТЬ (КВТ)': '',
    'ГАБАРИТЫ (ММ)': '',
    'НАПРЯЖЕНИЕ (В)': '',
    'ГЛАВНОЕ ФОТО': df.get('Photo', ''),
    'ГАЛЕРЕЯ ФОТО': '',
    'СТАТУС': 'published'
})

print(f"✅ Создано записей: {len(oleg_df)}")

# === ШАГ 5: СТАТИСТИКА ===
print("\n📊 СТАТИСТИКА:")
print(f"   Станков: {(oleg_df['ТИП ОБЪЕКТА'] == 'machine').sum()}")
print(f"   Запчастей: {(oleg_df['ТИП ОБЪЕКТА'] == 'spare').sum()}")
print(f"   С ценой: {(oleg_df['ЦЕНА'] > 0).sum()}")
print(f"   С фото: {(oleg_df['ГЛАВНОЕ ФОТО'] != '').sum()}")
print(f"   С описанием: {(oleg_df['КРАТКОЕ ОПИСАНИЕ'] != '').sum()}")

# === ШАГ 6: СОХРАНЕНИЕ ===
output_excel = f"CATALOG_FOR_OLEG_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
output_csv = f"CATALOG_FOR_OLEG_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

print("\n💾 Сохранение...")

try:
    oleg_df.to_excel(output_excel, index=False, engine='openpyxl')
    print(f"✅ Excel: {output_excel}")
except Exception as e:
    print(f"⚠️ Не удалось создать Excel: {e}")
    print("   (Возможно не установлен openpyxl: pip install openpyxl)")

oleg_df.to_csv(output_csv, index=False, encoding='utf-8-sig')
print(f"✅ CSV: {output_csv}")

# === ШАГ 7: ПРИМЕРЫ ===
print("\n📦 ПРИМЕРЫ (первые 3):")
for idx, row in oleg_df.head(3).iterrows():
    print(f"\n{idx+1}. {row['НАЗВАНИЕ ТОВАРА'][:60]}")
    print(f"   SKU: {row['ИДЕНТИФИКАТОР']}")
    print(f"   Тип: {row['ТИП ОБЪЕКТА']}")
    print(f"   Цена: {row['ЦЕНА']} руб")

print("\n" + "="*80)
print("🎉 ГОТОВО! КАТАЛОГ ДЛЯ ОЛЕГА СОЗДАН!")
print("="*80)
print(f"\n📁 Файлы сохранены в: {current_dir}")
print(f"\n✉️  Отправьте Олегу файл: {output_excel}")
