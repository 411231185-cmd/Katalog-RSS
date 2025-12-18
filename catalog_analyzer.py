# catalog_analyzer.py
import pandas as pd
import os
from datetime import datetime

CATALOG_PATH = r"C:\Users\User\Dropbox\ООО РУССтанкоСБыт\ПРАЙСЫ РСС\ЭТАЛОННЫЕ\544 оффера  копия.csv"

def load_catalog():
    try:
        for sep in [';', ',', '\t']:
            try:
                df = pd.read_csv(CATALOG_PATH, sep=sep, encoding='utf-8-sig')
                if len(df.columns) > 5:
                    print(f" Каталог загружен: {len(df)} офферов, {len(df.columns)} колонок")
                    return df
            except:
                continue
    except Exception as e:
        print(f" Ошибка загрузки: {e}")
        return None

def main():
    print("="*80)
    print("АНАЛИЗАТОР КАТАЛОГА 544 ОФФЕРА")
    print("="*80)
    
    if not os.path.exists(CATALOG_PATH):
        print(f"\n Файл не найден: {CATALOG_PATH}")
        return
    
    df = load_catalog()
    if df is not None:
        print(f"\n Файл успешно загружен!")
        print(f"Строк: {len(df)}")
        print(f"Колонок: {len(df.columns)}")
        print(f"\nПервые колонки:")
        for i, col in enumerate(df.columns[:5], 1):
            print(f"  {i}. {col}")

if __name__ == "__main__":
    main()
