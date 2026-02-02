#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎯 ПОЛНЫЙ КАТАЛОГ ДЛЯ ОЛЕГА - КАЧЕСТВЕННАЯ ВЕРСИЯ
Источник: MD файлы из docs/ + FINAL_TILDA_CATALOG.csv
Формат: ТОЧНО как в OLEG-Shablon.xlsx с 2 служебными строками
"""

import pandas as pd
import re
from pathlib import Path
from datetime import datetime
import sys

print("="*80)
print("🎯 ПОЛНЫЙ КАТАЛОГ ДЛЯ ОЛЕГА - КАЧЕСТВЕННАЯ ВЕРСИЯ")
print("="*80)

# === ШАГ 1: ЧТЕНИЕ ВСЕХ MD ФАЙЛОВ ===
print("\n📂 Чтение MD файлов...")

repo_root = Path(__file__).parent.parent
md_files = []

# Ищем MD файлы в docs/
docs_dir = repo_root / 'docs'
if docs_dir.exists():
    for md_file in docs_dir.glob('**/*.md'):
        if md_file.name not in {'README.md', 'SUMMARY.md'}:
            md_files.append(md_file)

print(f"✅ Найдено MD файлов: {len(md_files)}")

# === ФУНКЦИИ ИЗВЛЕЧЕНИЯ ДАННЫХ ИЗ MD ===

def extract_from_md(file_path):
    """Извлекает все характеристики из MD файла"""
    try:
        content = file_path.read_text(encoding='utf-8')
        
        # Убираем бренды
        content_clean = re.sub(r'ООО\s*["""«]?ТД\s*РУССтанкоСбыт["""»]?', '', content, flags=re.IGNORECASE)
        content_clean = re.sub(r'руссстанко\s*сбыт|rossstanko|tdrusstankosbyt', '', content_clean, flags=re.IGNORECASE)
        
        data = {
            'title': '',
            'description': '',
            'full_text': '',
            'weight': '',
            'power': '',
            'dimensions': '',
            'voltage': '380',  # По умолчанию
            'compatible': '',
            'category': '',
            'sku': ''
        }
        
        # Название из первого заголовка
        title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if title_match:
            data['title'] = title_match.group(1).strip()
        
        # SKU из названия файла
        data['sku'] = file_path.stem
        
        # Категория из пути
        path_parts = file_path.parts
        if 'docs' in path_parts:
            idx = path_parts.index('docs')
            if idx + 1 < len(path_parts):
                category_parts = path_parts[idx+1:-1]
                data['category'] = ' >>> '.join(category_parts)
        
        # Краткое описание - первое предложение после "Назначение"
        desc_patterns = [
            r'Назначение и возможности\s*\n(.+?)(?=\n#|\n\n|$)',
            r'##\s*Назначение\s*\n(.+?)(?=\n#|\n\n|$)',
            r'предназначен[а-я\s]+для\s+(.+?)(?:\.|$)'
        ]
        
        for pattern in desc_patterns:
            match = re.search(pattern, content_clean, re.MULTILINE | re.DOTALL)
            if match:
                desc_text = match.group(1).strip()
                # Первое предложение
                sentences = re.split(r'[.!?]+', desc_text)
                if sentences:
                    data['description'] = sentences[0].strip()[:150]
                # Полный текст (до 500 символов)
                data['full_text'] = re.sub(r'\s+', ' ', desc_text[:500]).strip()
                break
        
        # Вес/масса
        weight_patterns = [
            r'(?:масса|вес)\s*станка[:\s]*(\d+(?:[.,]\d+)?)\s*кг',
            r'(?:масса|вес)\s*головки[:\s]*(\d+(?:[.,]\d+)?)\s*кг',
            r'(?:масса|вес)[:\s]*(\d+(?:[.,]\d+)?)\s*кг'
        ]
        
        for pattern in weight_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                data['weight'] = match.group(1).replace(',', '.')
                break
        
        # Мощность
        power_patterns = [
            r'мощность\s+(?:электродвигателя\s+)?(?:привода\s+)?главного\s+движения[:\s]*(\d+(?:[.,]\d+)?)\s*квт',
            r'суммарная\s+мощность[:\s]*(\d+(?:[.,]\d+)?)\s*квт',
            r'мощность[:\s]*(\d+(?:[.,]\d+)?)\s*квт'
        ]
        
        for pattern in power_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                data['power'] = match.group(1).replace(',', '.')
                break
        
        # Габариты
        dim_patterns = [
            r'габариты?\s*станка[:\s]*(?:длина[:\s]*)?(\d{3,5})\s*[xх×,]\s*(\d{3,5})\s*[xх×,]\s*(\d{3,5})',
            r'(\d{3,5})\s*[xх×]\s*(\d{3,5})\s*[xх×]\s*(\d{3,5})\s*мм'
        ]
        
        for pattern in dim_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                data['dimensions'] = f"{match.group(1)}x{match.group(2)}x{match.group(3)}"
                break
        
        # Напряжение
        if '220' in content and '380' in content:
            data['voltage'] = '220/380'
        elif '380' in content:
            data['voltage'] = '380'
        elif '220' in content:
            data['voltage'] = '220'
        
        # Совместимость - модели станков
        models = re.findall(r'\b(?:16[КKк][234][0О]|1[МНмн]\d{2,3}|РТ\d{2,4}|16[АаAa]20[ФфFf]3?|1П756)\b', content)
        if models:
            unique_models = sorted(set(m.upper().replace('K', 'К') for m in models))
            data['compatible'] = ';'.join(unique_models[:5])  # Максимум 5 моделей
        
        return data
        
    except Exception as e:
        print(f"⚠️  Ошибка чтения {file_path.name}: {e}")
        return None

# Читаем все MD файлы
print("\n📖 Парсинг MD файлов...")
tkp_database = {}

for md_file in md_files:
    data = extract_from_md(md_file)
    if data:
        # Сохраняем по разным ключам для лучшего поиска
        title_key = data['title'].lower()
        sku_key = data['sku'].lower()
        
        tkp_database[title_key] = data
        tkp_database[sku_key] = data
        
        # Также по моделям
        if data['compatible']:
            for model in data['compatible'].split(';'):
                tkp_database[model.lower().strip()] = data

print(f"✅ Загружено записей в базу: {len(tkp_database)}")

# === ШАГ 2: ФИЛЬТРУЕМ ТОЛЬКО СТАНКИ И РЕВОЛЬВЕРНЫЕ ГОЛОВКИ ===
print("\n🔍 Фильтрация станков и револьверных головок...")

machines_and_turrets = {}

for key, data in tkp_database.items():
    title = data['title'].lower()
    category = data['category'].lower()
    
    # Проверяем что это станок или револьверная головка
    is_machine = any(word in title for word in ['станок', 'machine'])
    is_turret = any(word in title for word in ['револьверн', 'turret', 'головка'])
    is_in_category = any(word in category for word in ['станки', 'револьверн'])
    
    if (is_machine or is_turret or is_in_category) and data['title']:
        # Используем title как ключ чтобы избежать дублей
        machines_and_turrets[data['title']] = data

print(f"✅ Найдено станков и револьверных головок: {len(machines_and_turrets)}")

# === ШАГ 3: СОЗДАЕМ DATAFRAME ===
print("\n🔄 Создание каталога...")

catalog_data = []

for title, data in machines_and_turrets.items():
    # Определяем тип
    item_type = 'machine' if 'станок' in title.lower() else 'spare'
    
    # SKU - очищенное название
    sku = re.sub(r'[^\w\d.-]', '.', data['sku'].upper())
    
    # Категория
    category = data['category'] if data['category'] else 'Станки >>> Прочее'
    
    row = {
        'ID': sku,
        'Title': title,
        'SKU': sku,
        'Type': item_type,
        'Brand': '',  # Без бренда по требованию
        'Category_Path': category,
        'Price': 0,  # Цену можно добавить позже
        'Currency': 'RUB',
        'Compatible_SKUs': data['compatible'],
        'Short_Description': data['description'],
        'Full_Description': data['full_text'],
        'Weight_KG': data['weight'],
        'Power_KW': data['power'],
        'Dimensions_MM': data['dimensions'],
        'Voltage_V': data['voltage'],
        'Main_Photo': f"{sku}_main.jpg",
        'Gallery_Photos': '',
        'Status': 'published'
    }
    
    catalog_data.append(row)

oleg_df = pd.DataFrame(catalog_data)

print(f"✅ Создано записей: {len(oleg_df)}")

# === ШАГ 4: СТАТИСТИКА ===
print("\n📊 СТАТИСТИКА:")
print(f"   Станков (machine): {(oleg_df['Type'] == 'machine').sum()}")
print(f"   Запчастей (spare): {(oleg_df['Type'] == 'spare').sum()}")
print(f"   С весом: {(oleg_df['Weight_KG'] != '').sum()}")
print(f"   С мощностью: {(oleg_df['Power_KW'] != '').sum()}")
print(f"   С габаритами: {(oleg_df['Dimensions_MM'] != '').sum()}")
print(f"   С напряжением: {(oleg_df['Voltage_V'] != '').sum()}")
print(f"   С совместимостью: {(oleg_df['Compatible_SKUs'] != '').sum()}")

# === ШАГ 5: ДОБАВЛЕНИЕ СЛУЖЕБНЫХ СТРОК ===
print("\n🔧 Добавление служебных строк...")

# Строка 1: Русские названия
row1 = {
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

# Строка 2: Описание формата
row2 = {
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

# Собираем финальный DataFrame
final_df = pd.concat([
    pd.DataFrame([row1, row2]),
    oleg_df
], ignore_index=True)

print(f"✅ Итого строк (с заголовками): {len(final_df)}")

# === ШАГ 6: СОХРАНЕНИЕ ===
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
output_csv = f"CATALOG_MACHINES_TURRETS_{timestamp}.csv"
output_excel = f"CATALOG_MACHINES_TURRETS_{timestamp}.xlsx"

print("\n💾 Сохранение...")

# CSV
final_df.to_csv(output_csv, index=False, encoding='utf-8-sig')
print(f"✅ CSV: {output_csv}")

# Excel
try:
    final_df.to_excel(output_excel, index=False, engine='openpyxl')
    print(f"✅ Excel: {output_excel}")
except Exception as e:
    print(f"⚠️  Excel не создан: {e}")

# === ШАГ 7: ПРИМЕРЫ ===
print("\n📦 ПРИМЕРЫ (строки 3-5, первые товары):")
for idx in range(2, min(5, len(final_df))):
    row = final_df.iloc[idx]
    print(f"\n{idx-1}. {row['Title']}")
    print(f"   SKU: {row['SKU']}")
    print(f"   Вес: {row['Weight_KG']} кг" if row['Weight_KG'] else "   Вес: -")
    print(f"   Мощность: {row['Power_KW']} кВт" if row['Power_KW'] else "   Мощность: -")
    print(f"   Габариты: {row['Dimensions_MM']}" if row['Dimensions_MM'] else "   Габариты: -")
    print(f"   Описание: {row['Short_Description'][:80]}...")

print("\n" + "="*80)
print("🎉 КАТАЛОГ СТАНКОВ И РЕВОЛЬВЕРНЫХ ГОЛОВОК СОЗДАН!")
print("="*80)
print(f"\n📁 Файлы в: {Path.cwd()}")
print(f"\n✉️  Файл для Олега: {output_excel}")
print("\n💡 Данные взяты из MD файлов docs/")
print("💡 Бренды удалены из текстов")
print("💡 Формат соответствует OLEG-Shablon.xlsx")
