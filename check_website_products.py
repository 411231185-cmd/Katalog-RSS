# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup

def check_catalog():
    print('=' * 80)
    print('CHECKING WEBSITE CATALOG')
    print('=' * 80)
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    base_url = 'https://russtanko-rzn.ru'
    catalog_url = base_url + '/katalogi-zapasnykh-chastey-i-osnastki-dlya-tokarnykh-stankov'
    
    print("\nLoading: " + catalog_url)
    
    response = requests.get(catalog_url, headers=headers, timeout=15)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        products = soup.find_all('a', class_='t-store__card__link')
        
        print("\nFound products: " + str(len(products)))
        print("\nFirst 20 products on website:\n")
        
        for i, product in enumerate(products[:20], 1):
            title_elem = product.find('div', class_='t-store__card__title')
            if title_elem:
                title = title_elem.text.strip()
                print(str(i) + ". " + title)
        
        print("\n" + '=' * 80)
        print("RECOMMENDATION")
        print('=' * 80)
        print("""
We need to:
1. Compare YOUR offer names with website product names
2. Find matching patterns
3. Update search logic

Your offers have codes like: RT502_33_152, 1M63B_60_281
Website probably has simpler names like: "Val", "Shesternya", etc.
        """)
    else:
        print("Error: " + str(response.status_code))

if __name__ == '__main__':
    check_catalog()
