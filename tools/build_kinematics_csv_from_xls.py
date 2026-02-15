import openpyxl
import csv
import sys
from pathlib import Path

# Путь к исходному Excel-файлу
XLS_PATH = Path("Kinematika-Chertegi/1Н65/1 copy.xlsx")
# Путь к итоговому CSV
CSV_PATH = Path("docs/ТКП/ТКП-1Н65-ДИП500-полная-номенклатура-kinematics_part1.csv")

# Маппинг диапазонов позиций в секции (можно расширять)
SECTIONS = [
    (1, 32, "Бабка передняя"),
    (33, 33, "Патрон"),
    (34, 77, "Коробка подач основная"),
    (78, 99, "Коробка подач питчевая"),
    (100, 115, "Коробка подач питчевая"),
    (116, 146, "Фартук"),
    (147, 148, "Станина"),
    (149, 157, "Бабка задняя"),
    (158, 166, "Каретка"),
    (167, 171, "Суппорт"),
]

def get_section(pos):
    try:
        p = int(str(pos).strip())
    except Exception:
        return ""
    for start, end, name in SECTIONS:
        if start <= p <= end:
            return name
    return ""

def main():
    wb = openpyxl.load_workbook(XLS_PATH, data_only=True)
    ws = wb.active
    rows = list(ws.iter_rows(values_only=True))
    # Найти заголовки
    header_idx = None
    for i, row in enumerate(rows):
        if row and any("поз" in str(cell).lower() for cell in row):
            header_idx = i
            break
    if header_idx is None:
        print("Не найдена строка с заголовками!", file=sys.stderr)
        sys.exit(1)
    header = [str(cell).strip() if cell else '' for cell in rows[header_idx]]
    # Индексы нужных столбцов
    colmap = {k: i for i, k in enumerate(header)}
    # Ожидаемые столбцы: поз, Z, модуль, ширина, обозначение, наименование
    out_rows = []
    for row in rows[header_idx+1:]:
        if not row or not row[0]:
            continue
        pos = row[colmap.get('поз', 0)]
        if not pos:
            continue
        section = get_section(pos)
        out_rows.append([
            section,
            str(pos).strip(),
            str(row[colmap.get('Z', 1)]).strip() if colmap.get('Z', 1) < len(row) else '',
            str(row[colmap.get('модуль', 2)]).strip() if colmap.get('модуль', 2) < len(row) else '',
            str(row[colmap.get('ширина', 3)]).strip() if colmap.get('ширина', 3) < len(row) else '',
            str(row[colmap.get('обозначение', 4)]).strip() if colmap.get('обозначение', 4) < len(row) else '',
            str(row[colmap.get('наименование', 5)]).strip() if colmap.get('наименование', 5) < len(row) else '',
        ])
    # Запись в CSV
    with open(CSV_PATH, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['section','pos','Z','module','width','designation','name'])
        for r in out_rows:
            writer.writerow(r)
    print(f"Готово: {CSV_PATH} ({len(out_rows)} строк)")

if __name__ == "__main__":
    main()
