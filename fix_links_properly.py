# -*- coding: utf-8 -*-
import pandas as pd
import re

print('=' * 100)
print('🔗 ПРАВИЛЬНАЯ ПЕРЕЛИНКОВКА (ИСПРАВЛЕНИЕ)')
print('=' * 100)

# === ПОЛНЫЙ СЛОВАРЬ ССЫЛОК ===
LINKS_MAP = {
    '16М30Ф3': 'https://tdrusstankosbyt.ru/stanokchpu16303',
    '16А20Ф3': 'https://tdrusstankosbyt.ru/stanokchpu1620f3',
    'РТ755Ф3': 'https://tdrusstankosbyt.ru/stanokchpu7553',
    'РТ305М': 'https://tdrusstankosbyt.ru/stanokchpu305',
    'РТ779Ф3': 'https://tdrusstankosbyt.ru/stanokchpu7793',
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

CLEANUP_PATTERNS = [
    r'станкоартель', r'станкосервис', r'russtanko-rzn', r'rosstanko',
    r'станкостроительный завод', r'машиностроительный завод',
    r'\bТроицк\b', r'\bМосква\b', r'\bРязань\b', r'\bТула\b',
    r'©\s*\d{4}', r'\+?\d[\d\s\-\(\)]{7,}\d',
]

def clean_text(text):
    if pd.isna(text) or text == '':
        return text
    result = str(text)
    for pattern in CLEANUP_PATTERNS:
        result = re.sub(pattern, '', result, flags=re.IGNORECASE)
    return re.sub(r'\s+', ' ', result).strip()

def safe_add_links(text):
    if pd.isna(text) or text == '':
        return text
    
    # Удаляем старые сломанные ссылки
    text = re.sub(r'<a href="[^"]*">\s*</a>', '', str(text))
    text = re.sub(r'<a href="\s*', '', text)
    
    result = str(text)
    sorted_keywords = sorted(LINKS_MAP.keys(), key=len, reverse=True)
    
    for keyword in sorted_keywords:
        url = LINKS_MAP[keyword]
        # Простой паттерн: граница слова + ключевое слово + граница слова
        # НЕ заменяем, если уже внутри <a>
        if f'<a href="{url}">' not in result:
            pattern = r'\b' + re.escape(keyword) + r'\b'
            replacement = f'<a href="{url}">{keyword}</a>'
            result = re.sub(pattern, replacement, result, flags=re.IGNORECASE, count=10)
    
    return result

# === ОБРАБОТКА ===
input_file = r'C:\GitHub-Repositories\Katalog-RSS\catalogs\MASTER_BACKUP_BEFORE_FIX.csv'
output_file = r'C:\GitHub-Repositories\Katalog-RSS\catalogs\MASTER_WITH_HTML_LINKS.csv'

df = pd.read_csv(input_file, encoding='utf-8-sig')

print(f'\n📊 Всего офферов: {len(df)}')
print('\n🔧 ИСПРАВЛЕНИЕ ССЫЛОК...')

for idx, row in df.iterrows():
    if pd.notna(row.get('Description')):
        clean = clean_text(row['Description'])
        df.at[idx, 'Description'] = safe_add_links(clean)
    
    if pd.notna(row.get('Text')):
        clean = clean_text(row['Text'])
        df.at[idx, 'Text'] = safe_add_links(clean)
    
    if (idx + 1) % 100 == 0:
        print(f'   Обработано: {idx + 1} / {len(df)}')

df.to_csv(output_file, index=False, encoding='utf-8-sig')

print(f'\n✅ ГОТОВО!')
print(f'💾 Файл обновлён: {output_file}')

print('\n' + '=' * 100)
print('📋 ПРИМЕР ИСПРАВЛЕННОГО ОФФЕРА:')
print('=' * 100)
sample = df.iloc[0]
print(f"\nSKU: {sample['SKU']}")
print(f"Title: {sample['Title']}")
print(f"\nText (первые 600 символов):")
print(sample['Text'][:600])
print('=' * 100)
