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


# === УНИВЕРСАЛЬНЫЙ ПАРСЕР ДЛЯ ВСЕХ САЙТОВ ===
def get_soup(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            return BeautifulSoup(response.text, 'html.parser')
    except Exception as e:
        print(f"❌ Ошибка доступа к {url}: {e}")
    return None

def extract_spec(text, patterns, default=''):
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
        if match:
            return match.group(1).strip()
    return default

def parse_generic_page(url):
    soup = get_soup(url)
    if not soup:
        return None

    # Удаляем скрипты и стили
    for script in soup(["script", "style"]):
        script.decompose()

    title = soup.find('h1')
    title_text = title.get_text(strip=True) if title else 'Без названия'
    
    # Сбор контента
    content_blocks = []
    # Специфика для Tilda и основных сайтов
    tags = soup.find_all(['div', 'p', 'h2', 'h3', 'li', 'tr'], class_=re.compile(r't-text|t-descr|t396|tn-atom|product|content'))
    if not tags: # Если классов нет, берем стандартные теги
        tags = soup.find_all(['p', 'h2', 'h3', 'li', 'td'])
    for tag in tags:
        text = tag.get_text(separator=' ', strip=True)
        if text and len(text) > 15:
            content_blocks.append(text)

    full_text = "\n".join(content_blocks)
    
    # Извлечение ТТХ через улучшенные паттерны
    data = {
        'title': title_text,
        'url': url,
        'full_description': "\n\n".join(list(dict.fromkeys(content_blocks))), # удаляем дубли
        'weight': extract_spec(full_text, [r'(?:масса|вес).*?(\d[\d\s]*)\s*(?:кг|т|kg|t)', r'(\d[\d\s]*)\s*кг']),
        'power': extract_spec(full_text, [r'(?:мощность|привод).*?(\d+(?:\.\d+)?)\s*кВт', r'(\d+(?:\.\d+)?)\s*кВт']),
        'dimensions': extract_spec(full_text, [r'(\d+)\s*[xх×]\s*(\d+)\s*[xх×]\s*(\d+)\s*мм']),
        'spindle': extract_spec(full_text, [r'(?:отверстие|шпиндел).*?(\d+)\s*мм']),
        'rmc': extract_spec(full_text, [r'(?:РМЦ|расстояние.*?центр).*?(\d+)\s*мм']),
        'price': extract_spec(full_text, [r'цена.*?(\d[\d\s]*)\s*(?:руб|₽)', r'(\d[\d\s]*)\s*₽']),
    }
    # Очистка цены от пробелов
    if data['price']:
        data['price'] = re.sub(r'\s+', '', data['price'])
    # Краткое описание
    data['short_description'] = "\n".join(content_blocks[:3])[:500] if content_blocks else ''
    return data


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



# === СПИСОК СТРАНИЦ ДЛЯ ПАРСИНГА (5+ сайтов) ===

# Уникальные ссылки для станков
STANKI_URLS = [
    'https://td-rss.ru/stanok-1n65',
    'https://tdrusstankosbyt.ru/stanokrtrt1n65ndip500',
    'https://tdrusstankosbyt.ru/stanokrtrt1m63ndip300',
    'https://tdrusstankosbyt.ru/stanokrtrt16k20',
    'https://rosstanko.com/stanok-1n65',
    'https://russtanko-rzn.ru/stanok-1n65',
    'https://stankoartel.com/stanok-1n65',
    'https://pasportanastanki.ru/',
    'https://russtankosbyt.tilda.ws/stanokrtrt16k20',
    'https://russtankosbyt.tilda.ws/stanokrtrt16k40',
    'https://tdrusstankosbyt.ru/stanokrtrt817',
    'https://tdrusstankosbyt.ru/stanokrt117',
    'https://tdrusstankosbyt.ru/stanokchpu16303',
    'https://tdrusstankosbyt.ru/stanokchpu7553',
    'https://tdrusstankosbyt.ru/stanokchpu305',
    'https://tdrusstankosbyt.ru/stanokchpu1620f3',
    'https://tdrusstankosbyt.ru/stanokchpu7793',
    'https://tdrusstankosbyt.ru/stanokrt5001',
    'https://tdrusstankosbyt.ru/stanokrt5003',
    'https://tdrusstankosbyt.ru/stanokrt5004',
    'https://tdrusstankosbyt.ru/stanokrtrt30101',
    'https://tdrusstankosbyt.ru/stanokrtrt301',
    'https://tdrusstankosbyt.ru/stanokrtrt30102',
    'https://tdrusstankosbyt.ru/stanokrtrt917',
    'https://tdrusstankosbyt.ru/stanokrtrt16p25',
    'https://tdrusstankosbyt.ru/stanok1a983',
    'https://tdrusstankosbyt.ru/stanok1h983',
    'https://tdrusstankosbyt.ru/stanokrt783',
    'https://tdrusstankosbyt.ru/#opisanie-stanok-817-Obshii',
]

# Уникальные ссылки для запчастей
ZAPCHASTI_URLS = [
    'https://tdrusstankosbyt.ru/valy',
    'https://tdrusstankosbyt.ru/kolesazubchatiye',
    'https://rosstanko.com/valy',
    'https://russtanko-rzn.ru/valy',
    'https://stankoartel.com/valy',
    'https://tdrusstankosbyt.ru/shesterninazakaz',
    'https://tdrusstankosbyt.ru/shesternidlachpu',
    'https://russtankosbyt.tilda.ws/rezcovyblok',
    'https://tdrusstankosbyt.ru/remontrevolvernyhgolovok',
    'https://tdrusstankosbyt.ru/remontrevolvernyhgolovokzapchasti',
    'https://tdrusstankosbyt.ru/remontrevolvernyhgolovok16k30f340000',
    'https://tdrusstankosbyt.ru/revolvernyagolovkachpu',
    'https://tdrusstankosbyt.ru/chpu16303',
    'https://tdrusstankosbyt.ru/korobkipodach',
    'https://tdrusstankosbyt.ru/shvp',
    'https://tdrusstankosbyt.ru/shpindelnyibabki',
    'https://tdrusstankosbyt.ru/zadniibabki',
    'https://tdrusstankosbyt.ru/rezcovyblok',
    'https://tdrusstankosbyt.ru/rolikiuprrt30101f110',
    'https://tdrusstankosbyt.ru/rolikisgalgrt301f180',
    'https://tdrusstankosbyt.ru/shvp-kozuhi',
    'https://tdrusstankosbyt.ru/shpindel1m65',
    'https://tdrusstankosbyt.ru/vinty',
    'https://tdrusstankosbyt.ru/rejki',
    'https://tdrusstankosbyt.ru/karetki',
    'https://tdrusstankosbyt.ru/support',
    'https://tdrusstankosbyt.ru/muftaobgonnaya',
    'https://tdrusstankosbyt.ru/gajkimatochniye',
    'https://tdrusstankosbyt.ru/frikcionvsbore',
    'https://tdrusstankosbyt.ru/diski',
    'https://tdrusstankosbyt.ru/kolesakonicheskiye',
    'https://tdrusstankosbyt.ru/cherwiachniyepary',
    'https://tdrusstankosbyt.ru/frikcionniyemufty',
    'https://tdrusstankosbyt.ru/gajki',
    'https://tdrusstankosbyt.ru/komplektujushiekuzlam',
    'https://tdrusstankosbyt.ru/patroni',
    'https://tdrusstankosbyt.ru/kulachki',
    'https://tdrusstankosbyt.ru/zachvativkladishi',
    'https://tdrusstankosbyt.ru/venci',
    'https://tdrusstankosbyt.ru/polzushki',
    'https://tdrusstankosbyt.ru/suchari',
    'https://russtankosbyt.tilda.ws/remontrevolvernyhgolovok16m30f340000',
    'https://russtankosbyt.tilda.ws/remontrevolvernyhgolovok1p756dfz39000',
    'https://russtankosbyt.tilda.ws/remontrevolvernyhgolovok1p756dfz40000',
    'https://russtankosbyt.tilda.ws/remontrevolvernyhgolovokrt755f340000',
]


# === ГЛАВНАЯ ФУНКЦИЯ ===



    all_products = []
    for category, urls in URLS_TO_PARSE.items():
        print(f"\n{'='*80}")
        print(f"📁 Категория: {category}")
        print(f"{'='*80}\n")
        for url in urls:
            print(f"🌐 Парсинг: {url}")
            data = parse_generic_page(url)
            if data:
                data['category'] = category
                all_products.append(data)
                print(f"✅ Успех! Заголовок: {data['title'][:60]}...")
                print(f"   Вес: {data.get('weight','')} кг, Мощность: {data.get('power','')} кВт")
                print(f"   Габариты: {data.get('dimensions','')}, Цена: {data.get('price','')}")
                print(f"   Описание: {len(data['full_description'])} символов\n")
            else:
                print(f"❌ Не удалось распарсить\n")
            time.sleep(2)
    # === СОЗДАНИЕ EXCEL ===
    if not all_products:
        print("\n❌ Нет данных для создания каталога!")
        return
    print(f"\n{'='*80}")
    print(f"📊 СОЗДАНИЕ КАТАЛОГА")
    print(f"{'='*80}\n")
    rows = []
    for idx, product in enumerate(all_products, start=1):
        row = {
            'ID': f"PRODUCT.{idx:03d}",
            'Title': product['title'],
            'SKU': f"SKU.{idx:03d}",
            'Type': 'machine' if 'запчаст' not in product['category'].lower() else 'spare',
            'Brand': '',
            'Category_Path': f"Каталог >>> {product['category']}",
            'Price': product.get('price', ''),
            'Currency': 'RUB' if product.get('price') else '',
            'Compatible_SKUs': '',
            'Short_Description': product.get('short_description',''),
            'Full_Description': product.get('full_description',''),
            'Weight_KG': product.get('weight',''),
            'Power_KW': product.get('power',''),
            'Dimensions_MM': product.get('dimensions',''),
            'Voltage_V': '',
            'Main_Photo': '',
            'Gallery_Photos': '',
            'Status': 'active'
        }
        rows.append(row)
    df = pd.DataFrame(rows)
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
    final_df = pd.concat([header_row_1, header_row_2, df], ignore_index=True)
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
            'Power_KW': product['power'],
