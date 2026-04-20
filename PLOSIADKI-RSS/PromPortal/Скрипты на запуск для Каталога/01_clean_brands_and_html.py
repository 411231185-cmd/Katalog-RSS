import pathlib
import re
import pandas as pd
from bs4 import BeautifulSoup

ROOT = pathlib.Path(r"C:\GitHub-Repositories\Katalog-RSS")
FILE_PATH = ROOT / r"PLOSIADKI-RSS\PromPortal\PromPortal-РОВНЫЙ copy.xlsx"

NAME_COL = "Наименование"
ARTICLE_COL = "Код товара"
DESC_COL = "description_new"

FORBIDDEN_BRANDS = [
    "StankoArtel", "СтанкоАртель",
    "Rafamet", "Рафамет",
    "PromPortal", "Promportal", "Промпортал",
    "RusStanko", "Русстанко",
    "Rosstanko", "Россстанко",
    "StankiLife", "СтанкиЛайф",
    "KPSK", "КПСК",
    "Vse-k-stankam", "Все к станкам",
]

def strip_html(text: str) -> str:
    if not isinstance(text, str) or not text.strip():
        return ""
    soup = BeautifulSoup(text, "html.parser")
    txt = soup.get_text(separator="\n")
    txt = txt.replace("\xa0", " ").replace("\u200b", " ")
    lines = [l.strip() for l in txt.splitlines()]
    lines = [l for l in lines if l]
    return "\n".join(lines)

def clean_brands(text: str) -> str:
    if not isinstance(text, str):
        return text
    out = text
    for brand in FORBIDDEN_BRANDS:
        out = re.sub(re.escape(brand), "", out, flags=re.IGNORECASE)
    out = re.sub(r"\s{2,}", " ", out).strip()
    return out

def main():
    print("01: Чистка HTML и брендов в", FILE_PATH)
    df = pd.read_excel(FILE_PATH, engine="openpyxl")

    if DESC_COL not in df.columns:
        df[DESC_COL] = ""

    # Приводим колонку описания к строковому типу, чтобы не было float64/nan
    df[DESC_COL] = df[DESC_COL].astype("object")

    cleaned = 0
    for idx, row in df.iterrows():
        raw = row.get(DESC_COL, "")
        no_html = strip_html(str(raw))
        no_brands = clean_brands(no_html)
        df.at[idx, DESC_COL] = no_brands
        cleaned += 1

    df.to_excel(FILE_PATH, index=False, engine="openpyxl")
    print("01: обработано строк:", cleaned)
    print("01: файл перезаписан:", FILE_PATH)

if __name__ == "__main__":
    main()


