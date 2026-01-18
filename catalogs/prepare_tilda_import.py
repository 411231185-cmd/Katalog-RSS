@'
# -*- coding: utf-8 -*-
import pandas as pd
import re
import csv
import os

FILE_IN = r'C:\GitHub-Repositories\Katalog-RSS\catalogs\KATALOG-TRANSFORMED.csv'
FILE_OUT = r'C:\GitHub-Repositories\Katalog-RSS\catalogs\KATALOG-TILDA-READY.csv'

print("=" * 80)
print("PREPARE TILDA IMPORT")
print("=" * 80)

df = pd.read_csv(FILE_IN, sep=';', encoding='utf-8-sig')
print(f"Загружено {len(df)} строк")

def clean_html(text):
    if pd.isna(text):
        return ''
    text = str(text)
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'&nbsp;', ' ', text)
    text = re.sub(r'&quot;', '"', text)
    return text.strip()

for col in ['Description', 'Text']:
    if col in df.columns:
        df[col] = df[col].apply(clean_html)

print("Очищено. Сохраняю...")

with open(FILE_OUT, 'w', encoding='utf-8-sig', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=df.columns, delimiter=';', quotechar='"', quoting=csv.QUOTE_ALL, lineterminator='\n')
    writer.writeheader()
    for idx, row in df.iterrows():
        writer.writerow(row.to_dict())

print(f"ГОТОВО! Файл: {FILE_OUT}")
print("Загрузи его в Тильду:")
print("  - Кодировка: UTF-8 with BOM")
print("  - Разделитель: ;")
print("  - Кавычка: \"")
'@ | Out-File -Encoding UTF8 C:\GitHub-Repositories\Katalog-RSS\prepare_tilda_import.py
