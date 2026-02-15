import csv
import re
from pathlib import Path

# Исходный файл с "сырой" кинематикой
SRC = Path("Kinematika-Chertegi/Kinemati 1H65-7.csv")
# Итоговый эталонный CSV для KIN1
DST = Path("docs/ТКП/ТКП-1Н65-ДИП500-полная-номенклатура-kinematics_part1.csv")

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

def parse_csv():
    out_rows = []
    with open(SRC, encoding="utf-8-sig") as f:
        reader = csv.reader(f, delimiter='\t')
        for row in reader:
            # Пропуск пустых строк и заголовков
            if not row or all(not c.strip() for c in row):
                continue
            # Собрать все ячейки в одну строку и разбить по ;
            line = ';'.join(row)
            parts = [p.strip() for p in line.split(';') if p.strip()]
            # Ищем секцию и позицию
            for i, part in enumerate(parts):
                # Позиция — целое число или буква (a, b, ...)
                if re.match(r'^(\d+|[a-zа-я])$', part, re.I):
                    # Предыдущая ячейка — секция
                    section = parts[i-1] if i > 0 else ''
                    pos = part
                    # Дальше: Z, модуль, ширина, обозначение, наименование
                    z = parts[i+1] if i+1 < len(parts) else ''
                    module = parts[i+2] if i+2 < len(parts) else ''
                    width = parts[i+3] if i+3 < len(parts) else ''
                    designation = parts[i+4] if i+4 < len(parts) else ''
                    name = parts[i+5] if i+5 < len(parts) else ''
                    # Если секция пустая — определить по диапазону
                    if not section:
                        section = get_section(pos)
                    out_rows.append([
                        section, pos, z, module, width, designation, name
                    ])
    return out_rows

def main():
    rows = parse_csv()
    with open(DST, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['section','pos','Z','module','width','designation','name'])
        for r in rows:
            writer.writerow(r)
    print(f"Готово: {DST} ({len(rows)} строк)")

if __name__ == "__main__":
    main()
