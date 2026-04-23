import pathlib
import pandas as pd

ROOT = pathlib.Path(r"C:\GitHub-Repositories\Katalog-RSS")

PROMPORTAL_PATH = ROOT / r"PLOSIADKI-RSS\PromPortal\PromPortal-РОВНЫЙ copy.xlsx"
BATCHES_DIR = ROOT / r"Exel-Claude\batches"
OUTPUT_PATH = ROOT / r"PLOSIADKI-RSS\PromPortal\PromPortal-FINAL-with-descriptions-v2.xlsx"

DESC_COL = "description_new"
NEW_TOP_COL = "new_description_top"

# сюда позже подставим твой SERVICE_BLOCK из эталонного CSV
SERVICE_BLOCK = ""


def load_batches():
    """Собираем все обработанные батчи в один DataFrame."""
    all_rows = []
    for path in BATCHES_DIR.glob("promportal_batch_*.xlsx"):
        df = pd.read_excel(path)
        # ожидаем, что в батче уже есть new_description_top
        if NEW_TOP_COL in df.columns:
            all_rows.append(df[["row", "code", NEW_TOP_COL]])
    if not all_rows:
        return pd.DataFrame(columns=["row", "code", NEW_TOP_COL])
    return pd.concat(all_rows, ignore_index=True)


def main():
    print("Загружаю основной файл:", PROMPORTAL_PATH)
    df_main = pd.read_excel(PROMPORTAL_PATH, engine="openpyxl")

    df_batches = load_batches()
    if df_batches.empty:
        print("Нет ни одного батча с new_description_top")
        return

    # предполагаем, что 'row' в батче — это Excel-строка (1-based)
    df_batches["row_idx"] = df_batches["row"] - 1

    # Добавляем колонку, если её нет
    if NEW_TOP_COL not in df_main.columns:
        df_main[NEW_TOP_COL] = ""

    # Подставляем new_description_top в основной файл
    for _, r in df_batches.iterrows():
        idx = int(r["row_idx"])
        if 0 <= idx < len(df_main):
            df_main.at[idx, NEW_TOP_COL] = r[NEW_TOP_COL]

    # Если хочешь сразу собирать финальный description_new:
    # df_main[DESC_COL] = df_main[NEW_TOP_COL].fillna("").astype(str) + "\n\n" + SERVICE_BLOCK

    print("Сохраняю:", OUTPUT_PATH)
    df_main.to_excel(OUTPUT_PATH, index=False, engine="openpyxl")
    print("Готово.")


if __name__ == "__main__":
    main()