import csv, re

INP = r"C:/GitHub-Repositories/Katalog-RSS/RegTorg-Fis-MashPort/RegTorg_catalog_195_FIXED.csv"
OUT = r"C:/GitHub-Repositories/Katalog-RSS/RegTorg-Fis-MashPort/RegTorg_catalog_195_FIXED_ready.csv"

# Укажите нужное значение для рубрики (например, 'Запчасти')
RUBRIKA_VALUE = "Запчасти"

# Функция очистки поля Фотография
def clean_photo(s: str) -> str:
    s = s.strip()
    # превращаем [URL](URL) -> URL
    m = re.match(r'^\[(https?://[^\]]+)\]\((https?://[^)]+)\)$', s)
    if m:
        return m.group(2)
    # просто убрать скобки если кто-то напортачил
    s = s.replace('[', '').replace('](', '').replace(')', '')
    return s

def fix_value(val, field):
    if field == "Наличие":
        return "в наличии" if val.strip().lower().startswith("в наличии") else val
    if field == "Тип_опт_розница":
        return "опт/розница" if "опт" in val.lower() and "розница" in val.lower() else val
    return val

with open(INP, newline='', encoding='utf-8-sig') as f_in, open(OUT, 'w', newline='', encoding='utf-8-sig') as f_out:
    r = csv.DictReader(f_in)
    w = csv.DictWriter(f_out, fieldnames=r.fieldnames)
    w.writeheader()
    for row in r:
        row["Фотография"] = clean_photo(row.get("Фотография", ""))
        row["Наличие"] = fix_value(row.get("Наличие", ""), "Наличие")
        row["Тип_опт_розница"] = fix_value(row.get("Тип_опт_розница", ""), "Тип_опт_розница")
        row["Рубрика"] = RUBRIKA_VALUE
        w.writerow(row)

print("OK ->", OUT)
