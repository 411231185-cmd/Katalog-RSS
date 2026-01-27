# -*- coding: utf-8 -*-
import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import re


def clean_text(text):
    """Очистка текста от лишних пробелов"""
    if not text:
        return ''
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def extract_short_description(full_text, max_sentences=2):
    """Создаёт короткое описание из первых 2-3 предложений"""
    if not full_text:
        return ''
    sentences = re.split(r'[.!?]\s+', full_text)
    short = '. '.join(sentences[:max_sentences])
    if short and not short.endswith('.'):
        short += '.'
    return short


def search_on_tdrusstankosbyt_priority(product_title):
    """🆕 ПРИОРИТЕТНЫЙ ПОИСК НА ТВОЁМ САЙТЕ tdrusstankosbyt.ru"""
    print("  [🎯 tdrusstankosbyt.ru - ГЛАВНЫЙ] Поиск...")
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    try:
        base_url = 'https://tdrusstankosbyt.ru'
        
        # Пробуем разные разделы
        sections = [
            '/stanki',
            '/komplektuyushchie-i-zapchasti',
            '/shpindelnaya-gruppa',
            '/zapchasti',
            ''
        ]
        
        keywords = [w.lower() for w in product_title.split()[:6] if len(w) > 3]
        
        for section in sections:
            try:
                url = base_url + section
                response = requests.get(url, headers=headers, timeout=15)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    links = soup.find_all('a', href=True)
                    
                    for link in links:
                        href = link.get('href', '')
                        text = link.get_text(strip=True).lower()
                        
                        # Проверяем совпадение ключевых слов
                        matches = sum(1 for kw in keywords if kw in text or kw in href)
                        
                        if matches >= 2:
                            product_url = href if href.startswith('http') else base_url + href
                            
                            # Избегаем дублей и служебных страниц
                            if any(skip in product_url for skip in ['#', 'javascript:', 'tel:', 'mailto:']):
                                continue
                            
                            print(f"    🔍 Проверяю: {link.get_text(strip=True)[:50]}")
                            
                            time.sleep(1)
                            prod_response = requests.get(product_url, headers=headers, timeout=15)
                            
                            if prod_response.status_code == 200:
                                prod_soup = BeautifulSoup(prod_response.text, 'html.parser')
                                
                                # Удаляем мусор
                                for tag in prod_soup(['script', 'style', 'nav', 'footer', 'header', 'iframe']):
                                    tag.decompose()
                                
                                # Ищем контент
                                full_text = ''
                                
                                # Приоритет 1: Основной контент
                                content_areas = prod_soup.find_all(['article', 'main', 'div'], 
                                                                  class_=lambda x: x and any(cls in str(x).lower() for cls in ['content', 'description', 'product', 'text', 'info']))
                                
                                if content_areas:
                                    for area in content_areas:
                                        text = clean_text(area.get_text())
                                        if len(text) > 200:
                                            full_text = text
                                            break
                                
                                # Приоритет 2: Все абзацы
                                if not full_text:
                                    paragraphs = prod_soup.find_all(['p', 'div'])
                                    combined = ' '.join([clean_text(p.get_text()) for p in paragraphs])
                                    if len(combined) > 200:
                                        full_text = combined
                                
                                if len(full_text) > 150:
                                    short_desc = extract_short_description(full_text, 3)
                                    print(f"    ✅ НАЙДЕНО на tdrusstankosbyt.ru!")
                                    return {
                                        'description': short_desc[:400],
                                        'text': full_text[:3000]
                                    }
            
            except Exception as e:
                continue
        
    except Exception as e:
        print(f"    ❌ Ошибка tdrusstankosbyt.ru: {str(e)[:50]}")
    
    return None


def search_on_rosstanko_com(product_title):
    """Поиск на rosstanko.com"""
    print("  [rosstanko.com] Поиск...")
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    try:
        base_url = 'https://rosstanko.com'
        response = requests.get(base_url + '/produkcziya', headers=headers, timeout=15)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            products = soup.find_all('a', href=True)
            
            keywords = [w.lower() for w in product_title.split()[:5] if len(w) > 3]
            
            for product in products:
                href = product.get('href', '')
                text = product.get_text(strip=True).lower()
                
                if any(kw in text or kw in href for kw in keywords):
                    product_url = href if href.startswith('http') else base_url + href
                    
                    prod_response = requests.get(product_url, headers=headers, timeout=15)
                    if prod_response.status_code == 200:
                        prod_soup = BeautifulSoup(prod_response.text, 'html.parser')
                        
                        desc_divs = prod_soup.find_all(['div', 'p'], class_=lambda x: x and ('desc' in x.lower() or 'product' in x.lower()))
                        
                        for div in desc_divs:
                            full_text = clean_text(div.get_text())
                            if len(full_text) > 100:
                                short_desc = extract_short_description(full_text, 3)
                                print(f"    ✅ Найдено на rosstanko.com")
                                return {'description': short_desc[:400], 'text': full_text[:3000]}
                    
                    time.sleep(1)
    except Exception as e:
        print(f"    ❌ Ошибка rosstanko.com: {str(e)[:50]}")
    
    return None


def search_on_tdrusstankosbyt(product_title):
    """Поиск на tdrusstankosbyt.ru (резервный)"""
    print("  [tdrusstankosbyt.ru - резерв] Поиск...")
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    try:
        base_url = 'https://tdrusstankosbyt.ru'
        response = requests.get(base_url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            products = soup.find_all('a', href=True)
            
            keywords = [w.lower() for w in product_title.split()[:5] if len(w) > 3]
            
            for product in products:
                href = product.get('href', '')
                text = product.get_text(strip=True).lower()
                
                if any(kw in text or kw in href for kw in keywords):
                    product_url = href if href.startswith('http') else base_url + href
                    
                    prod_response = requests.get(product_url, headers=headers, timeout=15)
                    if prod_response.status_code == 200:
                        prod_soup = BeautifulSoup(prod_response.text, 'html.parser')
                        
                        for tag in prod_soup(['script', 'style', 'nav', 'footer']):
                            tag.decompose()
                        
                        full_text = clean_text(prod_soup.get_text())
                        if len(full_text) > 100:
                            short_desc = extract_short_description(full_text, 3)
                            print(f"    ✅ Найдено на tdrusstankosbyt.ru")
                            return {'description': short_desc[:400], 'text': full_text[:3000]}
                    
                    time.sleep(1)
    except Exception as e:
        print(f"    ❌ Ошибка tdrusstankosbyt.ru: {str(e)[:50]}")
    
    return None


def search_on_russtanko_rzn(product_title):
    """Поиск на russtanko-rzn.ru"""
    print("  [russtanko-rzn.ru] Поиск...")
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    try:
        base_url = 'https://russtanko-rzn.ru'
        catalog_url = base_url + '/katalogi-zapasnykh-chastey-i-osnastki-dlya-tokarnykh-stankov'
        
        response = requests.get(catalog_url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            products = soup.find_all('a', class_='t-store__card__link')
            
            for product in products:
                title_elem = product.find('div', class_='t-store__card__title')
                if title_elem:
                    card_title = title_elem.text.strip()
                    
                    similarity = 0
                    words_in_search = product_title.lower().split()[:5]
                    
                    for word in words_in_search:
                        if len(word) > 3 and word in card_title.lower():
                            similarity += 1
                    
                    if similarity >= 2:
                        product_url = product.get('href')
                        if product_url:
                            if not product_url.startswith('http'):
                                product_url = base_url + product_url
                            
                            print("    ✅ Найдено: " + card_title[:40])
                            
                            time.sleep(1)
                            prod_response = requests.get(product_url, headers=headers, timeout=15)
                            
                            if prod_response.status_code == 200:
                                prod_soup = BeautifulSoup(prod_response.text, 'html.parser')
                                
                                full_text = ''
                                text_containers = prod_soup.find_all(['p', 'div', 'span'])
                                
                                for container in text_containers:
                                    text = clean_text(container.get_text())
                                    if len(text) > 100 and 'cookie' not in text.lower():
                                        full_text = text
                                        break
                                
                                if full_text:
                                    short_desc = extract_short_description(full_text, max_sentences=3)
                                    return {
                                        'description': short_desc[:400],
                                        'text': full_text[:3000]
                                    }
    
    except Exception as e:
        print("    ❌ Ошибка russtanko-rzn.ru: " + str(e)[:50])
    
    return None


def search_product_on_all_sites(product_title):
    """🆕 Поиск на ВСЕХ 4 сайтах (приоритет - твой сайт!)"""
    
    # 1️⃣ СНАЧАЛА ТВОЙ САЙТ (приоритетная функция)
    result = search_on_tdrusstankosbyt_priority(product_title)
    if result:
        return result
    
    # 2️⃣ Потом russtanko-rzn
    result = search_on_russtanko_rzn(product_title)
    if result:
        return result
    
    # 3️⃣ Резервный поиск на tdrusstankosbyt
    result = search_on_tdrusstankosbyt(product_title)
    if result:
        return result
    
    # 4️⃣ И последний rosstanko.com
    result = search_on_rosstanko_com(product_title)
    if result:
        return result
    
    return None


def fill_descriptions(input_file=r'catalogs\MASTER_WITH_HTML_LINKS copy.csv', 
                      output_file=r'catalogs\MASTER_WITH_HTML_LINKS copy.csv',
                      limit=10):
    
    print('=' * 80)
    print('🚀 ПАРСЕР v2.0 - РАСШИРЕННЫЙ КОНТЕНТ + ТВОЙ САЙТ')
    print('=' * 80)
    print('Сайты (по приоритету):')
    print('1. 🎯 tdrusstankosbyt.ru (ТВОЙ - максимальный приоритет!)')
    print('2. russtanko-rzn.ru')
    print('3. tdrusstankosbyt.ru (резерв)')
    print('4. rosstanko.com')
    print('=' * 80)
    print('📏 Description: до 400 символов (3 предложения)')
    print('📄 Text: до 3000 символов (расширенный)')
    print('🔗 Перелинковка: 100% сохраняется!')
    print('=' * 80)
    
    df = pd.read_csv(input_file, encoding='utf-8-sig')
    print(f"\nОфферов в файле: {len(df)}")
    
    # ✅ ФИЛЬТР: только пустые Description
    empty_desc = df[df['Description'].isna() | (df['Description'] == '')]
    print(f"Пустых Description: {len(empty_desc)}")
    print(f"Обрабатываем первые: {limit}\n")
    
    success = 0
    
    for idx, row in empty_desc.head(limit).iterrows():
        title = row['Title']
        
        print(f"\n[{idx+1}/{len(empty_desc)}] {title}")
        
        # ✅ ПРОВЕРКА: есть ли HTML-ссылки в Text
        existing_text = str(row.get('Text', ''))
        has_html_links = '<a href=' in existing_text
        
        if has_html_links:
            print(f"  🔗 Text с перелинковкой ({existing_text.count('<a href=')} ссылок) — НЕ ТРОГАЕМ!")
        
        # Парсим
        result = search_product_on_all_sites(title)
        
        if result:
            # ✅ Заполняем Description
            df.at[idx, 'Description'] = result['description']
            
            # ✅ Text заполняем ТОЛЬКО если нет перелинковки
            if not has_html_links and (pd.isna(row['Text']) or row['Text'] == ''):
                df.at[idx, 'Text'] = result['text']
                print(f"  ✅ Заполнено: Description ({len(result['description'])} симв) + Text ({len(result['text'])} симв)")
            else:
                print(f"  ✅ Заполнен только Description ({len(result['description'])} симв) — Text сохранён")
            
            success += 1
        else:
            print("  ❌ Не найдено ни на одном сайте")
        
        time.sleep(2)
    
    df.to_csv(output_file, index=False, encoding='utf-8-sig')
    
    print("\n" + '=' * 80)
    print(f"✅ ЗАВЕРШЕНО!")
    print(f"Обработано: {limit} | Успешно: {success} ({success/limit*100:.1f}%)")
    print(f"🔗 Перелинковка: сохранена!")
    print(f"💾 Результат: {output_file}")
    print('=' * 80)


def main():
    print('=' * 80)
    print('🚀 RSS CATALOG PARSER v2.0 - РАСШИРЕННЫЙ')
    print('=' * 80)
    print('\n✨ УЛУЧШЕНИЯ:')
    print('1. Твой сайт tdrusstankosbyt.ru — первый приоритет!')
    print('2. Description до 400 символов (3 предложения)')
    print('3. Text до 3000 символов (было 2000)')
    print('4. Перелинковка 100% сохраняется!\n')
    print('Сайты:')
    print('1. 🎯 tdrusstankosbyt.ru (ПРИОРИТЕТ)')
    print('2. russtanko-rzn.ru')
    print('3. tdrusstankosbyt.ru (резерв)')
    print('4. rosstanko.com\n')
    
    choice = input('Начать парсинг? (y/n): ')
    
    if choice.lower() == 'y':
        limit = input('Сколько офферов обработать? (default: 10): ')
        limit = int(limit) if limit.isdigit() else 10
        fill_descriptions(limit=limit)


if __name__ == '__main__':
    main()
