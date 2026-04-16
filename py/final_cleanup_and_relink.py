# -*- coding: utf-8 -*-
import pandas as pd
import re

print('=' * 100)
print('🧹 ФИНАЛЬНАЯ ОЧИСТКА И ПОЛНАЯ ПЕРЕЛИНКОВКА')
print('=' * 100)

# === РАСШИРЕННЫЙ СЛОВАРЬ ССЫЛОК (ДОБАВЛЯЕМ ВСЕ МОДЕЛИ) ===
LINKS_MAP = {
    # СТАНКИ ЧПУ
    '16М30Ф3': 'https://tdrusstankosbyt.ru/stanokchpu16303',
    '16А20Ф3': 'https://tdrusstankosbyt.ru/stanokchpu1620f3',
    'РТ755Ф3': 'https://tdrusstankosbyt.ru/stanokchpu7553',
    'РТ305М': 'https://tdrusstankosbyt.ru/stanokchpu305',
    'РТ779Ф3': 'https://tdrusstankosbyt.ru/stanokchpu7793',
    
    # СТАНКИ (ДОБАВЛЯЕМ ВСЕ МОДЕЛИ ИЗ СКРИНА)
    '1П756': 'https://tdrusstankosbyt.ru/stanok1p756',
    '16М30': 'https://tdrusstankosbyt.ru/stanokchpu16303',
    '16К30': 'https://tdrusstankosbyt.ru/stanok16k30',
    'РТ755': 'https://tdrusstankosbyt.ru/stanokchpu7553',
    'РТ717': 'https://tdrusstankosbyt.ru/stanokrt717',
    '4Л721': 'https://tdrusstankosbyt.ru/stanok4l721',
    
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

# === РАСШИРЕННЫЙ СПИСОК ДЛЯ УДАЛЕНИЯ ===
REMOVE_PATTERNS = [
    # Бренды конкурентов
    r'станкоартель',
    r'станкосервис',
    r'russtanko-rzn',
    r'rosstanko',
    
    # Заводы
    r'станкостроительный завод',
    r'машиностроительный завод',
    r'завод[\s\-]?\w+',
    r'[А-Я]{2,}\s+завод',
    
    # Города (список основных)
    r'\bТроицк\b',
    r'\bМосква\b',
    r'\bРязань\b',
    r'\bТула\b',
    r'\bКоломна\b',
    r'\bЕгорьевск\b',
    r'\bИваново\b',
    r'\bНижний Новгород\b',
    
    # Копирайты и контакты
    r'©\s*\d{4}',
    r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
    r'\+?\d[\d\s\-\(\)]{7,}\d',
    r'http[s]?://[^\s]+',
    
    # Рекламные фразы
    r'наша компания',
    r'мы предлагаем',
    r'звоните нам',
    r'свяжитесь с нами',
]

def deep_clean(text):
    """Глубокая очистка текста"""
    if pd.isna(text) or text == '':
        return text
    
    result = str(text)
    
    # Удаляем все паттерны
    for pattern in REMOVE_PATTERNS:
        result = re.sub(pattern, '', result, flags=re.IGNORECASE)
    
    # Очищаем множественные пробелы
    result = re.sub(r'\s+', ' ', result).strip()
    
    # Удаляем пустые предложения
    result = re.sub(r'\.\s*\.', '.', result)
    
    return result

def add_all_links_aggressive(text):
    """Агрессивная перелинковка - заменяет ВСЕ упоминания"""
    if pd.isna(text) or text == '':
        return text
    
    result = str(text)
    
    # Сортируем по длине (длинные фразы первыми)
    sorted_keywords = sorted(LINKS_MAP.keys(), key=len, reverse=True)
    
    for keyword in sorted_keywords:
        url = LINKS_MAP[keyword]
        
        # Ищем ВСЕ упоминания (даже внутри других слов через границы)
        pattern = r'\b' + re.escape(keyword) + r'\b'
        
        # Заменяем только если ещё НЕ в теге <a>
        if keyword not in result or '<a href=' not in result:
            replacement = f'<a href="{url}">{keyword}</a>'
            result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
    
    return result

# === ОБРАБОТКА ===
input_file = r'C:\GitHub-Repositories\Katalog-RSS\catalogs\MASTER_WITH_HTML_LINKS.csv'
output_file = r'C:\GitHub-Repositories\Katalog-RSS\catalogs\MASTER_WITH_HTML_LINKS.csv'

df = pd.read_csv(input_file, encoding='utf-8-sig')

print(f'\n📊 Всего офферов: {len(df)}')
print('\n🧹 ОЧИСТКА И ПЕРЕЛИНКОВКА...')

for idx, row in df.iterrows():
    # 1. Очищаем Title
    if pd.notna(row.get('Title')):
        df.at[idx, 'Title'] = deep_clean(row['Title'])
    
    # 2. Очищаем Description
    if pd.notna(row.get('Description')):
        df.at[idx, 'Description'] = deep_clean(row['Description'])
    
    # 3. Очищаем и перелинковываем Text
    if pd.notna(row.get('Text')):
        # Сначала очищаем
        clean_text = deep_clean(row['Text'])
        # Потом агрессивно перелинковываем
        df.at[idx, 'Text'] = add_all_links_aggressive(clean_text)
    
    if (idx + 1) % 100 == 0:
        print(f'   Обработано: {idx + 1} / {len(df)}')

# Сохраняем
df.to_csv(output_file, index=False, encoding='utf-8-sig')

print(f'\n✅ ГОТОВО!')
print(f'💾 Файл обновлён: {output_file}')

# Пример
print('\n' + '=' * 100)
print('📋 ПРИМЕР ОЧИЩЕННОГО ОФФЕРА:')
print('=' * 100)
sample = df.iloc[0]
print(f"\nSKU: {sample['SKU']}")
print(f"Title: {sample['Title']}")
print(f"\nText (первые 800 символов):")
print(sample['Text'][:800])
print('...')
print('=' * 100)
