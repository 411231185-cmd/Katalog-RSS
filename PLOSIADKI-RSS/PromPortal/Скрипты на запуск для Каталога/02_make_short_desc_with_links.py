import pathlib
import pandas as pd
import re

ROOT = pathlib.Path(r"C:\GitHub-Repositories\Katalog-RSS")
FILE_PATH = ROOT / r"PLOSIADKI-RSS\PromPortal\PromPortal-РОВНЫЙ copy.xlsx"

NAME_COL = "Наименование"
ARTICLE_COL = "Код товара"
DESC_COL = "description_new"

SERVICE_BLOCK = (
    "Подобрать конкретную запчасть вы можете у нас на сайте в разделе Каталог "
    "[ТД РУССтанкоСбыт](https://td-rss.ru/catalog).\n\n"
    "[ПАТРОНОВ](https://td-rss.ru/catalog/postavka-j-jzgotovlenie-patronov-dlya-stankov-tokarnye-j-specialnye-patrony)\n"
    "[ПОДШИПНИКОВ](https://td-rss.ru/catalog/postavka-podshipnikov-dlya-stankov-sharikovye-rolikovye-i-upornye-podshipniki)\n"
    "[ЦЕНТРОВ](https://td-rss.ru/catalog/postavka-j-jzgotovlenie-centrov-dlya-tokarnyh-stankov-centry-s-konysom-morze)\n"
    "[СУППОРТОВ](https://td-rss.ru/catalog/izgotovlenie-supportov-dlya-tokarnyh-stankov-supporty-v-sbore-pod-zakaz)\n"
    "[ПЛАНШАЙБ](https://td-rss.ru/catalog/izgotovlenie-planshaib-dlya-tokarnyh-stankov-planshaiby-pod-zakaz)\n"
    "[ШВП](https://td-rss.ru/catalog/izgotovlenie-shvp-dlya-stankov-sharikovintovye-pary-pod-zakaz)\n"
    "[ВИНТОВ](https://td-rss.ru/catalog/izgotovlenie-vintov-dlya-stankov-hodovyh-vintov-podach-i-specialnyh-vintov-pod-zakaz)\n"
    "[ВАЛОВ](https://td-rss.ru/catalog/izgotovlenie-valov-dlya-stankov-valov-shesteren-shlicevyh-i-privodnyh-valov-pod-zakaz)\n"
    "[ВТУЛОК](https://td-rss.ru/catalog/izgotovlenie-vtulok-dlya-stankov-perehodnyh-opornyh-i-napravlyayushchih-vtulok-pod-zakaz)\n"
    "[ШЕСТЕРНЕЙ / ШЕСТЕРЁН](https://td-rss.ru/catalog/izgotovlenie-shesteren-dlya-stankov-zubchatye-kolesa-i-shesterni-pod-zakaz)\n"
    "[ЛЮНЕТОВ](https://td-rss.ru/catalog/izgotovlenie-lyunetov-dlya-tokarnyh-stankov-nepodvizhnye-i-podvizhnye-lyunety-pod-zakaz)\n"
    "[ЗАЩИТНЫХ КОЖУХОВ](https://td-rss.ru/catalog/izgotovlenie-zashchitnyh-kozhuхov-dlya-stankov-lyuboj-slozhnosti)\n"
    "[КАБИНЕТНЫХ ЗАЩИТ](https://td-rss.ru/catalog/izgotovlenie-kabinetnyh-zashchit-dlya-stankov-lyuboj-slozhnosti)\n"
    "[ВКЛАДЫШЕЙ](https://td-rss.ru/catalog/jzgotovlenje-vkladysei-j-zahvatov-dla-zakreplenja-zagotovkj-jlj-jnstrumenta)\n"
    "[ЗАХВАТОВ](https://td-rss.ru/catalog/jzgotovlenje-vkladysei-j-zahvatov-dla-zakreplenja-zagotovkj-jlj-jnstrumenta)"
)

def make_short_description(name, article) -> str:
    name = "" if name is None else str(name)
    article = "" if article is None else str(article)

    name = name.strip()
    article = article.strip()

    parts = []
    if name:
        parts.append(f"{name} — запасная часть для токарного станка.")
    if article and article.lower() != "nan":
        parts.append(f"Артикул: {article}.")
    parts.append("Купить с доставкой по России.")
    parts.append("Подбор по каталогу и чертежам заказчика.")
    parts.append("ТД РУССтанкоСбыт.")
    return " ".join(parts)

def main():
    print("02: Формируем короткие описания + блок перелинковки в", FILE_PATH)
    df = pd.read_excel(FILE_PATH, engine="openpyxl")

    if NAME_COL not in df.columns or ARTICLE_COL not in df.columns:
        raise ValueError("Проверь NAME_COL и ARTICLE_COL — таких колонок нет в файле.")
    if DESC_COL not in df.columns:
        df[DESC_COL] = ""

    df[DESC_COL] = df[DESC_COL].astype("object")

    changed = 0
    for idx, row in df.iterrows():
        name = row.get(NAME_COL, "")
        article = row.get(ARTICLE_COL, "")
        short_desc = make_short_description(name, article)
        new_desc = short_desc + "\n\n" + SERVICE_BLOCK
        df.at[idx, DESC_COL] = new_desc
        changed += 1

    df.to_excel(FILE_PATH, index=False, engine="openpyxl")
    print("02: обновлено описаний:", changed)
    print("02: файл перезаписан:", FILE_PATH)

if __name__ == "__main__":
    main()



