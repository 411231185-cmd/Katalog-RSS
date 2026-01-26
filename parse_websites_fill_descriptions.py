import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
from urllib.parse import quote

def search_on_rosstanko_com(product_title):
    """Поиск товара на rosstanko.com по названию"""
    print(f"  Ищем на rosstanko.com: {product_title[:50]}...")
    
    try:
        # URL поиска на rosstanko.com
        search_url = f"https://rosstanko.com/search?q={quote(product_title)}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(search_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Ищем описание товара (нужно уточнить селекторы)
            description = soup.find('div', class_='product-description')
            text = soup.find('div', class_='product-text')
            
            result = {
                'source': 'rosstanko.com',
                'description': description.get_text(strip=True) if description else '',
                'text': text.get_text(strip=True) if text else ''
            }
            
            return result
        
    except Exception as e:
        print(f"    ❌ Ошибка: {e}")
    
    return None

def search_on_russtanko_rzn(product_title):
    """Поиск товара на russtanko-rzn.ru по названию"""
    print(f"  Ищем на russtanko-rzn.ru: {product_title[:50]}...")
    
    try:
        # URL поиска на russtanko-rzn.ru
        search_url = f"https://russtanko-rzn.ru/search?q={quote(product_title)}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(search_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Ищем описание товара
            description = soup.find('div', class_='product-description')
            text = soup.find('div', class_='product-text')
            
            result = {
                'source': 'russtanko-rzn.ru',
                'description': description.get_text(strip=True) if description else '',
                'text': text.get_text(strip=True) if text else ''
            }
            
            return result
        
    except Exception as e:
        print(f"    ❌ Ошибка: {e}")
    
    return None

def fill_descriptions_from_websites(input_file='OFFERS_NEED_TEXT_DESCRIPTION.csv', 
                                     output_file='OFFERS_WITH_PARSED_DESCRIPTIONS.csv'):
    """Заполнение TEXT и Description для офферов с сайтов"""
    
    print("=" * 80)
    print("ПАРСИНГ ОПИСАНИЙ С САЙТОВ")
    print("=" * 80)
    
    # Читаем файл с офферами без описаний
    df = pd.read_csv(input_file, encoding='utf-8-sig')
    print(f"\nЗагружено {len(df)} офферов для обработки")
    
    # Добавляем колонки для результатов
    df['Parsed_Description'] = ''
    df['Parsed_Text'] = ''
    df['Source'] = ''
    
    success_count = 0
    
    for idx, row in df.iterrows():
        title = row['Title']
        
        print(f"\n[{idx+1}/{len(df)}] Обработка: {title}")
        
        # Проверяем, нужно ли заполнять
        needs_desc = pd.isna(row['Description']) or row['Description'] == ''
        needs_text = pd.isna(row['Text']) or row['Text'] == ''
        
        if not needs_desc and not needs_text:
            print("  ✓ Уже заполнено, пропускаем")
            continue
        
        # Ищем на первом сайте
        result1 = search_on_rosstanko_com(title)
        
        if result1 and (result1['description'] or result1['text']):
            df.at[idx, 'Parsed_Description'] = result1['description']
            df.at[idx, 'Parsed_Text'] = result1['text']
            df.at[idx, 'Source'] = result1['source']
            success_count += 1
            print(f"  ✓ Найдено на {result1['source']}")
            time.sleep(1)  # Пауза между запросами
            continue
        
        # Если не нашли, ищем на втором сайте
        result2 = search_on_russtanko_rzn(title)
        
        if result2 and (result2['description'] or result2['text']):
            df.at[idx, 'Parsed_Description'] = result2['description']
            df.at[idx, 'Parsed_Text'] = result2['text']
            df.at[idx, 'Source'] = result2['source']
            success_count += 1
            print(f"  ✓ Найдено на {result2['source']}")
        else:
            print("  ⚠️  Не найдено ни на одном сайте")
        
        time.sleep(1)  # Пауза между запросами
    
    # Сохраняем результаты
    df.to_csv(output_file, index=False, encoding='utf-8-sig')
    
    print("\n" + "=" * 80)
    print("РЕЗУЛЬТАТЫ ПАРСИНГА")
    print("=" * 80)
    print(f"Всего обработано: {len(df)}")
    print(f"Найдено описаний: {success_count}")
    print(f"Не найдено: {len(df) - success_count}")
    print(f"\nРезультаты сохранены в: {output_file}")

def main():
    print("=" * 80)
    print("ЗАПОЛНЕНИЕ ОПИСАНИЙ С САЙТОВ")
    print("=" * 80)
    print("\nСайты для парсинга:")
    print("  1. rosstanko.com")
    print("  2. russtanko-rzn.ru")
    print("\n⚠️  ВНИМАНИЕ: Скрипт требует уточнения CSS-селекторов!")
    print("Сначала проверьте структуру сайтов вручную.\n")
    
    choice = input("Продолжить парсинг? (y/n): ")
    
    if choice.lower() == 'y':
        fill_descriptions_from_websites()
    else:
        print("\nПарсинг отменён.")
        print("\nДля продолжения:")
        print("1. Откройте rosstanko.com и russtanko-rzn.ru")
        print("2. Найдите любой товар")
        print("3. Изучите HTML-структуру описания")
        print("4. Обновите CSS-селекторы в функциях search_on_*")

if __name__ == "__main__":
    main()
