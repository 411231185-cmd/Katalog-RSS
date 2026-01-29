# -*- coding: utf-8 -*-
import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
from urllib.parse import quote

def search_on_rosstanko_com(product_title):
    print(f"  tdrusstankosbyt.ru: {product_title[:50]}...")
    try:
        search_url = f"tdrusstankosbyt.rusearch?q={quote(product_title)}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(search_url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            desc = soup.find('div', class_='product-description')
            txt = soup.find('div', class_='product-text')
            return {'source': 'tdrusstankosbyt.ru', 'description': desc.get_text(strip=True) if desc else '', 'text': txt.get_text(strip=True) if txt else ''}
    except: pass
    return None

def search_on_russtanko_rzn(product_title):
    print(f"  tdrusstankosbyt.ru: {product_title[:50]}...")
    try:
        search_url = f"https://tdrusstankosbyt.ru/search?q={quote(product_title)}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(search_url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            desc = soup.find('div', class_='product-description')
            txt = soup.find('div', class_='product-text')
            return {'source': 'tdrusstankosbyt.ru', 'description': desc.get_text(strip=True) if desc else '', 'text': txt.get_text(strip=True) if txt else ''}
    except: pass
    return None

def search_on_stankoartel(product_title):
    print(f"  stankoartel.com: {product_title[:50]}...")
    try:
        search_url = f"https://stankoartel.com/search?q={quote(product_title)}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(search_url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            desc = soup.find('div', class_='t-text') or soup.find('div', class_='t-descr')
            txt = soup.find('div', class_='t-col')
            return {'source': 'stankoartel.com', 'description': desc.get_text(strip=True) if desc else '', 'text': txt.get_text(strip=True) if txt else ''}
    except: pass
    return None

print("="*80)
print("ПАРСИНГ 3 САЙТОВ")
print("="*80)

df = pd.read_csv('catalogs/MASTER_WITH_HTML_LINKS copy.csv', encoding='utf-8-sig')
print(f"Загружено: {len(df)} офферов\n")
success = 0

for idx, row in df.iterrows():
    title = row['Title']
    print(f"[{idx+1}/{len(df)}] {title}")
    
    curr_text = str(row.get('Text', ''))
    curr_desc = str(row.get('Description', ''))
    
    if len(curr_text) > 200 and len(curr_desc) > 50:
        print("  ✓ Пропуск")
        continue
    
    for func in [search_on_rosstanko_com, search_on_russtanko_rzn, search_on_stankoartel]:
        result = func(title)
        if result and (result['description'] or result['text']):
            if result['text']: df.at[idx, 'Text'] = result['text']
            if result['description']: df.at[idx, 'Description'] = result['description']
            success += 1
            print(f"  ✓ {result['source']}")
            break
        time.sleep(0.5)
    
    if (idx+1) % 50 == 0:
        df.to_csv('catalogs/MASTER_WITH_HTML_LINKS copy.csv', index=False, encoding='utf-8-sig')
        print(f"\n💾 Сохранение...\n")

df.to_csv('catalogs/MASTER_WITH_HTML_LINKS copy.csv', index=False, encoding='utf-8-sig')
print(f"\n✅ Готово! Найдено: {success}/{len(df)}")
