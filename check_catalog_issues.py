# -*- coding: utf-8 -*-
import pandas as pd

filepath = r'catalogs\MASTER_WITH_HTML_LINKS copy.csv'
df = pd.read_csv(filepath, encoding='utf-8-sig')

print('=' * 80)
print(f'📊 СТАТИСТИКА КАТАЛОГА ({len(df)} офферов)')
print('=' * 80)

# 1. Длинные Title
long_titles = df[df['Title'].notna() & (df['Title'].str.len() > 80)]
print(f'\n📏 Длинные Title (>80 символов): {len(long_titles)}')
for idx, row in long_titles.head(10).iterrows():
    print(f"   {row['SKU']}: {len(row['Title'])} символов")

# 2. Пустые Description
empty_desc = df[df['Description'].isna() | (df['Description'] == '')]
print(f'\n📝 Пустые Description: {len(empty_desc)}')

# 3. NaN Title/Text (битые офферы)
nan_titles = df[df['Title'].isna()]
print(f'\n⚠️  Битые офферы (Title = NaN): {len(nan_titles)}')
if len(nan_titles) > 0:
    print('   SKU битых офферов:')
    for sku in nan_titles['SKU'].head(10):
        print(f'   - {sku}')

# 4. HTML-ссылки
first_text = str(df.iloc[0]['Text'])
links_count = first_text.count('<a href="')
print(f'\n🔗 HTML-ссылки (первый оффер): {links_count}')

print('=' * 80)
