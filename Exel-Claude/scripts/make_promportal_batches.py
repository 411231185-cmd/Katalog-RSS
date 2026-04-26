import pandas as pd
from pathlib import Path

# БАЗОВАЯ ПАПКА ДЛЯ Excel-скриптов
base_dir = Path(r"C:\GitHub-Repositories\Katalog-RSS\Exel-Claude")

# Файл PromPortal-РОВНЫЙ лежит в родительской папке PromPortal
src_xlsx = base_dir.parent / "PLOSIADKI-RSS" / "PromPortal" / "PromPortal-РОВНЫЙ copy.xlsx"

# если листов несколько, пока берём первый (индекс 0)
sheet_name = 0

print("Читаю файл:", src_xlsx)
df = pd.read_excel(src_xlsx, sheet_name=sheet_name)

print("Строк в файле:", len(df))

# размер батча
batch_size = 200

# добавляем колонку batch_id в конец таблицы
df.insert(len(df.columns), "batch_id", (df.index // batch_size) + 1)

out_csv = base_dir / "PromPortal-ROVNY-BATCHES.csv"
df.to_csv(out_csv, index=False, encoding="utf-8-sig")

print("Готово, батчи сохранены в:", out_csv)