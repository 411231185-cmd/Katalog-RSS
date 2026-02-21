import pandas as pd
import numpy as np
import os

out_path = os.path.abspath('RegTorg-Fis-MashPort/RegTorg_catalog_FINAL_200.xlsx')
print('Чтение TOP_READY...')
df_top = pd.read_excel('RegTorg-Fis-MashPort/RegTorg_catalog_TOP_READY.xlsx')
print('TOP_READY:', df_top.shape)
print(df_top.head())

print('Чтение FIXED...')
df_fixed = pd.read_csv('RegTorg-Fis-MashPort/RegTorg_catalog_195_FIXED.csv', encoding='utf-8')
print('FIXED:', df_fixed.shape)
print(df_fixed.head())

print('Чтение ПРИМЕР...')
df_example = pd.read_excel('RegTorg-Fis-MashPort/Пример-РегТорг.xls')
print('EXAMPLE:', df_example.shape)
print(df_example.head())

ids_top = set(df_top['ID_товара']).union(set(df_top['Название']))
df_fixed_add = df_fixed[~df_fixed['ID_товара'].isin(ids_top) & ~df_fixed['Название'].isin(ids_top)]
df_example_add = df_example[~df_example['ID_товара'].isin(ids_top) & ~df_example['Название'].isin(ids_top)]

print('df_fixed_add:', df_fixed_add.shape)
print('df_example_add:', df_example_add.shape)

df_fixed_add = df_fixed_add[df_fixed_add['Фотография'].notnull() & (df_fixed_add['Фотография'] != '')]
df_example_add = df_example_add[df_example_add['Фотография'].notnull() & (df_example_add['Фотография'] != '')]

print('df_fixed_add (с фото):', df_fixed_add.shape)
print('df_example_add (с фото):', df_example_add.shape)

rows_to_add = 200 - len(df_top)
df_add = pd.concat([df_fixed_add, df_example_add], ignore_index=True).head(rows_to_add)
print('df_add:', df_add.shape)
print(df_add.head())

df_final = pd.concat([df_top, df_add], ignore_index=True)
print('df_final:', df_final.shape)
print(df_final.head())

if len(df_final) > 0:
    df_final.to_excel(out_path, index=False, engine='openpyxl')
    print(f'Сохранено: {out_path}')
else:
    print('Итоговый DataFrame пуст, файл не сохранён.')
