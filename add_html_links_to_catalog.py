# -*- coding: utf-8 -*-
import pandas as pd
import re

# === ПОЛНЫЙ СЛОВАРЬ ССЫЛОК (HTML-формат для Тильды) ===
LINKS_MAP = {
    # СТАНКИ
    '16М30Ф3': 'https://tdrusstankosbyt.ru/stanokchpu16303',
    '16А20Ф3': 'https://tdrusstankosbyt.ru/stanokchpu1620f3',
    'РТ755Ф3': 'https://tdrusstankosbyt.ru/stanokchpu7553',
    'РТ305М': 'https://tdrusstankosbyt.ru/stanokchpu305',
    'РТ779Ф3': 'https://tdrusstankosbyt.ru/stanokchpu7793',
    'РТ5001': 'https://russtankosbyt.tilda.ws/stanokrt5001',
    'РТ5003': 'https://russtankosbyt.tilda.ws/stanokrt5003',
    'РТ5004': 'https://russtankosbyt.tilda.ws/stanokrt5004',
    'РТ301.01': 'https://russtankosbyt.tilda.ws/stanokrtrt301',
    'РТ301.02': 'https://russtankosbyt.tilda.ws/stanokrtrt30102',
    'РТ301': 'https://russtankosbyt.tilda.ws/stanokrtrt301',
    'РТ917': 'https://russtankosbyt.tilda.ws/stanokrtrt917',
    '16К20': 'https://russtankosbyt.tilda.ws/stanokrtrt16k20',
    '16К40': 'https://russtankosbyt.tilda.ws/stanokrtrt16k40',
    '16Р25': 'https://russtankosbyt.tilda.ws/stanokrtrt16p25',
    '1М63Н': 'https://tdrusstankosbyt.ru/stanokrtrt1m63ndip300',
    '1М63': 'https://tdrusstankosbyt.ru/stanokrtrt1m63ndip300',
    '163': 'https://tdrusstankosbyt.ru/stanokrtrt1m63ndip300',
    'ДИП-300': 'https://tdrusstankosbyt.ru/stanokrtrt1m63ndip300',
    'ДИП300': 'https://tdrusstankosbyt.ru/stanokrtrt1m63ndip300',
    '1Н65': 'https://tdrusstankosbyt.ru/stanokrtrt1n65ndip500',
    '165': 'https://tdrusstankosbyt.ru/stanokrtrt1n65ndip500',
    '1М65': 'https://tdrusstankosbyt.ru/stanokrtrt1n65ndip500',
    'ДИП-500': 'https://tdrusstankosbyt.ru/stanokrtrt1n65ndip500',
    'ДИП500': 'https://tdrusstankosbyt.ru/stanokrtrt1n65ndip500',
    'РТ117': 'https://tdrusstankosbyt.ru/stanokrt117',
    'РТ817': 'https://tdrusstankosbyt.ru/stanokrtrt817',
    '1А983': 'https://tdrusstankosbyt.ru/stanok1a983',
    '1Н983': 'https://tdrusstankosbyt.ru/stanok1h983',
    'РТ783': 'https://tdrusstankosbyt.ru/stanokrt783',
    
    # ЗАПЧАСТИ
    'шестерни': 'https://russtankosbyt.tilda.ws/shesterninazakaz',
    'резцовый блок': 'https://tdrusstankosbyt.ru/rezcovyblok',
    'коробки подач': 'https://tdrusstankosbyt.ru/korobkipodach',
    'ШВП': 'https://tdrusstankosbyt.ru/shvp',
    'валы': 'https://tdrusstankosbyt.ru/valy',
    'шпиндельные бабки': 'https://tdrusstankosbyt.ru/shpindelnyibabki',
    'задние бабки': 'https://tdrusstankosbyt.ru/zadniibabki',
    'винты': 'https://tdrusstankosbyt.ru/vinty',
    'рейки': 'https://tdrusstankosbyt.ru/rejki',
    'каретка': 'https://tdrusstankosbyt.ru/karetki',
    'суппорт': 'https://tdrusstankosbyt.ru/support',
    'муфты обгонные': 'https://tdrusstankosbyt.ru/muftaobgonnaya',
    'гайки маточные': 'https://tdrusstankosbyt.ru/gajkimatochniye',
    'гайки': 'https://tdrusstankosbyt.ru/gajki',
    'фрикцион': 'https://tdrusstankosbyt.ru/frikcionvsbore',
    'диски': 'https://tdrusstankosbyt.ru/diski',
    'колеса конические': 'https://tdrusstankosbyt.ru/kolesakonicheskiye',
    'колеса зубчатые': 'https://tdrusstankosbyt.ru/kolesazubchatiye',
    'червячные пары': 'https://tdrusstankosbyt.ru/cherwiachniyepary',
    'фрикционные муфты': 'https://tdrusstankosbyt.ru/frikcionniyemufty',
    'патроны': 'https://tdrusstankosbyt.ru/patroni',
    'кулачки': 'https://tdrusstankosbyt.ru/kulachki',
    'венцы': 'https://tdrusstankosbyt.ru/venci',
    'ползушки': 'https://tdrusstankosbyt.ru/polzushki',
    'сухари': 'https://tdrusstankosbyt.ru/suchari',
    'револьверные головки': 'https://russtankosbyt.tilda.ws/revolvernyagolovkachpu',
    'ремонт': 'https://tdrusstankosbyt.ru/remontrevolvernyhgolovok',
}

def add_html_links(text):
    """Заменяет ключевые слова на HTML-ссылки"""
    if pd.isna(text) or text == '':
        return text
    
    result = str(text)
    
    # Сортируем по длине (длинные фразы сначала)
    sorted_keywords = sorted(LINKS_MAP.keys(), key=len, reverse=True)
    
    for keyword in sorted_keywords:
        url = LINKS_MAP[keyword]
        # Ищем точное совпадение слова (регистронезависимо)
        pattern = r'\b' + re.escape(keyword) + r'\b'
        
        # Проверяем, не заменён ли уже
        if not re.search(r'<a[^>]*>' + re.escape(keyword) + r'</a>', result, flags=re.IGNORECASE):
            replacement = f'<a href="{url}">{keyword}</a>'
            result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
    
    return result

# === ЧИТАЕМ ОСНОВНОЙ КАТАЛОГ ===
input_file = r'C:\GitHub-Repositories\Katalog-RSS\MASTER_CATALOG_CLEANED.csv'
output_file = r'C:\GitHub-Repositories\Katalog-RSS\catalogs\MASTER_WITH_HTML_LINKS.csv'

print('=' * 100)
print('🔗 ДОБАВЛЕНИЕ HTML-ССЫЛОК В КАТАЛОГ')
print('=' * 100)

df = pd.read_csv(input_file, encoding='utf-8-sig')

# Проверяем наличие колонки Text
if 'Text' not in df.columns:
    df['Text'] = ''

print(f"\n📊 Всего офферов: {len(df)}")
print(f"📚 Всего ключевых слов для перелинковки: {len(LINKS_MAP)}")

# Добавляем ссылки в Title, Description и Text
links_added = 0
for idx, row in df.iterrows():
    # Обрабатываем Description
    if pd.notna(row.get('Description')):
        df.at[idx, 'Description'] = add_html_links(row['Description'])
    
    # Обрабатываем Text (если есть)
    if pd.notna(row.get('Text')) and row['Text'] != '':
        df.at[idx, 'Text'] = add_html_links(row['Text'])
        links_added += df.at[idx, 'Text'].count('<a href=')

# Сохраняем
import os
os.makedirs(os.path.dirname(output_file), exist_ok=True)
df.to_csv(output_file, index=False, encoding='utf-8-sig')

print(f"\n✅ Обработка завершена!")
print(f"🔗 Добавлено HTML-ссылок: {links_added}")
print(f"\n📂 Файл сохранён: {output_file}")
print('=' * 100)

# Показываем пример
print('\n' + '=' * 100)
print('ПРИМЕР ОФФЕРА С HTML-ССЫЛКАМИ:')
print('=' * 100)
sample = df[df['Text'].str.contains('<a href=', na=False)].iloc[0] if len(df[df['Text'].str.contains('<a href=', na=False)]) > 0 else df.iloc[0]
print(f"SKU: {sample['SKU']}")
print(f"Title: {sample['Title']}")
print(f"\nDescription:")
print(sample['Description'][:300] if pd.notna(sample['Description']) else 'Нет')
print(f"\nText (первые 500 символов):")
print(sample['Text'][:500] if pd.notna(sample['Text']) else 'Нет')
print('...')
print('=' * 100)
