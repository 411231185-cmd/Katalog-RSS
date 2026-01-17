import pandas as pd
from pathlib import Path

CATALOGCSV = Path(r"C:\GitHub-Repositories\Katalog-RSS\catalogs\KATALOG-NEWyanvar.csv")

df = pd.read_csv(CATALOGCSV, sep=";", encoding="utf-8-sig")
print("Строк в каталоге:", len(df))
print("Колонки:", list(df.columns)[:10])
print(df[["Category","SKU","Title"]].head(5))
