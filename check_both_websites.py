# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup

def check_rosstanko_com():
    print('=' * 80)
    print('CHECKING: tdrusstankosbyt.ru')
    print('=' * 80)
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    # Проверяем главную и каталог
    urls = [
        'tdrusstankosbyt.ru',
        'tdrusstankosbyt.ruprodukcziya'
    ]
    
    for url in urls:
        print("\nChecking: " + url)
        try:
            response = requests.get(url, headers=headers, timeout=15)
            print("Status: " + str(response.status_code))
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Ищем ссылки на товары
                all_links = soup.find_all('a', href=True)
                
                product_links = []
                keywords = ['val', 'shest', 'muf', 'vint', 'gayk', 'koleso', 'patron', 'zapas']
                
                for link in all_links:
                    href = link.get('href', '').lower()
                    text = link.text.strip()
                    
                    if any(kw in href or kw in text.lower() for kw in keywords):
                        if text and len(text) > 15:
                            product_links.append({
                                'url': link.get('href'),
                                'text': text[:70]
                            })
                
                print("Found product links: " + str(len(product_links)))
                
                if product_links:
                    print("\nFirst 10 products:")
                    for i, item in enumerate(product_links[:10], 1):
                        print("\n" + str(i) + ". " + item['text'])
                        print("   " + item['url'])
        
        except Exception as e:
            print("Error: " + str(e))

def check_russtanko_rzn():
    print('\n' + '=' * 80)
    print('CHECKING: tdrusstankosbyt.ru')
    print('=' * 80)
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    url = 'https://tdrusstankosbyt.ru/katalogi-zapasnykh-chastey-i-osnastki-dlya-tokarnykh-stankov'
    
    print("\nChecking: " + url)
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        print("Status: " + str(response.status_code))
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Все ссылки
            all_links = soup.find_all('a', href=True)
            
            product_links = []
            keywords = ['page', 'val', 'shest', 'muf', 'vint', 'gayk']
            
            for link in all_links:
                href = link.get('href', '').lower()
                text = link.text.strip()
                
                if '/page/' in href or any(kw in text.lower() for kw in keywords):
                    if text and len(text) > 15:
                        product_links.append({
                            'url': link.get('href'),
                            'text': text[:70]
                        })
            
            print("Found product links: " + str(len(product_links)))
            
            if product_links:
                print("\nFirst 10 products:")
                for i, item in enumerate(product_links[:10], 1):
                    print("\n" + str(i) + ". " + item['text'])
                    print("   " + item['url'])
    
    except Exception as e:
        print("Error: " + str(e))

def main():
    print('=' * 80)
    print('CHECKING BOTH WEBSITES FOR PRODUCTS')
    print('=' * 80)
    
    check_rosstanko_com()
    check_russtanko_rzn()
    
    print('\n' + '=' * 80)
    print('NEXT STEP')
    print('=' * 80)
    print("""
After checking both sites, we will:
1. Choose the site with better product structure
2. Update parser to search on both sites
3. Use the one that has more matches
    """)

if __name__ == '__main__':
    main()
