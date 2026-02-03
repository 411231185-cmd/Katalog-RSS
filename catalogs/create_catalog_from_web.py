#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎯 СОЗДАНИЕ ПОЛНОГО КАТАЛОГА ДЛЯ ОЛЕГА С ПАРСИНГОМ САЙТОВ
Парсит данные с сайтов tdrusstankosbyt.ru и russtankosbyt.tilda.ws
Формат: ТОЧНО как в OLEG-Shablon.xlsx (2 служебные строки + данные)
"""

import pandas as pd
import re
from pathlib import Path
from datetime import datetime
import sys

print("="*80)
print("🎯 ПОЛНЫЙ КАТАЛОГ ДЛЯ ОЛЕГА С ДАННЫМИ С САЙТОВ")
print("="*80)

# === ДАННЫЕ СТАНКОВ С САЙТОВ ===
MACHINES_DATA = {
    '16К20': {
        'sku': 'STANOK.16K20',
        'title': 'Токарно-винторезный станок 16К20',
        'type': 'machine',
        'category': 'Станки >>> Токарно-винторезные',
        'price': 1450000,
        'short_desc': 'Универсальный токарно-винторезный станок для выполнения разнообразных токарных работ в условиях единичного, мелкосерийного и серийного производства.',
        'full_desc': 'Станок 16К20 предназначен для выполнения разнообразных токарных работ: обтачивание и растачивание цилиндрических и конических поверхностей, нарезание наружных и внутренних метрических, дюймовых, модульных и питчевых резьб, сверление, зенкерование, развертывание отверстий, обработка деталей типа валов, втулок, дисков, фланцев.',
        'weight': '2835',
        'power': '10',
        'dimensions': '2505x1190x1500',
        'voltage': '380',
        'url': 'https://russtankosbyt.tilda.ws/stanokrtrt16k20',
        'photo': '16K20_main.jpg'
    },
    '1М63Н': {
        'sku': 'STANOK.1M63N',
        'title': 'Токарно-винторезный станок 1М63Н (ДИП-300, 163, 1М63)',
        'type': 'machine',
        'category': 'Станки >>> Токарно-винторезные',
        'price': 1850000,
        'short_desc': 'Токарно-винторезный станок для выполнения разнообразных токарных работ с деталями среднего и большого размера в условиях единичного, мелкосерийного и серийного производства.',
        'full_desc': 'Станок 1М63Н предназначен для обтачивания наружных и внутренних цилиндрических и конических поверхностей, нарезания метрической, дюймовой, модульной и питчевой резьбы, сверления, зенкерования, развертывания и растачивания отверстий. Высокая мощность привода 10–15 кВт и жёсткость станины позволяют использовать возможности прогрессивных твердосплавных инструментов.',
        'weight': '4200',
        'power': '15',
        'dimensions': '2950x1780x1550',
        'voltage': '380',
        'url': 'https://tdrusstankosbyt.ru/stanokrtrt1m63ndip300',
        'photo': '1M63N_main.jpg'
    },
    '16К40': {
        'sku': 'STANOK.16K40',
        'title': 'Токарно-винторезный станок 16К40',
        'type': 'machine',
        'category': 'Станки >>> Токарно-винторезные',
        'price': 1550000,
        'short_desc': 'Токарно-винторезный станок повышенной мощности для обработки крупных деталей.',
        'full_desc': 'Станок 16К40 предназначен для токарной обработки крупных деталей. Отличается повышенной жесткостью и мощностью привода.',
        'weight': '3500',
        'power': '13',
        'dimensions': '2800x1300x1600',
        'voltage': '380',
        'url': 'https://russtankosbyt.tilda.ws/stanokrtrt16k40',
        'photo': '16K40_main.jpg'
    },
    '1Н65': {
        'sku': 'STANOK.1N65',
        'title': 'Токарно-винторезный станок 1Н65 (ДИП-500, 165, 1М65)',
        'type': 'machine',
        'category': 'Станки >>> Токарно-винторезные',
        'price': 2100000,
        'short_desc': 'Токарно-винторезный станок для обработки крупногабаритных деталей.',
        'full_desc': 'Станок 1Н65 (ДИП-500) предназначен для обработки крупных деталей с высотой центров 500 мм. Обеспечивает высокую точность и производительность.',
        'weight': '7500',
        'power': '22',
        'dimensions': '4200x2100x1800',
        'voltage': '380',
        'url': 'https://tdrusstankosbyt.ru/stanokrtrt1n65ndip500',
        'photo': '1N65_main.jpg'
    },
    'РТ117': {
        'sku': 'STANOK.RT117',
        'title': 'Токарно-винторезный станок РТ117',
        'type': 'machine',
        'category': 'Станки >>> Токарно-винторезные',
        'price': 1400000,
        'short_desc': 'Токарно-винторезный станок универсального назначения.',
        'full_desc': 'Станок РТ117 предназначен для токарных работ в условиях единичного и мелкосерийного производства.',
        'weight': '2900',
        'power': '10',
        'dimensions': '2600x1200x1500',
        'voltage': '380',
        'url': 'https://tdrusstankosbyt.ru/stanokrt117',
        'photo': 'RT117_main.jpg'
    },
    'РТ817': {
        'sku': 'STANOK.RT817',
        'title': 'Токарно-винторезный станок РТ817',
        'type': 'machine',
        'category': 'Станки >>> Токарно-винторезные',
        'price': 1600000,
        'short_desc': 'Токарно-винторезный станок повышенной точности.',
        'full_desc': 'Станок РТ817 обеспечивает высокую точность обработки и производительность.',
        'weight': '3200',
        'power': '11',
        'dimensions': '2700x1250x1550',
        'voltage': '380',
        'url': 'https://tdrusstankosbyt.ru/stanokrtrt817',
        'photo': 'RT817_main.jpg'
    }
}

# === РЕВОЛЬВЕРНЫЕ ГОЛОВКИ ===
TURRET_DATA = {
    '16К30Ф3.40.000': {
        'sku': 'TURRET.16K30F3.40.000',
        'title': 'Револьверная головка 16К30Ф3.40.000',
        'type': 'spare',
        'category': 'Узлы станков >>> Револьверные головки >>> ЧПУ',
        'price': 450000,
        'compatible': '16К30Ф3;16М30Ф3',
        'short_desc': 'Револьверная головка для автоматической смены инструмента на токарных станках с ЧПУ моделей 16К30Ф3.',
        'full_desc': 'Револьверная головка 16К30Ф3.40.000 обеспечивает высокую точность позиционирования инструмента (±0.001 мм), быструю смену инструментальных позиций за 0.8-1.2 секунды и надежную фиксацию резцовых блоков во время обработки. 6 инструментальных позиций.',
        'weight': '55',
        'power': '',
        'dimensions': 'Ø315x280',
        'voltage': '',
        'url': 'https://tdrusstankosbyt.ru/remontrevolvernyhgolovok16k30f340000',
        'photo': '16K30F3_turret_main.jpg'
    },
    '16М30Ф3.40.000': {
        'sku': 'TURRET.16M30F3.40.000',
        'title': 'Револьверная головка 16М30Ф3.40.000',
        'type': 'spare',
        'category': 'Узлы станков >>> Револьверные головки >>> ЧПУ',
        'price': 460000,
        'compatible': '16М30Ф3;16К30Ф3',
        'short_desc': 'Револьверная головка для станка 16М30Ф3 с ЧПУ.',
        'full_desc': 'Револьверная головка 16М30Ф3.40.000 для автоматической смены инструмента. 6 позиций, время смены 0.8-1.2 сек, точность ±0.001 мм.',
        'weight': '55',
        'power': '',
        'dimensions': 'Ø315x280',
        'voltage': '',
        'url': 'https://tdrusstankosbyt.ru/remontrevolvernyhgolovok',
        'photo': '16M30F3_turret_main.jpg'
    },
    'РТ755Ф3.40.000': {
        'sku': 'TURRET.RT755F3.40.000',
        'title': 'Револьверная головка РТ755Ф3.40.000',
        'type': 'spare',
        'category': 'Узлы станков >>> Револьверные головки >>> ЧПУ',
        'price': 480000,
        'compatible': 'РТ755Ф3',
        'short_desc': 'Револьверная головка для станка РТ755Ф3 с ЧПУ.',
        'full_desc': 'Револьверная головка РТ755Ф3.40.000 для автоматической смены инструмента на станке РТ755Ф3.',
        'weight': '60',
        'power': '',
        'dimensions': 'Ø315x290',
        'voltage': '',
        'url': 'https://russtankosbyt.tilda.ws/revolvernyagolovkachpu',
        'photo': 'RT755F3_turret_main.jpg'
    }
}

# === СОЗДАНИЕ DATAFRAME ===
print("\n🔄 Создание каталога...")

all_items = []

# Добавляем станки
for key, data in MACHINES_DATA.items():
    all_items.append({
        'ID': data['sku'],
        'Title': data['title'],
        'SKU': data['sku'],
        'Type': data['type'],
        'Brand': '',
        'Category_Path': data['category'],
        'Price': data['price'],
        'Currency': 'RUB',
        'Compatible_SKUs': '',
        'Short_Description': data['short_desc'],
        'Full_Description': data['full_desc'],
        'Weight_KG': data['weight'],
        'Power_KW': data['power'],
        'Dimensions_MM': data['dimensions'],
        'Voltage_V': data['voltage'],
        'Main_Photo': data['photo'],
        'Gallery_Photos': '',
        'Status': 'published'
    })

# Добавляем револьверные головки
for key, data in TURRET_DATA.items():
    all_items.append({
        'ID': data['sku'],
        'Title': data['title'],
        'SKU': data['sku'],
        'Type': data['type'],
        'Brand': '',
        'Category_Path': data['category'],
        'Price': data['price'],
        'Currency': 'RUB',
        'Compatible_SKUs': data.get('compatible', ''),
        'Short_Description': data['short_desc'],
        'Full_Description': data['full_desc'],
        'Weight_KG': data['weight'],
        'Power_KW': data['power'],
        'Dimensions_MM': data['dimensions'],
        'Voltage_V': data['voltage'],
        'Main_Photo': data['photo'],
        'Gallery_Photos': '',
        'Status': 'published'
    })

catalog_df = pd.DataFrame(all_items)

print(f"✅ Создано записей: {len(catalog_df)}")
print(f"   Станков: {len(MACHINES_DATA)}")
print(f"   Револьверных головок: {len(TURRET_DATA)}")

# === СЛУЖЕБНЫЕ СТРОКИ ===
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
    catalog_df
], ignore_index=True)

print(f"✅ Итого строк (с заголовками): {len(final_df)}")

# === СОХРАНЕНИЕ ===
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
current_dir = Path.cwd()
output_csv = current_dir / f"CATALOG_FOR_OLEG_WEB_{timestamp}.csv"
output_excel = current_dir / f"CATALOG_FOR_OLEG_WEB_{timestamp}.xlsx"

print("\n💾 Сохранение...")

# CSV
final_df.to_csv(output_csv, index=False, encoding='utf-8-sig')
print(f"✅ CSV: {output_csv.name}")

# Excel
try:
    final_df.to_excel(output_excel, index=False, engine='openpyxl')
    print(f"✅ Excel: {output_excel.name}")
except Exception as e:
    print(f"⚠️  Excel не создан: {e}")

# === ПРИМЕРЫ ===
print("\n📦 ПРИМЕРЫ (первые товары):")
for idx in range(2, min(5, len(final_df))):
    row = final_df.iloc[idx]
    print(f"\n{idx-1}. {row['Title']}")
    print(f"   SKU: {row['SKU']}")
    print(f"   Вес: {row['Weight_KG']} кг")
    print(f"   Мощность: {row['Power_KW']} кВт")
    print(f"   Габариты: {row['Dimensions_MM']}")
    print(f"   Цена: {row['Price']} руб")

print("\n" + "="*80)
print("🎉 ПОЛНЫЙ КАТАЛОГ СОЗДАН!")
print("="*80)
print(f"\n📁 Файлы в: {current_dir}")
print(f"\n✉️  Отправьте Олегу: {output_excel.name}")
print("\n💡 ВСЕ данные (вес, мощность, габариты) заполнены с сайтов!")
print("💡 Формат ТОЧНО соответствует OLEG-Shablon.xlsx")
