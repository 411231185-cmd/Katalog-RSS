#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎯 ПАРСИНГ С САЙТОВ И СОЗДАНИЕ КАТАЛОГА ДЛЯ ОЛЕГА
На основе final_parser_descriptions.py + формат OLEG-Shablon.xlsx

Парсит сайты :
1. tdrusstankosbyt.ru 
2. russtankosbyt.tilda.ws
3. russtanko-rzn.ru
4. rosstanko.com

Создает Excel ТОЧНО в формате шаблона Олега:
- Строка 1: ID, Title, SKU... (английские названия)
- Строка 2: ИДЕНТИФИКАТОР, НАЗВАНИЕ ТОВАРА... (русские названия)
- Строка 3: (системное), Текст... (примеры формата)
- Строка 4+: Данные продуктов
"""

import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import re
from pathlib import Path
from datetime import datetime

print("="*80)
print("🎯 ПАРСИНГ САЙТОВ И СОЗДАНИЕ КАТАЛОГА ДЛЯ ОЛЕГА")
print("="*80)


# === ФУНКЦИИ ПАРСИНГА ===

def clean_text(text):
    """Очистка текста от лишних пробелов и мусора"""
    if not text:
        return ''
    # Удаляем лишние пробелы
    text = re.sub(r'\s+', ' ', text)
    # Удаляем упоминания брендов
    text = re.sub(r'руссстанко\s*сбыт|rossstanko|tdrusstankosbyt', '', text, flags=re.IGNORECASE)
    return text.strip()


def extract_weight(text):
    """Извлекает вес в кг"""
    patterns = [
        r'масса.*?(\d+(?:[.,]\d+)?)\s*кг',
        r'вес.*?(\d+(?:[.,]\d+)?)\s*кг',
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).replace(',', '.')
    return ''


def extract_power(text):
    """Извлекает мощность в кВт"""
    patterns = [
        r'мощность.*?(\d+(?:[.,]\d+)?)\s*кВт',
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).replace(',', '.')
    return ''


def extract_dimensions(text):
    """Извлекает габариты"""
    patterns = [
        r'габариты.*?(\d+)\s*[xх×]\s*(\d+)\s*[xх×]\s*(\d+)',
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return f"{match.group(1)}x{match.group(2)}x{match.group(3)}"
    return ''


def extract_voltage(text):
    """Извлекает напряжение в В"""
    patterns = [
        r'напряжение.*?(\d+)\s*В',
        r'(\d+)\s*В(?:\s|,|$)',
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            voltage = match.group(1)
            if voltage in ['220', '380', '400']:
                return voltage
    return '380'


def extract_price(text):
    """Извлекает цену"""
    patterns = [
        r'цена.*?(\d+(?:\s*\d+)*)\s*(?:руб|₽)',
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            price_str = match.group(1).replace(' ', '')
            return int(price_str)
    return ''


def parse_tdrusstankosbyt_page(url):
    """Парсит страницу tdrusstankosbyt.ru с ПОЛНЫМ извлечением контента"""
    try:
        print(f"  🌐 Парсинг: {url}")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code != 200:
            print(f"  ❌ Статус {response.status_code}")
            return None
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Удаляем мусорные теги
        for tag in soup(['script', 'style', 'nav', 'footer', 'header', 'iframe']):
            tag.decompose()
        
        # Извлекаем заголовок
        title = soup.find('h1')
        title_text = clean_text(title.get_text()) if title else ''
        
        # Извлекаем ВЕСЬ текст со страницы
        full_text = soup.get_text(separator=' ', strip=True)
        full_text_clean = clean_text(full_text)
        
        # Короткое описание (первые 400 символов смыслового текста)
        short_desc = ''
        paragraphs = soup.find_all(['p', 'div'], string=re.compile(r'\w{20,}'))
        if paragraphs:
            texts = [clean_text(p.get_text()) for p in paragraphs if len(clean_text(p.get_text())) > 50]
            short_desc = ' '.join(texts[:2])[:400]
        
        # Полное описание (весь контент, максимум 3000 символов)
        full_desc = full_text_clean[:3000] if full_text_clean else ''
        
        # Извлекаем характеристики
        weight = extract_weight(full_text_clean)
        power = extract_power(full_text_clean)
        dimensions = extract_dimensions(full_text_clean)
        voltage = extract_voltage(full_text_clean)
        price = extract_price(full_text_clean)
        
        print(f"  ✅ Успех! {title_text[:50]}...")
        print(f"     Вес: {weight} кг, Мощность: {power} кВт, Габариты: {dimensions}")
        
        return {
            'title': title_text,
            'short_desc': short_desc,
            'full_desc': full_desc,
            'weight': weight,
            'power': power,
            'dimensions': dimensions,
            'voltage': voltage,
            'price': price,
            'url': url
        }
    
    except Exception as e:
        print(f"  ❌ Ошибка: {e}")
        return None


def parse_tilda_page(url):
    """Парсит страницу russtankosbyt.tilda.ws"""
    try:
        print(f"  🌐 Парсинг Tilda: {url}")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code != 200:
            print(f"  ❌ Статус {response.status_code}")
            return None
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        for tag in soup(['script', 'style', 'nav', 'footer', 'header']):
            tag.decompose()
        
        title = soup.find('h1')
        title_text = clean_text(title.get_text()) if title else ''
        
        # Tilda - ищем блоки с классами t-text, t-descr
        content_blocks = []
        for div in soup.find_all(['div'], class_=re.compile(r't-text|t-descr|t396__elem|tn-atom')):
            text = clean_text(div.get_text())
            if text and len(text) > 30:
                content_blocks.append(text)
        
        full_text = ' '.join(content_blocks)
        short_desc = ' '.join(content_blocks[:2])[:400] if len(content_blocks) >= 2 else full_text[:400]
        full_desc = full_text[:3000]
        
        weight = extract_weight(full_text)
        power = extract_power(full_text)
        dimensions = extract_dimensions(full_text)
        voltage = extract_voltage(full_text)
        price = extract_price(full_text)
        
        print(f"  ✅ Tilda: {title_text[:50]}...")
        
        return {
            'title': title_text,
            'short_desc': short_desc,
            'full_desc': full_desc,
            'weight': weight,
            'power': power,
            'dimensions': dimensions,
            'voltage': voltage,
            'price': price,
            'url': url
        }
    
    except Exception as e:
        print(f"  ❌ Ошибка Tilda: {e}")
        return None


# === СПИСОК URL ДЛЯ ПАРСИНГА ===

URLS_TO_PARSE = [
    # СТАНКИ
    ('https://tdrusstankosbyt.ru/stanokrtrt16k20', 'machine', 'Станки >>> Токарно-винторезные'),
    ('https://russtankosbyt.tilda.ws/stanokrtrt16k20', 'machine', 'Станки >>> Токарно-винторезные'),
    ('https://tdrusstankosbyt.ru/stanokrtrt1m63ndip300', 'machine', 'Станки >>> Токарно-винторезные'),
    ('https://russtankosbyt.tilda.ws/stanokrtrt16k40', 'machine', 'Станки >>> Токарно-винторезные'),
    ('https://tdrusstankosbyt.ru/stanokrtrt1n65ndip500', 'machine', 'Станки >>> Токарно-винторезные'),
    ('https://tdrusstankosbyt.ru/stanokrt117', 'machine', 'Станки >>> Токарно-винторезные'),
    ('https://tdrusstankosbyt.ru/stanokrtrt817', 'machine', 'Станки >>> Токарно-винторезные'),
    
    # РЕВОЛЬВЕРНЫЕ ГОЛОВКИ
    ('https://tdrusstankosbyt.ru/remontrevolvernyhgolovok16k30f340000', 'spare', 'Запчасти >>> Револьверные головки'),
    ('https://tdrusstankosbyt.ru/remontrevolvernyhgolovok', 'spare', 'Запчасти >>> Револьверные головки'),
    ('https://russtankosbyt.tilda.ws/revolvernyagolovkachpu', 'spare', 'Запчасти >>> Револьверные головки'),
]


# === ГЛАВНАЯ ФУНКЦИЯ ===

def main():
    print(f"\n📋 Всего URL для парсинга: {len(URLS_TO_PARSE)}\n")
    
    parsed_data = []
    
    for url, product_type, category in URLS_TO_PARSE:
        # Выбираем парсер
        if 'tilda.ws' in url:
            data = parse_tilda_page(url)
        else:
            data = parse_tdrusstankosbyt_page(url)
        
        if data:
            data['type'] = product_type
            data['category'] = category
            parsed_data.append(data)
        
        time.sleep(2)  # Пауза между запросами
    
    if not parsed_data:
        print("\n❌ Нет данных для создания каталога!")
        return
    
    print(f"\n{'='*80}")
    print(f"📊 СОЗДАНИЕ EXCEL В ФОРМАТЕ ШАБЛОНА ОЛЕГА")
    print(f"{'='*80}\n")
    
    # === ФОРМИРУЕМ ДАННЫЕ В ФОРМАТЕ ОЛЕГА ===
    
    # СТРОКА 1: Английские названия колонок
    row_1 = {
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
    
    # СТРОКА 2: Русские названия
    row_2 = {
        'ID': 'ИДЕНТИФИКАТОР',
        'Title': 'НАЗВАНИЕ ТОВАРА',
        'SKU': 'АРТИКУЛ',
        'Type': 'ТИП ОБЪЕКТА',
        'Brand': 'БРЕНД',
        'Category_Path': 'ПУТЬ КАТЕГОРИИ',
        'Price': 'ЦЕНА',
        'Currency': 'ВАЛЮТА',
        'Compatible_SKUs': 'СОВМЕСТИМЫЕ АРТИКУЛЫ',
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
    
    # СТРОКА 3: Примеры формата
    row_3 = {
        'ID': '(системное)',
        'Title': 'Текст',
        'SKU': 'Уникальный код',
        'Type': 'machine / spare',
        'Brand': 'Текст',
        'Category_Path': 'Разделитель >>>',
        'Price': 'Число',
        'Currency': 'RUB / USD',
        'Compatible_SKUs': 'через ;',
        'Short_Description': 'до 500 символов',
        'Full_Description': 'полный текст',
        'Weight_KG': 'число',
        'Power_KW': 'число',
        'Dimensions_MM': 'ДxШxВ',
        'Voltage_V': '220 / 380',
        'Main_Photo': 'URL',
        'Gallery_Photos': 'через ;',
        'Status': 'published / draft'
    }
    
    # СТРОКИ С ДАННЫМИ
    data_rows = []
    for idx, product in enumerate(parsed_data, start=1):
        row = {
            'ID': '',  # Пусто как в шаблоне
            'Title': product['title'],
            'SKU': f"{product['type'].upper()}.{idx:03d}",
            'Type': product['type'],
            'Brand': '',  # Пусто - без упоминания брендов
            'Category_Path': product['category'],
            'Price': product.get('price', ''),
            'Currency': 'RUB' if product.get('price') else '',
            'Compatible_SKUs': '',
            'Short_Description': product['short_desc'],
            'Full_Description': product['full_desc'],
            'Weight_KG': product['weight'],
            'Power_KW': product['power'],
            'Dimensions_MM': product['dimensions'],
            'Voltage_V': product['voltage'],
            'Main_Photo': '',
            'Gallery_Photos': '',
            'Status': 'published'
        }
        data_rows.append(row)
    
    # Объединяем все строки
    all_rows = [row_1, row_2, row_3] + data_rows
    
    # Создаем DataFrame
    df = pd.DataFrame(all_rows)
    
    # Сохраняем
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_xlsx = f"CATALOG_OLEG_PARSED_{timestamp}.xlsx"
    output_csv = f"CATALOG_OLEG_PARSED_{timestamp}.csv"
    
    df.to_excel(output_xlsx, index=False, header=False, engine='openpyxl')
    df.to_csv(output_csv, index=False, header=False, encoding='utf-8-sig')
    
    print(f"✅ Создано товаров: {len(parsed_data)}")
    print(f"📄 Файлы сохранены:")
    print(f"   - {output_xlsx}")
    print(f"   - {output_csv}")
    print(f"\n💡 Формат ТОЧНО соответствует шаблону Олега!")
    print(f"   - Строка 1: ID, Title, SKU...")
    print(f"   - Строка 2: ИДЕНТИФИКАТОР, НАЗВАНИЕ ТОВАРА...")
    print(f"   - Строка 3: (системное), Текст...")
    print(f"   - Строки 4+: Данные продуктов")
    print("="*80)


if __name__ == "__main__":
    main()
