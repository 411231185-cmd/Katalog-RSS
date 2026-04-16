import pandas as pd
import re

filepath = 'catalogs/MASTER_WITH_HTML_LINKS copy.csv'
df = pd.read_csv(filepath, encoding='utf-8-sig')
print(f'Загружено: {len(df)} офферов')

cities = ['москва', 'москве', 'московский', 'санкт-петербург', 'спб']
brands = ['bosch', 'makita', 'бош', 'макита']

def clean_text(text):
    if pd.isna(text): return text
    text_str = str(text)
    for word in cities + brands:
        text_str = re.sub(r'\b' + word + r'\b', '', text_str, flags=re.IGNORECASE)
    return re.sub(r'\s+', ' ', text_str).strip()

for field in ['Title', 'Text', 'Description']:
    if field in df.columns:
        df[field] = df[field].apply(clean_text)
        print(f'Очищено: {field}')

df.to_csv(filepath, index=False, encoding='utf-8-sig')
print(f'ГОТОВО! Файл перезаписан: {filepath}')
