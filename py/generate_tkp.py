# -*- coding: utf-8 -*-
"""
Скрипт для генерации ТКП (Технико-коммерческое предложение) всех офферов
"""

import pandas as pd
import os
from pathlib import Path

# КОНФИГУРАЦИЯ
BASE_DIR = Path(__file__).parent
CATALOG_FILE = BASE_DIR / "catalogs" / "ЭТАЛОННЫЙ есть UID и SKU22.12.csv"
OUTPUT_FILE_ALL = BASE_DIR / "ТКП всех офферов.txt"
OUTPUT_FILE_MACHINES = BASE_DIR / "ТКП станков.txt"

def load_catalog():
    """Загрузка каталога из CSV файла"""
    print(f"Загрузка каталога из: {CATALOG_FILE}")
    
    # Пробуем разные разделители
    for sep in [';', ',', '\t']:
        try:
            df = pd.read_csv(CATALOG_FILE, sep=sep, encoding='utf-8-sig')
            if len(df.columns) > 5:
                print(f"✅ Каталог загружен: {len(df)} офферов, {len(df.columns)} колонок")
                return df
        except Exception as e:
            # Логируем ошибку для отладки
            print(f"  Попытка с разделителем '{sep}' не удалась: {e}")
            continue
    
    raise Exception("Не удалось загрузить каталог с известными разделителями")

def generate_tkp(df, filter_machines=False):
    """Генерация ТКП из каталога"""
    if filter_machines:
        print(f"\nГенерация ТКП только для станков...")
    else:
        print(f"\nГенерация ТКП для всех офферов...")
    
    lines = []
    counter = 1
    
    # Ключевые слова для фильтрации станков
    machine_keywords = ['станок', 'станки', 'токарн', 'фрезерн', 'сверлильн']
    
    for idx, row in df.iterrows():
        # Получаем данные из строки
        # SKU - основной идентификатор, Tilda UID используется как резервный идентификатор
        sku = row.get('SKU', row.get('Tilda UID', ''))
        title = row.get('Title', '')
        category = row.get('Category', '')
        
        # Пропускаем пустые записи
        if pd.isna(title) or title == '':
            continue
        
        # Фильтрация по станкам
        if filter_machines:
            title_lower = str(title).lower()
            category_lower = str(category).lower() if pd.notna(category) else ''
            
            # Проверяем наличие ключевых слов
            has_keyword = any(kw in title_lower or kw in category_lower for kw in machine_keywords)
            if not has_keyword:
                continue
        
        # Формируем строку в формате: Number) SKU — Title (Category)
        if pd.notna(sku) and sku != '':
            if pd.notna(category) and category != '':
                # Извлекаем последнюю часть категории после ">>>"
                if '>>>' in str(category):
                    category_parts = str(category).split('>>>')
                    category_short = category_parts[-1].strip()
                else:
                    category_short = str(category).split(';')[-1].strip()
                
                line = f"{counter}) {sku} — {title} ({category_short})"
            else:
                line = f"{counter}) {sku} — {title}"
        else:
            line = f"{counter}) {title}"
        
        lines.append(line)
        counter += 1
    
    return lines

def save_tkp(lines, output_file):
    """Сохранение ТКП в файл"""
    print(f"\nСохранение в: {output_file}")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        for line in lines:
            f.write(line + "\n")
    
    print(f"✅ Сохранено {len(lines)} офферов")

def main():
    print("=" * 80)
    print("ГЕНЕРАЦИЯ ТКП ОФФЕРОВ")
    print("=" * 80)
    
    # Проверяем наличие входного файла
    if not CATALOG_FILE.exists():
        print(f"\n❌ Файл не найден: {CATALOG_FILE}")
        return
    
    # Загружаем каталог
    df = load_catalog()
    
    # Генерируем ТКП всех офферов
    lines_all = generate_tkp(df, filter_machines=False)
    save_tkp(lines_all, OUTPUT_FILE_ALL)
    
    # Генерируем ТКП только для станков
    lines_machines = generate_tkp(df, filter_machines=True)
    save_tkp(lines_machines, OUTPUT_FILE_MACHINES)
    
    print("\n" + "=" * 80)
    print(f"ГОТОВО!")
    print(f"  - {OUTPUT_FILE_ALL.name}: {len(lines_all)} офферов")
    print(f"  - {OUTPUT_FILE_MACHINES.name}: {len(lines_machines)} офферов")
    print("=" * 80)

if __name__ == "__main__":
    main()
