# -*- coding: utf-8 -*-
"""
Скрипт для обновления JSON и CSV из Markdown файлов
Используйте этот скрипт после ручного редактирования Markdown файлов
"""

import json
import csv
import re
from pathlib import Path

BASE_DIR = Path(__file__).parent
DESCRIPTIONS_DIR = BASE_DIR / "descriptions"
OUTPUT_JSON = BASE_DIR / "descriptions.json"
OUTPUT_CSV = BASE_DIR / "descriptions.csv"

def parse_markdown_file(filepath):
    """Парсинг Markdown файла в структуру данных"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Извлечение SKU и названия из заголовка
    header_match = re.search(r'^# (\S+) - (.+)$', content, re.MULTILINE)
    if not header_match:
        return None
    
    sku = header_match.group(1)
    name = header_match.group(2)
    
    # Извлечение назначения
    purpose_match = re.search(r'## Назначение\n(.+?)(?=\n##)', content, re.DOTALL)
    purpose = purpose_match.group(1).strip() if purpose_match else ""
    
    # Извлечение характеристик
    char_match = re.search(r'## Основные характеристики\n(.+?)(?=\n##)', content, re.DOTALL)
    characteristics = []
    if char_match:
        char_text = char_match.group(1)
        characteristics = [line.strip('- ').strip() for line in char_text.split('\n') if line.strip().startswith('-')]
    
    # Извлечение комплектации
    equip_match = re.search(r'## Комплектация\n(.+?)(?=\n\*\*Источник)', content, re.DOTALL)
    equipment = []
    if equip_match:
        equip_text = equip_match.group(1)
        equipment = [line.strip('- ').strip() for line in equip_text.split('\n') if line.strip().startswith('-')]
    
    # Извлечение источника
    source_match = re.search(r'\*\*Источник:\*\* (.+)$', content, re.MULTILINE)
    source_url = source_match.group(1).strip() if source_match else "https://rosstanko.com/"
    
    return {
        "sku": sku,
        "name": name,
        "purpose": purpose,
        "characteristics": characteristics,
        "equipment": equipment,
        "source_url": source_url
    }

def update_from_markdown():
    """Обновление JSON и CSV из Markdown файлов"""
    print("=" * 80)
    print("ОБНОВЛЕНИЕ ДАННЫХ ИЗ MARKDOWN ФАЙЛОВ")
    print("=" * 80)
    
    all_data = []
    
    # Читаем все Markdown файлы
    md_files = sorted(DESCRIPTIONS_DIR.glob("*.md"))
    md_files = [f for f in md_files if f.name != "README.md"]
    
    print(f"\nНайдено файлов: {len(md_files)}")
    
    for md_file in md_files:
        print(f"  Обработка: {md_file.name}")
        data = parse_markdown_file(md_file)
        if data:
            all_data.append(data)
            print(f"    ✅ {data['sku']} - {len(data['characteristics'])} характеристик")
        else:
            print(f"    ❌ Ошибка парсинга")
    
    # Сохранение JSON
    print(f"\n💾 Сохранение: {OUTPUT_JSON.name}")
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump({"stanks": all_data}, f, ensure_ascii=False, indent=2)
    
    # Сохранение CSV
    print(f"💾 Сохранение: {OUTPUT_CSV.name}")
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
    print(f"✅ ГОТОВО! Обновлено {len(all_data)} записей")
    print("=" * 80)

if __name__ == "__main__":
    update_from_markdown()
