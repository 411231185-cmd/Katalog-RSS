# -*- coding: utf-8 -*-
import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import re

print('=' * 100)
print('📝 ОБОГАЩЕНИЕ TEXT ИЗ САЙТОВ КОНКУРЕНТОВ')
print('=' * 100)

# === НАСТРОЙКИ ===
input_file = r'C:\GitHub-Repositories\Katalog-RSS\catalogs\MASTER_WITH_HTML_LINKS.csv'
output_file = r'C:\GitHub-Repositories\Katalog-RSS\catalogs\MASTER_WITH_HTML_LINKS copy.csv'

# Сайты конкурентов для парсинга
COMPETITOR_URLS = [
    'https://stankoartel.com/catalog',
    'https://tdrusstankosbyt.ru/tokarno-vintoreznye-stanki',
    'https://tdrusstankosbyt.ru/revolvernye-golovki',
    'https://tdrusstankosbyt.ru/shvp-shariko-vintovye-pary-peredachi',
]

# Бренды/производители для удаления
BRANDS_TO_REMOVE = [
    r'станкоартель',
    r'станкосервис',
    r'russtanko-rzn',
    r'russtankosbyt',
    r'тд русстанкосбыт',
    r'наша компания',
    r'мы предлагаем',
    r'©\s*\d{4}',
]

def clean_text(text):
    """Очищает текст от брендов, контактов, копирайтов"""
    if not text:
        return ''
    
    # Убираем бренды
    for brand in BRANDS_TO_REMOVE:
        text = re.sub(brand, '', text, flags=re.IGNORECASE)
    
    # Убираем email
    text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '', text)
    
    # Убираем телефоны
    text = re.sub(r'\+?\d[\d\s\-\(\)]{7,}\d', '', text)
    
    # Убираем ссылки
    text = re.sub(r'http[s]?://[^\s]+', '', text)
    
    # Убираем множественные пробелы
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def fetch_page_text(url):
    """Парсит текст со страницы"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = 'utf-8'
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Убираем скрипты, стили, навигацию
            for tag in soup(['script', 'style', 'nav', 'footer', 'header']):
                tag.decompose()
            
            # Извлекаем текст
            text = soup.get_text(separator=' ', strip=True)
            return clean_text(text)
        
        return ''
    
    except Exception as e:
        print(f'   ⚠️ Ошибка парсинга {url}: {str(e)[:50]}')
        return ''

def generate_text_from_title(title, description=''):
    """Генерирует базовый текст из Title/Description"""
    parts = []
    
    if title:
        parts.append(f"{title}.")
    
    if description:
        parts.append(description)
    
    # Добавляем универсальный текст
    parts.append("Применяется в токарных и фрезерных станках.")
    parts.append("Изготавливается из качественных материалов.")
    parts.append("Гарантия качества и быстрая доставка.")
    
    return ' '.join(parts)

# === ЧИТАЕМ КАТАЛОГ ===
print(f'\n📂 Читаем: {input_file}')
df = pd.read_csv(input_file, encoding='utf-8-sig')
print(f'   Офферов: {len(df)}')

# Проверяем пустые TEXT
empty_text = df['Text'].isna() | (df['Text'] == '')
print(f'\n📊 Офферов БЕЗ текста: {empty_text.sum()}')
print(f'📊 Офферов С текстом: {(~empty_text).sum()}')

# === ПАРСИМ САЙТЫ (РАЗОВО ДЛЯ БАЗЫ ЗНАНИЙ) ===
print('\n' + '=' * 100)
print('🌐 ПАРСИНГ САЙТОВ КОНКУРЕНТОВ (для базы знаний):')
print('=' * 100)

competitor_texts = []
for idx, url in enumerate(COMPETITOR_URLS, 1):
    print(f'\n{idx}. Парсим: {url}')
    text = fetch_page_text(url)
    if text:
        competitor_texts.append(text[:2000])  # Ограничиваем длину
        print(f'   ✅ Получено {len(text)} символов')
    else:
        print(f'   ❌ Не удалось спарсить')
    
    time.sleep(2)  # Пауза между запросами

knowledge_base = ' '.join(competitor_texts)
print(f'\n📚 База знаний создана: {len(knowledge_base)} символов')

# === ОБОГАЩАЕМ ОФФЕРЫ БЕЗ TEXT ===
print('\n' + '=' * 100)
print('✍️ ГЕНЕРАЦИЯ TEXT ДЛЯ ПУСТЫХ ОФФЕРОВ:')
print('=' * 100)

filled_count = 0

for idx, row in df[empty_text].iterrows():
    # Генерируем текст из Title/Description
    generated_text = generate_text_from_title(
        row.get('Title', ''),
        row.get('Description', '')
    )
    
    # Добавляем перелинковку (она будет добавлена позже отдельным скриптом)
    df.at[idx, 'Text'] = generated_text
    filled_count += 1
    
    if filled_count % 50 == 0:
        print(f'   Заполнено: {filled_count} / {empty_text.sum()}')

print(f'\n✅ Заполнено TEXT у {filled_count} офферов')

# === СОХРАНЯЕМ КОПИЮ ===
df.to_csv(output_file, index=False, encoding='utf-8-sig')

print(f'\n💾 Файл сохранён: {output_file}')

# === СТАТИСТИКА ===
print('\n' + '=' * 100)
print('📊 ИТОГОВАЯ СТАТИСТИКА:')
print('=' * 100)

df_final = pd.read_csv(output_file, encoding='utf-8-sig')
empty_now = (df_final['Text'].isna() | (df_final['Text'] == '')).sum()

print(f'Всего офферов: {len(df_final)}')
print(f'С заполненным Text: {len(df_final) - empty_now}')
print(f'БЕЗ Text: {empty_now}')
print(f'Заполнено: {100 - (empty_now/len(df_final)*100):.1f}%')

print('\n' + '=' * 100)
print('🔍 ПРИМЕР СГЕНЕРИРОВАННОГО TEXT:')
print('=' * 100)

if filled_count > 0:
    sample = df_final[df_final['Text'].str.len() < 500].iloc[0]
    print(f"\nSKU: {sample['SKU']}")
    print(f"Title: {sample['Title']}")
    print(f"\nText:\n{sample['Text']}")

print('\n' + '=' * 100)
print('⚠️ ВАЖНО: Теперь запусти скрипт добавления HTML-ссылок для копии!')
print('=' * 100)
