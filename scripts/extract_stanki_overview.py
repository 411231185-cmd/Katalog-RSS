# -- coding: utf-8 --

import pandas as pd
from pathlib import Path

NEWCSV = Path(r"C:\GitHub-Repositories\Katalog-RSS\catalogs\NEW-Katalog-Tilda.csv")
TOPCSV = Path(r"C:\GitHub-Repositories\Katalog-RSS\catalogs\TOP-KATALOG-s-prefiksami-i-foto copy 2.csv")

def load_df(path: Path, name: str) -> pd.DataFrame:
    if not path.exists():
        raise SystemExit(f"Файл не найден: {path}")
    df = pd.read_csv(path, sep=";", encoding="utf-8-sig")
    print(f"[{name}] строк: {len(df)}, колонки: {list(df.columns)[:10]}")
    return df

def main():
    df_new = load_df(NEWCSV, "NEW")
    df_top = load_df(TOPCSV, "TOP")

    # фильтруем только раздел "Станки"
    def is_stanok(cat):
        return isinstance(cat, str) and cat.startswith("Станки;")

    new_stanki = df_new[df_new["Category"].apply(is_stanok)].copy()
    top_stanki = df_top[df_top["Category"].apply(is_stanok)].copy()

    print("\n[NEW] Станков:", len(new_stanki))
    print(new_stanki[["Tilda UID", "SKU", "Category", "Title"]].head(20))

    print("\n[TOP] Станков:", len(top_stanki))
    print(top_stanki[["Tilda UID", "SKU", "Category", "Title"]].head(20))

    # Для анализа пересечений: по SKU
    new_sku = set(str(x) for x in new_stanki["SKU"].dropna())
    top_sku = set(str(x) for x in top_stanki["SKU"].dropna())

    print("\nSKU только в NEW:", len(new_sku - top_sku))
    print(sorted(list(new_sku - top_sku))[:20])

    print("\nSKU только в TOP:", len(top_sku - new_sku))
    print(sorted(list(top_sku - new_sku))[:20])

if __name__ == "__main__":
    main()
