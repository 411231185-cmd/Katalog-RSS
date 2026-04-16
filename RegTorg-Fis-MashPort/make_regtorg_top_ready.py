import pandas as pd
import numpy as np

# Путь к исходному каталогу
catalog_path = 'RegTorg-Fis-MashPort/RegTorg_catalog_195_FOR_REGTORG.csv'
# Путь к итоговому файлу
output_path = 'RegTorg-Fis-MashPort/RegTorg_catalog_TOP_READY.xlsx'

# Ключевые слова для фильтрации популярных товаров
keywords = [
    'Суппорт', 'Револьверная головка', 'ШВП', 'Патрон', 'Люнет', 'Резцедержатель',
    'Винт ходовой', 'Шпиндель', 'Муфта', 'Шестерня', 'Кулачки', 'Диски фрикционные',
    'Гайка маточная', 'Вал', 'Насос', 'Шкив'
]

# Чтение основного каталога
try:
    df = pd.read_csv(catalog_path, encoding='utf-8')
except Exception:
    df = pd.read_csv(catalog_path, encoding='cp1251')

# Фильтрация по ключевым словам
mask = np.column_stack([
    df[col].astype(str).str.contains('|'.join(keywords), case=False, na=False)
    for col in ['Название','Описание','Ключевые_слова','Рубрика']
]).any(axis=1)
df_top = df[mask].copy()

# Проверка обязательных полей

def check_fields(row):
    errors = []
    if not (10 <= len(str(row['Название'])) <= 120):
        errors.append('Название')
    if not (200 <= len(str(row['Описание'])) <= 5000):
        errors.append('Описание')
    if not (10 <= len(str(row['Ключевые_слова'])) <= 120):
        errors.append('Ключевые_слова')
    try:
        float(row['Цена'])
    except:
        errors.append('Цена')
    if row['Валюта'] not in ['руб','USD','EUR','грн','бел. руб.','тенге']:
        errors.append('Валюта')
    if not row['Рубрика'] or len(str(row['Рубрика'])) > 200:
        errors.append('Рубрика')
    return ','.join(errors)

df_top['Ошибки'] = df_top.apply(check_fields, axis=1)

# Сохраняем итоговый файл
print(f'Сохраняю {output_path}...')
df_top.to_excel(output_path, index=False, engine='openpyxl')
print('Готово!')
