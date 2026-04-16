import pandas as pd
import os

src = 'RegTorg-Fis-MashPort/RegTorg_catalog_FINAL_3_test.xlsx'
dst = 'RegTorg-Fis-MashPort/RegTorg_catalog_FINAL_3_test_clean.xls'

# Читаем исходный файл
df = pd.read_excel(src)

# Оставляем только столбцы из официального шаблона
columns = [
    'ID_товара', 'Название', 'Описание', 'Ключевые_слова', 'Цена', 'Валюта',
    'Единица_измерения', 'Наличие', 'Тип_опт_розница', 'Рубрика',
    'Фотография', 'Артикул', 'Производитель', 'Страна_производитель'
]
df_clean = df[columns]

# Удаляем лишние пробелы в заголовках и значениях
for col in df_clean.columns:
    df_clean[col] = df_clean[col].astype(str).str.strip()

# Сохраняем в формате .xls (старый Excel)
try:
    import xlwt
    df_clean.to_excel(dst, index=False, engine='xlwt')
    print(f'Сохранено: {os.path.abspath(dst)}')
except Exception as e:
    print(f'Ошибка при сохранении: {e}')
print(df_clean)
