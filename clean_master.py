# -*- coding: utf-8 -*-
import pandas as pd
import re

print('=' * 80)
print('🧹 ЧИСТКА ОТ ГОРОДОВ И БРЕНДОВ')
print('=' * 80)

filepath = 'catalogs/MASTER_WITH_HTML_LINKS copy.csv'
df = pd.read_csv(filepath, encoding='utf-8-sig')
print(f'✅ Загружено: {len(df)} офферов')

cities = ['москва', 'москве', 'московский', 'санкт-петербург', 'спб']
brands = ['bosch', 'makita', 'бош', 'макита']

def clean_text(text):
    if pd.isna(text):
        return text
    text_str = str(text)
    for word in cities + brands:
        text_str = re.sub(r'\b' + re.escape(word) + r'\b', '', text_str, flags=re.IGNORECASE)
    text_str = re.sub(r'\s+', ' ', text_str).strip()
    return text_str

for field in ['Title', 'Text', 'Description']:
    if field in df.columns:
        df[field] = df[field].apply(clean_text)
        print(f'✅ Очищено: {field}')

df.to_csv('catalogs/MASTER_CLEANED.csv', index=False, encoding='utf-8-sig')
print(f'\n✅ Сохранено: catalogs/MASTER_CLEANED.csv')
