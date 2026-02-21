import pandas as pd
import yaml
import os

src = 'RegTorg-Fis-MashPort/RegTorg_catalog_FINAL_3_test_clean.xlsx'
dst = 'RegTorg-Fis-MashPort/RegTorg_catalog_FINAL_3_test_clean.yml'

# Читаем файл с 3 офферами строго по шаблону
df = pd.read_excel(src)

# Формируем структуру YML (offers: list of offer dicts)
yml_data = {
    'offers': [row.dropna().to_dict() for _, row in df.iterrows()]
}

# Сохраняем в YML
with open(dst, 'w', encoding='utf-8') as f:
    yaml.dump(yml_data, f, allow_unicode=True, sort_keys=False)
print(f'YML сохранён: {os.path.abspath(dst)}')
print(f'Всего позиций: {len(yml_data["offers"])}')
