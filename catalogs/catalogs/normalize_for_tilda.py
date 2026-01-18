import csv
import pandas as pd
import re

SRC = r"catalogs\TEST_2_OFFERA.csv"
OUT = r"catalogs\TEST_2_OFFERA__TILDA_IMPORT.csv"

def clean_md_link(s: str) -> str:
    # превращает [https://...](https://...) -> https://...
    return re.sub(r"\[(https?://[^\]]+)\]\(\1\)", r"\1", s)

df = pd.read_csv(SRC, sep=";", encoding="utf-8-sig", dtype=str).fillna("")

# 1) Жестко: Tilda UID = SKU (чтобы не было сюрпризов)
if "Tilda UID" in df.columns and "SKU" in df.columns:
    df["Tilda UID"] = df["SKU"]

# 2) Чистим ссылки (важно для Photo/Url)
for col in ["Photo", "Url"]:
    if col in df.columns:
        df[col] = df[col].astype(str).map(clean_md_link)

# 3) Подчищаем пробелы (особенно в начале Text)
for col in ["Title", "Description", "Text", "Category", "Brand", "SKU"]:
    if col in df.columns:
        df[col] = df[col].astype(str).str.strip()

# 4) Сохраняем так, чтобы HTML/; не ломали колонки
df.to_csv(OUT, sep=";", index=False, encoding="utf-8-sig", quoting=csv.QUOTE_ALL)
print("OK:", OUT)
