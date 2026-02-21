import pandas as pd
import yaml
import os

# Используем CSV как источник (можно заменить на итоговый XLSX при необходимости)
df = pd.read_csv('RegTorg-Fis-MashPort/RegTorg_catalog_195_FIXED.csv', encoding='utf-8')

# Оставляем только строки с фото
df = df[df['Фотография'].notnull() & (df['Фотография'] != '')]

# Оставляем только нужные поля (универсальный набор)
fields = [
    'ID_товара', 'Название', 'Описание', 'Цена', 'Валюта', 'Единица_измерения',
    'Наличие', 'Рубрика', 'Фотография', 'Артикул', 'Производитель', 'Страна_производитель'
]
df = df[fields]

# Формируем структуру YML (offers: list of offer dicts)
yml_data = {
    'offers': [row.dropna().to_dict() for _, row in df.iterrows()]
}

# Сохраняем в YML
out_path = os.path.abspath('RegTorg-Fis-MashPort/RegTorg_catalog_universal.yml')
with open(out_path, 'w', encoding='utf-8') as f:
    yaml.dump(yml_data, f, allow_unicode=True, sort_keys=False)
print(f'YML сохранён: {out_path}')
print(f'Всего позиций: {len(yml_data["offers"])}')
