import pandas as pd
import re
import csv
from pathlib import Path

IN_PATH = Path(r"C:\GitHub-Repositories\Katalog-RSS\catalogs\TEST_2_OFFERA.csv")
OUT_PATH = Path(r"C:\GitHub-Repositories\Katalog-RSS\catalogs\TEST_2_OFFERA__import_example.csv")

TARGET_COLS = [
    "SKU", "Category", "Title", "Description", "Text", "Photo",
    "Price", "Quantity", "Price Old", "Editions", "Modifications",
    "External ID", "Parent UID"
]

def extract_url(val: str) -> str:
    """
    Превращает:
      [https://...](https://...) -> https://...
    и также вытаскивает первую http(s) ссылку из строки.
    """
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return ""
    s = str(val).strip()
    if not s:
        return ""
    m = re.search(r"\((https?://[^)]+)\)", s)
    if m:
        return m.group(1).strip()
    m = re.search(r"(https?://\S+)", s)
    if m:
        return m.group(1).strip()
    return s

# 1) Читаем входной CSV (у вас он в “тилинском” формате) [file:72]
df = pd.read_csv(IN_PATH, sep=";", encoding="utf-8-sig", dtype=str).fillna("")

# 2) Маппинг колонок (берём по смыслу)
src_to_target = {
    "SKU": "SKU",
    "Category": "Category",
    "Title": "Title",
    "Description": "Description",
    "Text": "Text",
    "Photo": "Photo",
    "Price": "Price",
    "Quantity": "Quantity",
    "Price Old": "Price Old",
    "Editions": "Editions",
    "Modifications": "Modifications",
    "External ID": "External ID",
    "Parent UID": "Parent UID",
}

out = pd.DataFrame()

for tgt in TARGET_COLS:
    src = None
    for k, v in src_to_target.items():
        if v == tgt and k in df.columns:
            src = k
            break
    out[tgt] = df[src] if src else ""

# 3) Photo: превращаем markdown-ссылку в “голый” URL, как в примере
out["Photo"] = out["Photo"].apply(extract_url)

# 4) Чуть подчистим числа (на случай пробелов)
for col in ["Price", "Quantity", "Price Old"]:
    out[col] = out[col].astype(str).str.strip()

# 5) Сохраняем: ; + UTF-8 with BOM + все значения в кавычках (важно для Text/HTML) [file:1]
out.to_csv(
    OUT_PATH,
    sep=";",
    index=False,
    encoding="utf-8-sig",
    quoting=csv.QUOTE_ALL
)

print(f"OK: saved -> {OUT_PATH}")
print("Columns:", list(out.columns))
print("Rows:", len(out))
