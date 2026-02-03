#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎯 АВТОМАТИЧЕСКИЙ ПАРСЕР ПОЛНЫХ ДАННЫХ С САЙТОВ
Парсит tdrusstankosbyt.ru и russtankosbyt.tilda.ws
Извлекает ВСЕ данные: назначение, характеристики, комплектацию, преимущества
Создает ПОЛНЫЙ каталог для Олега
"""

import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
from pathlib import Path
from datetime import datetime
import time

print("="*80)
print("🎯 АВТОМАТИЧЕСКИЙ ПАРСЕР ПОЛНЫХ ДАННЫХ ДЛЯ КАТАЛОГА ОЛЕГА")
print("="*80)

# === ФУНКЦИИ ПАРСИНГА ===

def parse_tdrusstankosbyt_page(url):
    """Парсит страницу tdrusstankosbyt.ru - извлекает ВСЕ данные"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code != 200:
            return None
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Извлекаем ВСЕ текстовое содержимое со страницы
        full_text = soup.get_text(separator='\n', strip=True)
        
        # Извлекаем заголовок
        title = soup.find('h1')
        title_text = title.get_text(strip=True) if title else ''
        
        # Извлекаем все параграфы и блоки с данными
        content_blocks = []
        
        # Ищем div'ы с классами содержащими текст/контент
        for div in soup.find_all(['div', 'section'], class_=re.compile(r't-text|t-descr|t396__elem|tn-atom')):
            text = div.get_text(separator=' ', strip=True)
            if text and len(text) > 20:
                content_blocks.append(text)
        
        # Если не нашли через классы, берем все p, h2, h3, ul, ol
        if not content_blocks:
            for tag in soup.find_all(['p', 'h2', 'h3', 'ul', 'ol', 'li']):
                text = tag.get_text(strip=True)
                if text and len(text) > 10:
                    content_blocks.append(text)
        
        # Объединяем все найденные блоки
        full_description = '\n\n'.join(content_blocks)
        
        # Извлекаем технические характеристики (вес, мощность, габариты, напряжение)
        weight = extract_weight(full_text)
        power = extract_power(full_text)
        dimensions = extract_dimensions(full_text)
        voltage = extract_voltage(full_text)
        
        # Извлекаем цену если есть
        price = extract_price(full_text)
        
        # Формируем краткое описание (первые 2-3 абзаца)
        short_description = '\n'.join(content_blocks[:3]) if len(content_blocks) >= 3 else '\n'.join(content_blocks)
        
        return {
            'title': title_text,
            'short_description': short_description[:500] if short_description else '',  # Первые 500 символов
            'full_description': full_description,
            'weight': weight,
            'power': power,
            'dimensions': dimensions,
            'voltage': voltage,
            'price': price,
            'url': url
        }
    except Exception as e:
        print(f"❌ Ошибка парсинга {url}: {e}")
        return None


def parse_tilda_page(url):
    """Парсит страницу russtankosbyt.tilda.ws"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code != 200:
            return None
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Извлекаем текст
        full_text = soup.get_text(separator='\n', strip=True)
        
        # Заголовок
        title = soup.find('h1')
        title_text = title.get_text(strip=True) if title else ''
        
        # Все текстовые блоки Tilda
        content_blocks = []
        for div in soup.find_all(['div'], class_=re.compile(r't-text|t-descr|t396__elem|tn-atom')):
            text = div.get_text(separator=' ', strip=True)
            if text and len(text) > 20:
                content_blocks.append(text)
        
        full_description = '\n\n'.join(content_blocks)
        short_description = '\n'.join(content_blocks[:3]) if len(content_blocks) >= 3 else '\n'.join(content_blocks)
        
        # Характеристики
        weight = extract_weight(full_text)
        power = extract_power(full_text)
        dimensions = extract_dimensions(full_text)
        voltage = extract_voltage(full_text)
        price = extract_price(full_text)
        
        return {
            'title': title_text,
            'short_description': short_description[:500] if short_description else '',
            'full_description': full_description,
            'weight': weight,
            'power': power,
            'dimensions': dimensions,
            'voltage': voltage,
            'price': price,
            'url': url
        }
    except Exception as e:
        print(f"❌ Ошибка парсинга {url}: {e}")
        return None


# === ФУНКЦИИ ИЗВЛЕЧЕНИЯ ХАРАКТЕРИСТИК ===

def extract_weight(text):
    """Извлекает вес в кг"""
    patterns = [
        r'(?:масса|вес).*?(\d+(?:\.\d+)?)\s*(?:кг|kg)',
        r'(\d+(?:\.\d+)?)\s*кг',
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1)
    return ''


def extract_power(text):
    """Извлекает мощность в кВт"""
    patterns = [
        r'мощность.*?(\d+(?:\.\d+)?)\s*кВт',
        r'(\d+(?:\.\d+)?)\s*кВт',
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1)
    return ''


def extract_dimensions(text):
    """Извлекает габариты в формате ДxШxВ"""
    patterns = [
        r'габариты.*?(\d+)\s*[xх×]\s*(\d+)\s*[xх×]\s*(\d+)',
        r'(\d+)\s*[xх×]\s*(\d+)\s*[xх×]\s*(\d+)\s*мм',
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
        r'(\d+)\s*В(?:\s|$)',
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            voltage = match.group(1)
            if voltage in ['220', '380', '400']:
                return voltage
    return '380'  # По умолчанию


def extract_price(text):
    """Извлекает цену"""
    patterns = [
        r'цена.*?(\d+(?:\s*\d+)*)\s*(?:руб|₽)',
        r'(\d+(?:\s*\d+)*)\s*(?:руб|₽)',
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            price_str = match.group(1).replace(' ', '')
            return int(price_str)
    return ''


# === СПИСОК СТРАНИЦ ДЛЯ ПАРСИНГА ===

URLS_TO_PARSE = {
    'СТАНКИ': [
        'https://tdrusstankosbyt.ru/stanokrtrt16k20',
        'https://russtankosbyt.tilda.ws/stanokrtrt16k20',
        'https://tdrusstankosbyt.ru/stanokrtrt1m63ndip300',
        'https://russtankosbyt.tilda.ws/stanokrtrt16k40',
        'https://tdrusstankosbyt.ru/stanokrtrt1n65ndip500',
        'https://tdrusstankosbyt.ru/stanokrt117',
        'https://tdrusstankosbyt.ru/stanokrtrt817',
    ],
    'РЕВОЛЬВЕРНЫЕ ГОЛОВКИ': [
        'https://tdrusstankosbyt.ru/remontrevolvernyhgolovok16k30f340000',
        'https://tdrusstankosbyt.ru/remontrevolvernyhgolovok',
        'https://russtankosbyt.tilda.ws/revolvernyagolovkachpu',
    ]
}


# === ГЛАВНАЯ ФУНКЦИЯ ===

def main():
    all_products = []
    
    for category, urls in URLS_TO_PARSE.items():
        print(f"\n{'='*80}")
        print(f"📁 Категория: {category}")
        print(f"{'='*80}\n")
        
        for url in urls:
            print(f"🌐 Парсинг: {url}")
            
            # Определяем какой парсер использовать
            if 'tilda.ws' in url:
                data = parse_tilda_page(url)
            else:
                data = parse_tdrusstankosbyt_page(url)
            
            if data:
                data['category'] = category
                all_products.append(data)
                print(f"✅ Успех! Заголовок: {data['title'][:60]}...")
                print(f"   Вес: {data['weight']} кг, Мощность: {data['power']} кВт")
                print(f"   Габариты: {data['dimensions']}, Напряжение: {data['voltage']} В")
                print(f"   Описание: {len(data['full_description'])} символов\n")
            else:
                print(f"❌ Не удалось распарсить\n")
            
            time.sleep(2)  # Пауза между запросами
    
    # === СОЗДАНИЕ EXCEL ===
    
    if not all_products:
        print("\n❌ Нет данных для создания каталога!")
        return
    
    print(f"\n{'='*80}")
    print(f"📊 СОЗДАНИЕ КАТАЛОГА")
    print(f"{'='*80}\n")
    
    # Создаем DataFrame
    rows = []
    for idx, product in enumerate(all_products, start=1):
        row = {
            'ID': f"PRODUCT.{idx:03d}",
            'Title': product['title'],
            'SKU': f"SKU.{idx:03d}",
            'Type': 'machine' if 'револьвер' not in product['category'].lower() else 'spare',
            'Brand': '',  # Без упоминания брендов
            'Category_Path': f"Каталог >>> {product['category']}",
            'Price': product.get('price', ''),
            'Currency': 'RUB' if product.get('price') else '',
            'Compatible_SKUs': '',
            'Short_Description': product['short_description'],
            'Full_Description': product['full_description'],
            'Weight_KG': product['weight'],
            'Power_KW': product['power'],
            'Dimensions_MM': product['dimensions'],
            'Voltage_V': product['voltage'],
            'Main_Photo': '',
            'Gallery_Photos': '',
            'Status': 'active'
        }
        rows.append(row)
    
    df = pd.DataFrame(rows)
    
    # Создаем заголовки как в шаблоне
    header_row_1 = pd.DataFrame([{
        'ID': 'ID товара',
        'Title': 'Название',
        'SKU': 'Артикул',
        'Type': 'Тип',
        'Brand': 'Бренд',
        'Category_Path': 'Путь категории',
        'Price': 'Цена',
        'Currency': 'Валюта',
        'Compatible_SKUs': 'Совместимые артикулы',
        'Short_Description': 'Краткое описание',
        'Full_Description': 'Полное описание',
        'Weight_KG': 'Вес (кг)',
        'Power_KW': 'Мощность (кВт)',
        'Dimensions_MM': 'Габариты (мм)',
        'Voltage_V': 'Напряжение (В)',
        'Main_Photo': 'Главное фото',
        'Gallery_Photos': 'Галерея фото',
        'Status': 'Статус'
    }])
    
    header_row_2 = pd.DataFrame([{
        'ID': 'число',
        'Title': 'текст',
        'SKU': 'текст',
        'Type': 'machine/spare/accessory',
        'Brand': 'текст',
        'Category_Path': 'Категория1 >>> Категория2',
        'Price': 'число',
        'Currency': 'RUB/USD/EUR',
        'Compatible_SKUs': 'SKU1, SKU2, SKU3',
        'Short_Description': 'текст до 500 символов',
        'Full_Description': 'полный текст',
        'Weight_KG': 'число',
        'Power_KW': 'число',
        'Dimensions_MM': 'ДxШxВ',
        'Voltage_V': '220/380',
        'Main_Photo': 'URL или путь',
        'Gallery_Photos': 'URL1, URL2, URL3',
        'Status': 'active/inactive'
    }])
    
    # Объединяем
    final_df = pd.concat([header_row_1, header_row_2, df], ignore_index=True)
    
    # Сохраняем
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file_xlsx = f"CATALOG_OLEG_FULL_AUTO_{timestamp}.xlsx"
    output_file_csv = f"CATALOG_OLEG_FULL_AUTO_{timestamp}.csv"
    
    final_df.to_excel(output_file_xlsx, index=False, engine='openpyxl')
    final_df.to_csv(output_file_csv, index=False, encoding='utf-8-sig')
    
    print(f"✅ Создано записей: {len(rows)}")
    print(f"📄 Файлы сохранены:")
    print(f"   - {output_file_xlsx}")
    print(f"   - {output_file_csv}")
    print(f"\n💡 ВСЕ ПОЛНЫЕ ОПИСАНИЯ извлечены с сайтов!")
    print("="*80)


if __name__ == "__main__":
    main()
