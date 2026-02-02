#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎯 ПОЛНЫЙ КАТАЛОГ ДЛЯ ОЛЕГА С ДАННЫМИ ИЗ ТКП
Источник: ТКП файлы + FINAL_TILDA_CATALOG.csv
Формат: ТОЧНО как в шаблоне OLEG-Shablon.xlsx
"""

import pandas as pd
import re
from pathlib import Path
from datetime import datetime
import sys

print("="*80)
print("🎯 ПОЛНЫЙ КАТАЛОГ ДЛЯ ОЛЕГА (С ДАННЫМИ ИЗ ТКП)")
print("="*80)

# === ШАГ 1: ЧТЕНИЕ ТКП ФАЙЛОВ ===
print("\n📂 Чтение ТКП файлов...")

tkp_data = {}
repo_root = Path(__file__).parent.parent

# Читаем все MD файлы (кроме служебных/каталогов)
md_files = []
for p in repo_root.glob('**/*.md'):
    if any(part in {'.git', '.venv', 'catalogs'} for part in p.parts):
        continue
    if p.name in {'README.md', 'OLEG-1.md'}:
        continue
    md_files.append(p)

print(f"✅ Найдено MD файлов: {len(md_files)}")

for md_file in md_files:
    try:
        content = md_file.read_text(encoding='utf-8')
        
        # Извлекаем название из первого заголовка
        title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if not title_match:
            continue
            
        title = title_match.group(1).strip()
        
        # Извлекаем характеристики
        specs = {
            'title': title,
            'description': '',
            'full_text': '',
            'weight': '',
            'power': '',
            'dimensions': '',
            'voltage': '',
            'compatible': []
        }
        
        # Описание (первый абзац после заголовка)
        desc_match = re.search(r'##\s+(?:ТЕХНИЧЕСКИЕ ХАРАКТЕРИСТИКИ|Назначение и возможности)\s+(.+?)(?=##|$)', content, re.DOTALL)
        if desc_match:
            desc_text = desc_match.group(1).strip()
            # Берем первое предложение для краткого описания
            sentences = re.split(r'[.!?]+', desc_text)
            if sentences:
                specs['description'] = sentences[0].strip() + '.'
            # Полный текст
            specs['full_text'] = re.sub(r'\s+', ' ', desc_text[:500]).strip()
        
        # Вес
        weight_match = re.search(r'(?:вес|масса).*?(\d+(?:[\.,]\d+)?)\s*(?:кг|kg)', content, re.IGNORECASE)
        if weight_match:
            specs['weight'] = weight_match.group(1).replace(',', '.')
        
        # Мощность
        power_match = re.search(r'мощность.*?(\d+(?:[\.,]\d+)?)\s*(?:квт|kw)', content, re.IGNORECASE)
        if power_match:
            specs['power'] = power_match.group(1).replace(',', '.')
        
        # Габариты
        dim_match = re.search(r'габарит.*?(\d{3,4})\s*[xх×]\s*(\d{3,4})\s*[xх×]\s*(\d{3,4})', content, re.IGNORECASE)
        if dim_match:
            specs['dimensions'] = f"{dim_match.group(1)}x{dim_match.group(2)}x{dim_match.group(3)}"
        
        # Напряжение
        voltage_match = re.search(r'напряжение.*?(\d{2,3})\s*в', content, re.IGNORECASE)
        if voltage_match:
            specs['voltage'] = voltage_match.group(1)
        
        # Совместимые модели
        models = re.findall(r'\b(?:16К20|1М63|16К40|1Н65|1М65|РТ\d+|16А20Ф3|16М30Ф3)\b', content)
        specs['compatible'] = list(set(models))
        
        # Сохраняем по разным вариантам ключей
        tkp_data[title.lower()] = specs
        # Также по модели если есть
        for model in specs['compatible']:
            tkp_data[model.lower()] = specs
            
    except Exception as e:
        continue

print(f"✅ Загружено описаний: {len(tkp_data)}")

# === ШАГ 2: ЧТЕНИЕ КАТАЛОГА ===
print("\n📖 Чтение каталога...")

current_dir = Path.cwd()
csv_files = list(current_dir.glob("FINAL_TILDA_CATALOG.csv"))

if not csv_files:
    print("❌ FINAL_TILDA_CATALOG.csv не найден!")
    sys.exit(1)

df = pd.read_csv(csv_files[0], encoding='utf-8-sig')
print(f"✅ Загружено: {len(df)} товаров")

# === ШАГ 3: ФУНКЦИИ ОБРАБОТКИ ===

def clean_html(text):
    if pd.isna(text):
        return ""
    text = str(text)
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

BRAND_PATTERNS = [
    r'русс?танк[оа]сбыт',
    r'rossstanko(?:-rzn)?',
    r'росс?танк[оа]',
    r'росстанко',
    r'tdrusstankosbyt',
    r'русстанкосбыт',
    r'тд\s*русстанкосбыт'
]

def remove_brands(text):
    if pd.isna(text):
        return ""
    text = str(text)
    for pattern in BRAND_PATTERNS:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE)
    text = re.sub(r'\s{2,}', ' ', text)
    return text.strip()

def get_type(title):
    title = str(title).lower()
    if any(kw in title for kw in ['станок', 'machine', 'lathe']):
        return 'machine'
    return 'spare'

def get_brand(title):
    """Без упоминания брендов - оставляем пустым"""
    return ''

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

def find_tkp_data(title, sku, text):
    """Ищет данные в ТКП по названию, SKU или тексту"""
    # Пробуем разные варианты поиска
    search_keys = [
        str(title).lower(),
        str(sku).lower(),
    ]
    
    # Извлекаем модель из названия
    models = re.findall(r'\b(?:16К20|1М63|16К40|1Н65|1М65|РТ\d+|16А20Ф3|16М30Ф3)\b', str(title), re.IGNORECASE)
    search_keys.extend([m.lower() for m in models])
    
    # Ищем в ТКП
    for key in search_keys:
        for tkp_key, tkp_info in tkp_data.items():
            if key in tkp_key or tkp_key in key:
                return tkp_info
    
    return None

def get_description(row):
    """Получает краткое описание из ТКП или Text"""
    tkp = find_tkp_data(row.get('Title', ''), row.get('SKU', ''), row.get('Text', ''))
    
    if tkp and tkp.get('description'):
        return remove_brands(tkp['description'])[:150]
    
    # Если нет в ТКП - из Text
    text = remove_brands(clean_html(row.get('Text', '')))
    if text:
        sentences = re.split(r'[.!?]+', text)
        if sentences:
            return sentences[0].strip()[:150] + '.'
    
    return ""

def get_full_description(row):
    """Получает полное описание из ТКП или Text"""
    tkp = find_tkp_data(row.get('Title', ''), row.get('SKU', ''), row.get('Text', ''))
    
    if tkp and tkp.get('full_text'):
        return remove_brands(tkp['full_text'])
    
    return remove_brands(clean_html(row.get('Text', '')))

def get_weight(row):
    """Получает вес из ТКП или Text"""
    tkp = find_tkp_data(row.get('Title', ''), row.get('SKU', ''), row.get('Text', ''))
    
    if tkp and tkp.get('weight'):
        return tkp['weight']
    
    # Ищем в Text
    text = str(row.get('Text', ''))
    match = re.search(r'(\d+(?:[\.,]\d+)?)\s*кг', text, re.IGNORECASE)
    if match:
        return match.group(1).replace(',', '.')
    
    return ''

def get_power(row):
    """Получает мощность из ТКП или Text"""
    tkp = find_tkp_data(row.get('Title', ''), row.get('SKU', ''), row.get('Text', ''))
    
    if tkp and tkp.get('power'):
        return tkp['power']
    
    # Ищем в Text
    text = str(row.get('Text', ''))
    match = re.search(r'(\d+(?:[\.,]\d+)?)\s*квт', text, re.IGNORECASE)
    if match:
        return match.group(1).replace(',', '.')
    
    return ''

def get_dimensions(row):
    """Получает габариты из ТКП или Text"""
    tkp = find_tkp_data(row.get('Title', ''), row.get('SKU', ''), row.get('Text', ''))
    
    if tkp and tkp.get('dimensions'):
        return tkp['dimensions']
    
    # Ищем в Text
    text = str(row.get('Text', ''))
    match = re.search(r'(\d{3,4})\s*[xх×]\s*(\d{3,4})\s*[xх×]\s*(\d{3,4})', text)
    if match:
        return f"{match.group(1)}x{match.group(2)}x{match.group(3)}"
    
    return ''

def get_voltage(row):
    """Получает напряжение из ТКП или Text"""
    tkp = find_tkp_data(row.get('Title', ''), row.get('SKU', ''), row.get('Text', ''))
    
    if tkp and tkp.get('voltage'):
        return tkp['voltage']
    
    # Ищем в Text
    text = str(row.get('Text', ''))
    if '220/380' in text or '380/220' in text:
        return '220/380'
    if '380' in text:
        return '380'
    if '220' in text:
        return '220'
    
    return ''

def get_compatible(row):
    """Получает совместимость из ТКП"""
    tkp = find_tkp_data(row.get('Title', ''), row.get('SKU', ''), row.get('Text', ''))
    
    if tkp and tkp.get('compatible'):
        return ';'.join(sorted(tkp['compatible']))
    
    # Ищем в тексте
    text = str(row.get('Title', '')) + ' ' + str(row.get('Text', ''))
    models = re.findall(r'\b(?:16К20|1М63|16К40|1Н65|1М65|РТ\d+)\b', text)
    if models:
        return ';'.join(sorted(set(models)))
    
    return ''

# === ШАГ 4: СОЗДАНИЕ КАТАЛОГА ===
print("\n🔄 Создание каталога с данными из ТКП...")

# Создаем данные с применением функций
oleg_data = {
    'ID': df.get('SKU', df.get('Tilda UID', '')),
    'Title': df.get('Title', ''),
    'SKU': df.get('SKU', df.get('Tilda UID', '')),
    'Type': df['Title'].apply(get_type),
    'Brand': df['Title'].apply(get_brand),
    'Category_Path': df.get('Product Type', df.get('Category', '')).apply(format_category),
    'Price': pd.to_numeric(df.get('Price', 0), errors='coerce').fillna(0),
    'Currency': 'RUB',
    'Compatible_SKUs': df.apply(get_compatible, axis=1),
    'Short_Description': df.apply(get_description, axis=1),
    'Full_Description': df.apply(get_full_description, axis=1),
    'Weight_KG': df.apply(get_weight, axis=1),
    'Power_KW': df.apply(get_power, axis=1),
    'Dimensions_MM': df.apply(get_dimensions, axis=1),
    'Voltage_V': df.apply(get_voltage, axis=1),
    'Main_Photo': df.get('Photo', ''),
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
print(f"   С кратким описанием: {(oleg_df['Short_Description'] != '').sum()}")
print(f"   С полным описанием: {(oleg_df['Full_Description'] != '').sum()}")
print(f"   С весом: {(oleg_df['Weight_KG'] != '').sum()}")
print(f"   С мощностью: {(oleg_df['Power_KW'] != '').sum()}")
print(f"   С габаритами: {(oleg_df['Dimensions_MM'] != '').sum()}")
print(f"   С напряжением: {(oleg_df['Voltage_V'] != '').sum()}")
print(f"   С совместимостью: {(oleg_df['Compatible_SKUs'] != '').sum()}")

# === ШАГ 6: ДОБАВЛЕНИЕ СЛУЖЕБНЫХ СТРОК ===
print("\n🔧 Добавление служебных строк...")

template_rows = []
template_candidates = [
    current_dir / 'OLEG-Shablon.xlsx',
    current_dir / 'OLEG-Shablon-dropbox.xlsx'
]

for path in template_candidates:
    if path.exists():
        try:
            tpl = pd.read_excel(path)
            if len(tpl) >= 2:
                template_rows = [tpl.iloc[0].to_dict(), tpl.iloc[1].to_dict()]
                break
        except Exception:
            pass

if not template_rows:
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
    template_rows = [row1, row2]

# Собираем финальный DataFrame
final_df = pd.concat(
    [pd.DataFrame(template_rows), oleg_df],
    ignore_index=True
)

print(f"✅ Итого строк (с заголовками): {len(final_df)}")

# === ШАГ 7: СОХРАНЕНИЕ ===
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
output_csv = f"CATALOG_FOR_OLEG_FULL_{timestamp}.csv"
output_excel = f"CATALOG_FOR_OLEG_FULL_{timestamp}.xlsx"

print("\n💾 Сохранение...")

# CSV
final_df.to_csv(output_csv, index=False, encoding='utf-8-sig')
print(f"✅ CSV: {output_csv}")

# Excel
try:
    final_df.to_excel(output_excel, index=False, engine='openpyxl')
    print(f"✅ Excel: {output_excel}")
except:
    print("⚠️  Excel не создан (нет openpyxl)")

# === ШАГ 8: ПРИМЕРЫ ===
print("\n📦 ПРИМЕРЫ (строки 4-6, первые товары):")
for idx in range(3, min(6, len(final_df))):
    row = final_df.iloc[idx]
    print(f"\n{idx-2}. {row['Title'][:60]}")
    print(f"   SKU: {row['SKU']}")
    print(f"   Тип: {row['Type']}")
    print(f"   Вес: {row['Weight_KG']} кг")
    print(f"   Мощность: {row['Power_KW']} кВт")
    print(f"   Габариты: {row['Dimensions_MM']}")
    print(f"   Описание: {row['Short_Description'][:80]}...")

print("\n" + "="*80)
print("🎉 ПОЛНЫЙ КАТАЛОГ ДЛЯ ОЛЕГА СОЗДАН!")
print("="*80)
print(f"\n📁 Файлы в: {current_dir}")
print(f"\n✉️  Отправьте Олегу: {output_excel}")
print("\n💡 Формат ТОЧНО соответствует шаблону OLEG-Shablon.xlsx")
print("💡 Данные взяты из ТКП файлов репозитория")
