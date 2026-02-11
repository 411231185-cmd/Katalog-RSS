import pandas as pd
import os

# Список найденных файлов с "кинематикой" (по результатам поиска)
files = [
    r"catalogs/ЭТАЛОННЫЙ есть UID и SKU22.12.csv",
    r"catalogs/TEST_2_OFFERA__import_example.csv"
]

for file in files:
    try:
        if file.endswith('.csv'):
            df = pd.read_csv(file, encoding='utf-8')
        elif file.endswith('.xlsx'):
            df = pd.read_excel(file, engine='openpyxl')
        else:
            print(f"Не поддерживаемый формат: {file}")
            continue
        print(f"Файл {file} успешно прочитан. Кол-во строк: {len(df)}")
    except Exception as e:
        print(f"Ошибка при чтении {file}: {e}")
