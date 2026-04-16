# -*- coding: utf-8 -*-
"""
Скрипт для конвертации структуры каталога в формат Tilda
Удаляет лишние колонки и добавляет кавычки вокруг полей
"""

import pandas as pd
from pathlib import Path

# КОНФИГУРАЦИЯ
BASE_DIR = Path(__file__).parent
SOURCE_FILE = BASE_DIR / "catalogs" / "TOP-KATALOG-s-prefiksami-i-foto copy 2.csv"
OUTPUT_FILE = BASE_DIR / "TOP-KATALOG-s-prefiksami-i-foto copy 2-CHPU-TEXT.csv"

# Стандартные колонки Tilda (22 колонки)
TILDA_COLUMNS = [
    "Tilda UID", "Brand", "SKU", "Mark", "Category", "Title", "Description", 
    "Text", "Photo", "Price", "Quantity", "Price Old", "Editions", 
    "Modifications", "External ID", "Parent UID", "Weight", "Length", 
    "Width", "Height", "Url", "UID"
]

def convert_catalog():
    """Конвертирует каталог в формат Tilda"""
    print("=" * 80)
    print("КОНВЕРТАЦИЯ КАТАЛОГА В ФОРМАТ TILDA")
    print("=" * 80)
    
    # Проверяем наличие файла
    if not SOURCE_FILE.exists():
        print(f"\n❌ Файл не найден: {SOURCE_FILE}")
        return
    
    print(f"\n1. Загрузка каталога: {SOURCE_FILE.name}")
    
    # Читаем CSV
    try:
        df = pd.read_csv(SOURCE_FILE, sep=';', encoding='utf-8-sig')
        print(f"   ✅ Загружено: {len(df)} строк, {len(df.columns)} колонок")
        print(f"   Колонки: {', '.join(df.columns[:5])}...")
    except Exception as e:
        print(f"   ❌ Ошибка загрузки: {e}")
        return
    
    print(f"\n2. Проверка и отбор колонок...")
    
    # Проверяем наличие всех необходимых колонок
    missing_cols = [col for col in TILDA_COLUMNS if col not in df.columns]
    if missing_cols:
        print(f"   ⚠️  Отсутствующие колонки: {', '.join(missing_cols)}")
    
    # Выбираем только нужные колонки
    available_cols = [col for col in TILDA_COLUMNS if col in df.columns]
    df_tilda = df[available_cols].copy()
    
    print(f"   ✅ Отобрано колонок: {len(available_cols)} из {len(TILDA_COLUMNS)}")
    
    # Удаленные колонки
    removed_cols = [col for col in df.columns if col not in TILDA_COLUMNS]
    if removed_cols:
        print(f"   🗑️  Удалены колонки: {', '.join(removed_cols)}")
    
    print(f"\n3. Сохранение в формате Tilda...")
    
    # Сохраняем с кавычками вокруг всех полей
    df_tilda.to_csv(
        OUTPUT_FILE,
        sep=';',
        encoding='utf-8-sig',
        index=False,
        quoting=1,  # QUOTE_ALL - кавычки вокруг всех полей
        quotechar='"'
    )
    
    print(f"   ✅ Сохранено: {OUTPUT_FILE.name}")
    print(f"   📊 Строк: {len(df_tilda)}")
    print(f"   📊 Колонок: {len(df_tilda.columns)}")
    
    print("\n" + "=" * 80)
    print("ГОТОВО!")
    print("=" * 80)
    print(f"\nФайл для загрузки в Tilda: {OUTPUT_FILE.name}")
    print("\nРазличия:")
    print(f"  • Исходный файл: {len(df.columns)} колонок")
    print(f"  • Новый файл: {len(df_tilda.columns)} колонок (стандарт Tilda)")
    print(f"  • Формат: все поля в кавычках")
    print("=" * 80)

if __name__ == "__main__":
    convert_catalog()
