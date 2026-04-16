# -*- coding: utf-8 -*-
import pandas as pd
import re

filepath = r'catalogs\MASTER_WITH_HTML_LINKS copy.csv'
df = pd.read_csv(filepath, encoding='utf-8-sig')

print('=' * 80)
print('✂️  УКОРАЧИВАНИЕ ДЛИННЫХ TITLE')
print('=' * 80)

long_titles = df[df['Title'].notna() & (df['Title'].str.len() > 80)]
print(f'\nДлинных Title: {len(long_titles)}')

shortened = 0

for idx, row in long_titles.iterrows():
    old_title = row['Title']
    
    # Убираем лишнее: модели в скобках, артикулы
    new_title = old_title
    
    # Убираем артикулы типа "КЖ1842.02.001.026"
    new_title = re.sub(r'[А-ЯA-Z]{2,}\d+\.\d+\.\d+\.\d+', '', new_title)
    
    # Убираем лишние пробелы
    new_title = re.sub(r'\s+', ' ', new_title).strip()
    
    # Обрезаем до 80 символов по последнему слову
    if len(new_title) > 80:
        new_title = new_title[:77].rsplit(' ', 1)[0] + '...'
    
    if new_title != old_title:
        df.at[idx, 'Title'] = new_title
        shortened += 1
        print(f'\n{shortened}. SKU: {row["SKU"]}')
        print(f'   Было ({len(old_title)}): {old_title}')
        print(f'   Стало ({len(new_title)}): {new_title}')

if shortened > 0:
    df.to_csv(filepath, index=False, encoding='utf-8-sig')
    print(f'\n✅ Укорочено: {shortened} Title')
else:
    print('\n⏭️  Нечего укорачивать')

print('=' * 80)
