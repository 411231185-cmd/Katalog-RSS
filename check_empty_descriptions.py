# -*- coding: utf-8 -*-
import pandas as pd

df = pd.read_csv('MASTER_CATALOG_WITH_DESCRIPTIONS.csv', encoding='utf-8-sig')

# Офферы без Description
empty_desc = df[pd.isna(df['Description']) | (df['Description'] == '')]

print("=" * 80)
print("OFFERS WITHOUT DESCRIPTION: " + str(len(empty_desc)))
print("=" * 80)
print("\n")

for idx, row in empty_desc.head(20).iterrows():
    print(str(idx+1) + ". SKU: " + str(row['SKU']))
    print("   Title: " + str(row['Title']))
    print("   Text: " + str(row['Text'])[:100] + "...")
    print()

# Сохраним в отдельный файл
empty_desc.to_csv('OFFERS_WITHOUT_DESCRIPTION.csv', index=False, encoding='utf-8-sig')
print("\nSaved to: OFFERS_WITHOUT_DESCRIPTION.csv")
