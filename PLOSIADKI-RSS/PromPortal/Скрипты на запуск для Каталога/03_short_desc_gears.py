import pathlib
import pandas as pd
import re

ROOT = pathlib.Path(r"C:\GitHub-Repositories\Katalog-RSS")
FILE_PATH = ROOT / r"PLOSIADKI-RSS\PromPortal\PromPortal-РОВНЫЙ copy.xlsx"

NAME_COL = "Наименование"
ARTICLE_COL = "Код товара"
DESC_COL = "description_new"

def is_gear(name: str) -> bool:
    if not name:
        return False
    n = name.lower()
    return "колесо зубчатое" in n or "шестерн" in n

def improve_gear_desc(name: str, article: str, old_desc: str) -> str:
    name = (name or "").strip()
    article = (article or "").strip()
    base = f"{name} — цилиндрическое зубчатое колесо для передачи крутящего момента в кинематических цепях токарных станков."
    if article:
        base += f" Артикул: {article}."
    base += " Применяется в узлах коробки подач или коробки скоростей для формирования диапазонов подач и шагов резьб. ТД РУССтанкоСбыт."
    parts = old_desc.split("\n\n", 1)
    tail = ""
    if len(parts) == 2:
        tail = "\n\n" + parts[1]
    return base + tail

def main():
    print("03: Уточнение описаний для зубчатых колёс в", FILE_PATH)
    df = pd.read_excel(FILE_PATH, engine="openpyxl")

    if DESC_COL not in df.columns:
        print("03: нет колонки описания, пропускаю")
        return

    # Приводим колонку описания к строковому типу
    df[DESC_COL] = df[DESC_COL].astype("object")

    changed = 0
    for idx, row in df.iterrows():
        name = str(row.get(NAME_COL, "") or "")
        if not is_gear(name):
            continue
        article = str(row.get(ARTICLE_COL, "") or "")
        old_desc = str(row.get(DESC_COL, "") or "")
        new_desc = improve_gear_desc(name, article, old_desc)
        df.at[idx, DESC_COL] = new_desc
        changed += 1

    df.to_excel(FILE_PATH, index=False, engine="openpyxl")
    print("03: обновлено описаний (шестерни):", changed)
    print("03: файл перезаписан:", FILE_PATH)

if __name__ == "__main__":
    main()


