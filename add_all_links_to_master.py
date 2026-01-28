# -*- coding: utf-8 -*-
import pandas as pd
import re

print('=' * 100)
print('🔗 ДОБАВЛЕНИЕ ПОЛНОЙ ПЕРЕЛИНКОВКИ В MASTER КАТАЛОГ')
print('=' * 100)

# === ПОЛНЫЙ СЛОВАРЬ ССЫЛОК ===
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

def add_inline_links(text):
    if pd.isna(text) or text == '':
        return text
    result = str(text)
    sorted_keywords = sorted(LINKS_MAP.keys(), key=len, reverse=True)
    for keyword in sorted_keywords:
        url = LINKS_MAP[keyword]
        pattern = r'\b' + re.escape(keyword) + r'\b'
        if not re.search(r'<a[^>]*>' + re.escape(keyword) + r'</a>', result, flags=re.IGNORECASE):
            replacement = f'<a href="{url}">{keyword}</a>'
            result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
    return result

def append_all_links(text, used_keywords):
    if pd.isna(text) or text == '':
        text = ''
    remaining_links = []
    for keyword, url in LINKS_MAP.items():
        if keyword not in used_keywords:
            remaining_links.append(f'<a href="{url}">{keyword}</a>')
    if remaining_links:
        footer = '<br><br><strong>Смотрите также:</strong><br>' + ', '.join(remaining_links)
        return str(text) + footer
    return text

input_file = r'C:\GitHub-Repositories\Katalog-RSS\catalogs\MASTER_WITH_HTML_LINKS.csv'
output_file = r'C:\GitHub-Repositories\Katalog-RSS\catalogs\MASTER_WITH_HTML_LINKS.csv'

df = pd.read_csv(input_file, encoding='utf-8-sig')
print(f'\n📊 Всего офферов: {len(df)}')

if 'Text' not in df.columns:
    df['Text'] = ''

print('\n🔧 ДОБАВЛЕНИЕ ПЕРЕЛИНКОВКИ...')
total_inline = 0
total_footer = 0

for idx, row in df.iterrows():
    base_text = row.get('Description', row.get('Title', ''))
    if pd.isna(base_text) or base_text == '':
        base_text = row.get('Title', '')
    
    text_with_inline = add_inline_links(str(base_text))
    
    used_keywords = set()
    for keyword in LINKS_MAP.keys():
        if re.search(r'\b' + re.escape(keyword) + r'\b', str(base_text), flags=re.IGNORECASE):
            used_keywords.add(keyword)
    
    final_text = append_all_links(text_with_inline, used_keywords)
    df.at[idx, 'Text'] = final_text
    
    inline_count = text_with_inline.count('<a href=')
    total_count = final_text.count('<a href=')
    total_inline += inline_count
    total_footer += (total_count - inline_count)
    
    if (idx + 1) % 100 == 0:
        print(f'   Обработано: {idx + 1} / {len(df)}')

df.to_csv(output_file, index=False, encoding='utf-8-sig')

print(f'\n✅ ГОТОВО!')
print(f'📊 Inline-ссылки: {total_inline}')
print(f'📊 Футер-ссылки: {total_footer}')
print(f'🔗 ВСЕГО ссылок: {total_inline + total_footer}')
print(f'\n💾 Файл обновлён: {output_file}')

sample = df.iloc[0]
print(f"\n📋 ПРИМЕР (SKU: {sample['SKU']}):")
print(sample['Text'][:500] + '...')
