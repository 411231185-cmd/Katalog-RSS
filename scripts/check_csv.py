import pandas as pd

# Путь к файлу
file_path = r"C:\GitHub-Repositories\Katalog-RSS\catalogs\TOP-KATALOG-s-prefiksami-i-foto copy 2-CHPU-TEXT.csv"

# Загружаем CSV
df = pd.read_csv(file_path, encoding='utf-8')

# Показываем первые строки
print("=" * 80)
print("ПЕРВЫЕ 5 СТРОК ФАЙЛА:")
print("=" * 80)
print(df.head())

print("\n" + "=" * 80)
print("ИНФОРМАЦИЯ О ФАЙЛЕ:")
print("=" * 80)
print(f"Всего строк: {len(df)}")
print(f"Всего колонок: {len(df.columns)}")
print(f"\nНазвания колонок:")
for i, col in enumerate(df.columns, 1):
    print(f"  {i}. {col}")

print("\n" + "=" * 80)
print("ПРОВЕРКА ПУСТЫХ ЯЧЕЕК:")
print("=" * 80)
print(df.isnull().sum())

print("\n" + "=" * 80)
print("СТАТИСТИКА ПО ТЕКСТОВЫМ ПОЛЯМ:")
print("=" * 80)
for col in df.columns:
    empty_count = df[col].isnull().sum() + (df[col] == '').sum()
    filled_count = len(df) - empty_count
    print(f"{col}: заполнено {filled_count}/{len(df)} ({filled_count*100//len(df)}%)")
