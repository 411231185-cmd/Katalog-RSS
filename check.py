import pandas as pd
df = pd.read_csv('catalogs/FINAL_CATALOG_FOR_TILDA.csv', sep=';', encoding='utf-8', nrows=3)
print('='*80)
print('СТРУКТУРА (23 колонки):')
print('='*80)
for i, col in enumerate(df.columns):
    print(f'{i+1:2}. {col}')
print()
print('='*80)
print('ПЕРВАЯ СТРОКА:')
print('='*80)
row = df.iloc[0]
print(f'Tilda UID: {row["Tilda UID"]}')
print(f'Brand: {row["Brand"]}')
print(f'SKU: {row["SKU"]}')
print(f'Offers ID: {row["Offers ID"]}')
print(f'Title: {row["Title"]}')
print('='*80)
