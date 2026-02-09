#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
master_catalog_creator.py
Создаёт финальный каталог Олега из ATALONNY-PERELIKOVKA.csv с использованием префиксных словарей и автозаполнением описаний с сайтов.
"""
import pandas as pd
import re
from pathlib import Path
from bs4 import BeautifulSoup
import requests

def load_prefix_dicts():
    # PREFIKSY-VSE..txt
    prefix_map = {}
    with open('slovari/PREFIKSY-VSE..txt', encoding='utf-8') as f:
        for line in f:
            if '-' in line:
                k, v = line.split('-', 1)
                prefix_map[k.strip()] = v.strip()
    # SLOVAR-PREFIKSOV-offery.txt
    offer_prefixes = {}
    with open('slovari/SLOVAR-PREFIKSOV-offery.txt', encoding='utf-8') as f:
        for line in f:
            if ';' in line:
                k, v = line.split(';', 1)
                offer_prefixes[k.strip()] = v.strip()
    return prefix_map, offer_prefixes

def clean_text(text):
    if not text:
        return ''
    text = re.sub(r'<.*?>', '', str(text))
    text = re.sub(r'руссстанко\s*сбыт|rossstanko|tdrusstankosbyt', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def extract_compatible_skus(text):
    # Извлекает модели станков (например, 16К20, 1М63)
    if not text:
        return ''
    matches = re.findall(r'(\d+[A-ZА-Я]+\d+)', text, re.I)
    return ';'.join(set(matches))

def fetch_description_from_sites(title):
        # Perplexity API integration
        def fetch_from_perplexity(query):
            import requests
            api_key = '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'
            url = 'https://api.perplexity.ai/v1/completions'
            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            }
            payload = {
                'model': 'pplx-7b-chat',
                'messages': [
                    {'role': 'user', 'content': f'Дай подробное описание и технические характеристики для: {query}'}
                ],
                'max_tokens': 1024
            }
            try:
                resp = requests.post(url, headers=headers, json=payload, timeout=20)
                if resp.status_code == 200:
                    result = resp.json()
                    content = result['choices'][0]['message']['content']
                    return content[:200], content
            except Exception:
                pass
            return '', ''
    from urllib.parse import quote
    headers = {'User-Agent': 'Mozilla/5.0'}
    sites = [
        {'name': 'github-repo', 'repo': '411231185-cmd/Katalog-RSS', 'query': title},
        {'name': 'td-rss.ru', 'url': f"https://td-rss.ru/search?q={quote(title)}", 'selector': '.product-description'},
        {'name': 'rosstanko.com', 'url': f"https://rosstanko.com/search?q={quote(title)}", 'selector': '.product-description'},
        {'name': 'russtanko-rzn.ru', 'url': f"https://russtanko-rzn.ru/search?q={quote(title)}", 'selector': '.product-text'},
        {'name': 'stankoartel.com', 'url': f"https://stankoartel.com/search?q={quote(title)}", 'selector': '.t-descr'}
    ]
    for site in sites:
        try:
            print(f"  🔍 Поиск на {site['name']}...")
            if site['name'] == 'github-repo':
                # Используем GitHub API для поиска по репозиторию
                import requests
                api_url = f"https://api.github.com/search/code?q={site['query']}+repo:{site['repo']}"
                resp = requests.get(api_url, headers={'Accept': 'application/vnd.github.v3+json'}, timeout=10)
                if resp.status_code == 200:
                    items = resp.json().get('items', [])
                    for item in items:
                        file_url = item.get('html_url', '')
                        if file_url:
                            file_resp = requests.get(file_url)
                            if file_resp.status_code == 200:
                                text = file_resp.text
                                print(f"  ✅ Найдено в GitHub-репозитории")
                                return text[:200], text
            elif site['name'] == 'perplexity':
                short, full = fetch_from_perplexity(title)
                if full:
                    print(f"  ✅ Найдено через Perplexity")
                    return short, full
            else:
                response = requests.get(site['url'], headers=headers, timeout=10)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    found_text = soup.select_one(site['selector'])
                    if found_text:
                        full_text = found_text.get_text(strip=True)
                        print(f"  ✅ Найдено на {site['name']}" )
                        return full_text[:200], full_text
        except Exception:
            continue
    # Если ничего не найдено, пробуем Perplexity
    short, full = fetch_from_perplexity(title)
    if full:
        print(f"  ✅ Найдено через Perplexity (fallback)")
        return short, full
    return '', ''
    return '', ''

def main():
    prefix_map, offer_prefixes = load_prefix_dicts()
    df = pd.read_csv('ATALONNY-PERELIKOVKA.csv', encoding='utf-8-sig')
    data_rows = []
    for idx, row in df.iterrows():
        title = str(row.get('Title', ''))
        desc = str(row.get('Description', ''))
        text = str(row.get('Text', ''))
        sku = str(row.get('SKU', ''))
        category = str(row.get('Category', ''))
        # Определяем префикс и категорию
        prefix = ''
        for pfx in offer_prefixes:
            if title.startswith(pfx):
                prefix = pfx
                break
        if not prefix:
            for pfx in prefix_map:
                if title.startswith(pfx):
                    prefix = pfx
                    break
        sku_final = f"{prefix}.{sku}" if prefix else sku
        category_final = prefix_map.get(prefix, category)
        # Описания
        short_desc = clean_text(desc)[:200]
        full_desc = clean_text(text)
        if not short_desc or not full_desc:
            fetched_short, fetched_full = fetch_description_from_sites(title)
            if not short_desc:
                short_desc = clean_text(fetched_short)[:200]
            if not full_desc:
                full_desc = clean_text(fetched_full)
        compatible = extract_compatible_skus(full_desc)
        status = 'published' if row.get('Photo') and row.get('Price') else 'draft'
        # Новые поля для specs и связанных товаров
        weight_kg = row.get('Weight', '')
        power_kw = row.get('Power', '')
        voltage_v = row.get('Voltage', '')
        dimensions_mm = row.get('Dimensions', '')
        related_skus = row.get('Related_SKUs', '')
        data_rows.append({
            'ID': '',
            'Title': title,
            'SKU': sku_final,
            'Type': 'machine' if 'Станки' in category_final else 'spare',
            'Brand': '',
            'Category_Path': category_final,
            'Price': int(float(row.get('Price', 0))) if str(row.get('Price', '')).replace('.', '', 1).isdigit() else '',
            'Currency': 'RUB',
            'Compatible_SKUs': compatible,
            'Short_Description': short_desc,
            'Full_Description': full_desc,
            'Weight_KG': weight_kg,
            'Power_KW': power_kw,
            'Dimensions_MM': dimensions_mm,
            'Voltage_V': voltage_v,
            'Main_Photo': row.get('Photo', ''),
            'Gallery_Photos': '',
            'Related_SKUs': related_skus,
            'Status': status
        })
    # Заголовки
    row_1 = {'ID': 'ID', 'Title': 'Title', 'SKU': 'SKU', 'Type': 'Type', 'Brand': 'Brand',
        'Category_Path': 'Category_Path', 'Price': 'Price', 'Currency': 'Currency',
        'Compatible_SKUs': 'Compatible_SKUs', 'Short_Description': 'Short_Description',
        'Full_Description': 'Full_Description', 'Weight_KG': 'Weight_KG', 'Power_KW': 'Power_KW',
        'Dimensions_MM': 'Dimensions_MM', 'Voltage_V': 'Voltage_V', 'Main_Photo': 'Main_Photo',
        'Gallery_Photos': 'Gallery_Photos', 'Status': 'Status'}
    row_2 = {'ID': 'ИДЕНТИФИКАТОР', 'Title': 'НАЗВАНИЕ ТОВАРА', 'SKU': 'АРТИКУЛ', 'Type': 'ТИП ОБЪЕКТА',
        'Brand': 'БРЕНД', 'Category_Path': 'ПУТЬ КАТЕГОРИИ', 'Price': 'ЦЕНА', 'Currency': 'ВАЛЮТА',
        'Compatible_SKUs': 'СОВМЕСТИМОСТЬ', 'Short_Description': 'КРАТКОЕ ОПИСАНИЕ',
        'Full_Description': 'ПОЛНОЕ ОПИСАНИЕ', 'Weight_KG': 'ВЕС (КГ)', 'Power_KW': 'МОЩНОСТЬ (КВТ)',
        'Dimensions_MM': 'ГАБАРИТЫ (ММ)', 'Voltage_V': 'НАПРЯЖЕНИЕ (В)', 'Main_Photo': 'ГЛАВНОЕ ФОТО',
        'Gallery_Photos': 'ГАЛЕРЕЯ ФОТО', 'Status': 'СТАТУС'}
    row_3 = {'ID': '(системное)', 'Title': 'Текст', 'SKU': 'Уникальный код', 'Type': 'machine / spare',
        'Brand': 'Текст', 'Category_Path': 'Разделитель >>>', 'Price': 'Число', 'Currency': 'RUB',
        'Compatible_SKUs': 'Артикулы через ;', 'Short_Description': '1-2 предложения',
        'Full_Description': 'Текст без тегов', 'Weight_KG': 'Число', 'Power_KW': 'Число',
        'Dimensions_MM': 'ДхШхВ', 'Voltage_V': 'Число', 'Main_Photo': '{SKU}_main.jpg',
        'Gallery_Photos': 'через ;', 'Status': 'published / draft'}
    all_rows = [row_1, row_2, row_3] + data_rows
    df_out = pd.DataFrame(all_rows)
    df_out.to_excel('CATALOG_OLEG_FINAL_100.xlsx', index=False, header=False, engine='openpyxl')
    print('✅ Каталог сохранён: CATALOG_OLEG_FINAL_100.xlsx')

if __name__ == "__main__":
    main()
