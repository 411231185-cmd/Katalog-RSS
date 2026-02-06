#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для создания каталога по шаблону Олега
- Читает шаблон OLEG-Shablon.xlsx (структура колонок)
- Читает один или несколько исходных каталогов (CSV)
- Формирует итоговый каталог строго по шаблону
- Выгружает отдельный файл с незаполненными/проблемными строками
"""
import pandas as pd
from pathlib import Path

# === Параметры ===
TEMPLATE_PATH = Path('catalogs/OLEG-Shablon.xlsx')
CATALOG_SOURCES = [
    Path('catalogs/CATALOG_MACHINES_TURRETS_20260202_204049.csv'),
    # Добавьте сюда другие каталоги при необходимости
]
OUTPUT_PATH = Path('catalogs/CATALOG_FOR_OLEG_FULL.xlsx')
UNFILLED_PATH = Path('catalogs/CATALOG_FOR_OLEG_UNFILLED.xlsx')

# === 1. Чтение шаблона ===
template_df = pd.read_excel(TEMPLATE_PATH, nrows=0)
template_columns = list(template_df.columns)

# === 2. Чтение исходных каталогов ===
sources = [pd.read_csv(src, encoding='utf-8-sig') for src in CATALOG_SOURCES]
full_df = pd.concat(sources, ignore_index=True)

# === 3. Приведение к шаблону ===
result = pd.DataFrame(columns=template_columns)

for col in template_columns:
    # Попытка найти совпадающую колонку по названию (без учёта регистра)
    match = [c for c in full_df.columns if c.strip().lower() == col.strip().lower()]
    if match:
        result[col] = full_df[match[0]]
    else:
        result[col] = ''  # Пусто, если нет совпадения

# === 4. Поиск незаполненных строк ===
not_filled = result[result.isnull().any(axis=1) | (result == '').any(axis=1)]

# === 5. Сохранение ===
result.to_excel(OUTPUT_PATH, index=False)
not_filled.to_excel(UNFILLED_PATH, index=False)

print(f'✅ Итоговый каталог сохранён: {OUTPUT_PATH}')
print(f'⚠️  Не все строки заполнены, проверьте файл: {UNFILLED_PATH}')
