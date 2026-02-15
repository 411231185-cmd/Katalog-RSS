import csv
from pathlib import Path

CSV_PATH = Path("docs/ТКП/ТКП-1Н65-ДИП500-полная-номенклатура-kinematics_part1.csv")

SECTION_ORDER = [
    "Бабка передняя",
    "Патрон",
    "Колёса зубчатые сменные (гитара)",
    "Коробка подач основная",
    "Коробка подач с питчевыми резьбами",
    "Коробка подач питчевая"
]

TABLE_HEADER = "| Поз. | Z | Модуль | Ширина | Обозначение | Наименование |\n|---|---|---|---|---|---|"

def read_csv():
    with open(CSV_PATH, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    return rows

def render_markdown(rows):
    out = []
    for section in SECTION_ORDER:
        section_rows = [r for r in rows if r["section"] == section]
        if not section_rows:
            continue
        out.append(f"### {section}\n")
        out.append(TABLE_HEADER)
        for r in section_rows:
            out.append(f"| {r['pos'] or ''} | {r['Z'] or ''} | {r['module'] or ''} | {r['width'] or ''} | {r['designation'] or ''} | {r['name'] or ''} |")
        out.append("")
    return "\n".join(out)

def main():
    rows = read_csv()
    md = render_markdown(rows)
    print(md)

if __name__ == "__main__":
    main()
