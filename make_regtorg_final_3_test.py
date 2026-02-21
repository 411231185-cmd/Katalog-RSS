import pandas as pd
import os

src = 'RegTorg-Fis-MashPort/RegTorg_catalog_FINAL_200.xlsx'
dst = 'RegTorg-Fis-MashPort/RegTorg_catalog_FINAL_3_test.xlsx'

# Читаем исходный файл
try:
    df = pd.read_excel(src)
    print(f'Исходных позиций: {len(df)}')
    # Оставляем только первые 3 оффера
    df3 = df.head(3)
    df3.to_excel(dst, index=False, engine='openpyxl')
    print(f'Сохранено: {os.path.abspath(dst)}')
    print(df3)
except Exception as e:
    print(f'Ошибка: {e}')
