# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup

def analyze_page():
    print('=' * 80)
    print('DEEP WEBSITE ANALYSIS')
    print('=' * 80)
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    url = 'https://tdrusstankosbyt.ru/katalogi-zapasnykh-chastey-i-osnastki-dlya-tokarnykh-stankov'
    
    print("\nLoading: " + url)
    
    response = requests.get(url, headers=headers, timeout=15)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Проверяем все возможные варианты
        print("\n--- SEARCHING FOR PRODUCTS ---\n")
        
        # Вариант 1: Tilda Store
        tilda_cards = soup.find_all('div', class_='t-store__card')
        print("1. t-store__card: " + str(len(tilda_cards)))
        
        # Вариант 2: Ссылки с классом store
        store_links = soup.find_all('a', class_=lambda x: x and 'store' in x.lower() if x else False)
        print("2. Links with 'store': " + str(len(store_links)))
        
        # Вариант 3: Все ссылки на странице
        all_links = soup.find_all('a', href=True)
        print("3. All links: " + str(len(all_links)))
        
        # Фильтруем ссылки на товары
        product_links = []
        for link in all_links:
            href = link.get('href', '')
            text = link.text.strip()
            
            # Ищем ссылки с ключевыми словами
            keywords = ['val', 'shest', 'muf', 'vint', 'gayk', 'patron', 'zapas', 'page']
            
            if any(kw in href.lower() for kw in keywords) and text and len(text) > 10:
                product_links.append({'url': href, 'text': text[:60]})
        
        print("\n4. Filtered product links: " + str(len(product_links)))
        
        if product_links:
            print("\nFirst 15 product links:\n")
            for i, item in enumerate(product_links[:15], 1):
                print(str(i) + ". " + item['text'])
                print("   URL: " + item['url'])
                print()
        
        # Проверяем наличие Tilda
        tilda_scripts = soup.find_all('script', src=lambda x: x and 'tilda' in x.lower() if x else False)
        print("\nTilda scripts found: " + str(len(tilda_scripts)))
        
        if len(tilda_scripts) > 0:
            print("\nThis is a Tilda website!")
            print("Products may be loaded dynamically via JavaScript")
            print("\nSOLUTION: We need to use direct URLs from your catalog")
    
    else:
        print("Error: " + str(response.status_code))

if __name__ == '__main__':
    analyze_page()
