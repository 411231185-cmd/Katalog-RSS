# -*- coding: utf-8 -*-
"""
Скрипт для сбора описаний станков с сайта tdrusstankosbyt.ru
и создания структурированных файлов для GitHub репозитория
"""

import requests
from bs4 import BeautifulSoup
import json
import csv
from pathlib import Path
import time
import re

# КОНФИГУРАЦИЯ
BASE_DIR = Path(__file__).parent
DESCRIPTIONS_DIR = BASE_DIR / "descriptions"
OUTPUT_JSON = BASE_DIR / "descriptions.json"
OUTPUT_CSV = BASE_DIR / "descriptions.csv"

# Список станков для обработки
STANKI = [
    {"sku": "STANOK.RT5001", "name": "Станок лентобандажировочный РТ5001", "search": "РТ5001"},
    {"sku": "1M63", "name": "Токарно-винторезный станок 1М63", "search": "1М63"},
    {"sku": "16K40", "name": "Токарный станок 16К40", "search": "16К40"},
    {"sku": "1N65", "name": "Токарно-винторезный станок 1Н65", "search": "1Н65"},
    {"sku": "1N98", "name": "Токарно-винторезный станок 1Н98", "search": "1Н98"},
    {"sku": "16K30", "name": "Токарный станок 16К30", "search": "16К30"},
    {"sku": "16M30", "name": "Токарный станок 16М30", "search": "16М30"},
    {"sku": "1N62", "name": "Токарно-винторезный станок 1Н62", "search": "1Н62"},
    {"sku": "1K62", "name": "Токарный станок 1К62", "search": "1К62"},
    {"sku": "GS526", "name": "Фрезерный станок GS-526", "search": "GS-526"},
    {"sku": "UBB112", "name": "Фрезерный станок UBB-112", "search": "UBB-112"},
]

BASE_URL = "tdrusstankosbyt.ru"

def search_stanok_page(search_term):
    """Поиск страницы станка на сайте"""
    # Попробуем несколько вариантов URL
    possible_urls = [
        f"{BASE_URL}/catalog/{search_term.lower().replace('-', '').replace('М', 'm').replace('Н', 'n').replace('К', 'k')}/",
        f"{BASE_URL}/{search_term.lower()}/",
        f"{BASE_URL}/stanki/{search_term.lower()}/",
    ]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    for url in possible_urls:
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                return url, response.text
        except Exception as e:
            continue
    
    return None, None

def extract_description_info(html_content, url):
    """Извлечение информации о станке из HTML"""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Извлекаем назначение (первый абзац или описание)
    purpose = ""
    purpose_selectors = [
        'div.description p:first-of-type',
        'div.content p:first-of-type',
        '.product-description p',
        'article p:first-of-type'
    ]
    
    for selector in purpose_selectors:
        element = soup.select_one(selector)
        if element and element.get_text(strip=True):
            purpose = element.get_text(strip=True)
            break
    
    # Извлекаем характеристики
    characteristics = []
    
    # Ищем таблицы характеристик
    tables = soup.find_all('table')
    for table in tables:
        rows = table.find_all('tr')
        for row in rows:
            cells = row.find_all(['td', 'th'])
            if len(cells) >= 2:
                key = cells[0].get_text(strip=True)
                value = cells[1].get_text(strip=True)
                if key and value:
                    characteristics.append(f"{key}: {value}")
    
    # Ищем списки характеристик
    if not characteristics:
        lists = soup.find_all(['ul', 'ol'])
        for ul in lists:
            items = ul.find_all('li')
            for item in items:
                text = item.get_text(strip=True)
                if text and len(text) > 5:  # Фильтр коротких элементов
                    characteristics.append(text)
    
    # Извлекаем комплектацию
    equipment = []
    # Ищем раздел с комплектацией
    equipment_keywords = ['комплектац', 'состав', 'включа']
    for keyword in equipment_keywords:
        sections = soup.find_all(text=re.compile(keyword, re.IGNORECASE))
        for section in sections:
            parent = section.find_parent(['div', 'section', 'article'])
            if parent:
                items = parent.find_all('li')
                for item in items:
                    text = item.get_text(strip=True)
                    if text:
                        equipment.append(text)
                if equipment:
                    break
        if equipment:
            break
    
    return {
        "purpose": purpose if purpose else "Информация уточняется",
        "characteristics": characteristics[:10] if characteristics else ["Характеристики уточняются"],
        "equipment": equipment[:10] if equipment else ["Стандартная комплектация"],
        "source_url": url
    }

def create_markdown_file(stanok_data, filepath):
    """Создание Markdown файла для станка"""
    content = f"""# {stanok_data['sku']} - {stanok_data['name']}

## Назначение
{stanok_data['purpose']}

## Основные характеристики
"""
    
    for char in stanok_data['characteristics']:
        content += f"- {char}\n"
    
    content += "\n## Комплектация\n"
    for eq in stanok_data['equipment']:
        content += f"- {eq}\n"
    
    content += f"\n**Источник:** {stanok_data['source_url']}\n"
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

def scrape_all_stanki():
    """Основная функция сбора данных"""
    print("=" * 80)
    print("СБОР ОПИСАНИЙ СТАНКОВ С ROSSTANKO.COM")
    print("=" * 80)
    
    # Создаем директорию для описаний
    DESCRIPTIONS_DIR.mkdir(exist_ok=True)
    
    all_data = []
    
    for i, stanok in enumerate(STANKI, 1):
        print(f"\n[{i}/{len(STANKI)}] Обработка: {stanok['name']}")
        
        # Поиск страницы
        url, html = search_stanok_page(stanok['search'])
        
        if not url:
            print(f"   ⚠️  Страница не найдена, используем заглушку")
            stanok_data = {
                "sku": stanok['sku'],
                "name": stanok['name'],
                "purpose": f"Станок {stanok['name']} - информация уточняется на сайте tdrusstankosbyt.ru",
                "characteristics": ["Характеристики уточняются"],
                "equipment": ["Стандартная комплектация"],
                "source_url": f"{BASE_URL}/"
            }
        else:
            print(f"   ✅ Найдено: {url}")
            # Извлечение данных
            info = extract_description_info(html, url)
            stanok_data = {
                "sku": stanok['sku'],
                "name": stanok['name'],
                **info
            }
            print(f"   📝 Извлечено: {len(stanok_data['characteristics'])} характеристик")
        
        all_data.append(stanok_data)
        
        # Создание Markdown файла
        md_file = DESCRIPTIONS_DIR / f"{stanok['sku']}.md"
        create_markdown_file(stanok_data, md_file)
        print(f"   💾 Сохранено: {md_file.name}")
        
        # Небольшая задержка между запросами
        time.sleep(1)
    
    # Сохранение JSON
    print(f"\n📁 Сохранение JSON: {OUTPUT_JSON.name}")
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump({"stanks": all_data}, f, ensure_ascii=False, indent=2)
    
    # Сохранение CSV
    print(f"📁 Сохранение CSV: {OUTPUT_CSV.name}")
    with open(OUTPUT_CSV, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['SKU', 'Name', 'Purpose', 'Characteristics', 'Equipment', 'SourceURL'])
        
        for data in all_data:
            writer.writerow([
                data['sku'],
                data['name'],
                data['purpose'],
                '; '.join(data['characteristics']),
                '; '.join(data['equipment']),
                data['source_url']
            ])
    
    print("\n" + "=" * 80)
    print("ГОТОВО!")
    print("=" * 80)
    print(f"\nСоздано файлов:")
    print(f"  • {len(all_data)} Markdown файлов в descriptions/")
    print(f"  • descriptions.json")
    print(f"  • descriptions.csv")
    print("=" * 80)

if __name__ == "__main__":
    scrape_all_stanki()
