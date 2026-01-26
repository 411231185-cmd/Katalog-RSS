# -*- coding: utf-8 -*-
import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import re

def clean_text(text):
    if not text:
        return ''
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def extract_short_description(full_text, max_sentences=2):
    if not full_text:
        return ''
    sentences = re.split(r'[.!?]\s+', full_text)
    short = '. '.join(sentences[:max_sentences])
    if short and not short.endswith('.'):
        short += '.'
    return short

def search_product_on_russtanko_rzn(product_title):
    print("  Searching: " + product_title[:50] + "...")
    
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
                            
                            print("    Found: " + card_title[:40])
                            
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
                                    short_desc = extract_short_description(full_text, max_sentences=2)
                                    return {
                                        'description': short_desc[:300],
                                        'text': full_text[:2000]
                                    }
    
    except Exception as e:
        print("    Error: " + str(e))
    
    return None

def fill_descriptions(input_file='OFFERS_NEED_TEXT_DESCRIPTION.csv', 
                      output_file='OFFERS_FILLED.csv',
                      limit=10):
    
    print('=' * 80)
    print('PARSING DESCRIPTIONS')
    print('=' * 80)
    
    df = pd.read_csv(input_file, encoding='utf-8-sig')
    print("\nOffers: " + str(len(df)))
    print("Processing: " + str(limit) + "\n")
    
    success = 0
    
    for idx, row in df.head(limit).iterrows():
        title = row['Title']
        
        print("[" + str(idx+1) + "/" + str(limit) + "] " + title)
        
        has_desc = not (pd.isna(row['Description']) or row['Description'] == '')
        has_text = not (pd.isna(row['Text']) or row['Text'] == '')
        
        if has_desc and has_text:
            print("  Already filled")
            continue
        
        result = search_product_on_russtanko_rzn(title)
        
        if result:
            if not has_desc:
                df.at[idx, 'Description'] = result['description']
            if not has_text:
                df.at[idx, 'Text'] = result['text']
            
            success += 1
            print("  SUCCESS!")
        else:
            print("  Not found")
        
        time.sleep(2)
    
    df.to_csv(output_file, index=False, encoding='utf-8-sig')
    
    print("\n" + '=' * 80)
    print("Processed: " + str(limit) + " | Filled: " + str(success))
    print("File: " + output_file)
    print('=' * 80)

def main():
    print('=' * 80)
    print('RSS CATALOG PARSER')
    print('=' * 80)
    print('\nFills Description and Text from russtanko-rzn.ru\n')
    
    choice = input('Start? (y/n): ')
    
    if choice.lower() == 'y':
        fill_descriptions(limit=10)

if __name__ == '__main__':
    main()
