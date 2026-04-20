import pathlib
import pandas as pd

ROOT = pathlib.Path(r"C:\GitHub-Repositories\Katalog-RSS")
FILE_PATH = ROOT / r"PLOSIADKI-RSS\PromPortal\PromPortal-РОВНЫЙ copy.xlsx"

NAME_COL = "Наименование"
ARTICLE_COL = "Код товара"
DESC_COL = "description_new"

def is_shaft(name: str) -> bool:
    if not name:
        return False
    n = name.lower()
    return "вал " in n or n.startswith("вал-") or "вал " in n

def improve_shaft_desc(name: str, article: str, old_desc: str) -> str:
    name = (name or "").strip()
    article = (article or "").strip()
    base = f"{name} — вал приводных и кинематических цепей токарного станка."
    if article:
        base += f" Артикул: {article}."
    base += " Обеспечивает передачу крутящего момента между узлами станка и стабильную работу механизмов подачи. ТД РУССтанкоСбыт."
    parts = old_desc.split("\n\n", 1)
    tail = ""
    if len(parts) == 2:
        tail = "\n\n" + parts[1]
    return base + tail

def main():
    print("04: Уточнение описаний для валов в", FILE_PATH)
    df = pd.read_excel(FILE_PATH, engine="openpyxl")

    if DESC_COL not in df.columns:
        print("04: нет колонки описания, пропускаю")
        return

    # Приводим колонку описания к строковому типу
    df[DESC_COL] = df[DESC_COL].astype("object")

    changed = 0
    for idx, row in df.iterrows():
        name = str(row.get(NAME_COL, "") or "")
        if not is_shaft(name):
            continue
        article = str(row.get(ARTICLE_COL, "") or "")
        old_desc = str(row.get(DESC_COL, "") or "")
        new_desc = improve_shaft_desc(name, article, old_desc)
        df.at[idx, DESC_COL] = new_desc
        changed += 1

    df.to_excel(FILE_PATH, index=False, engine="openpyxl")
    print("04: обновлено описаний (валы):", changed)
    print("04: файл перезаписан:", FILE_PATH)

if __name__ == "__main__":
    main()


