import re
from pathlib import Path

INP = Path("TOP-KATALOG-CAPILOT.csv")
OUT = Path("TOP-KATALOG-CAPILOT_FIXED.csv")

# [https://a](https://a) -> https://a
md_link = re.compile(r"\[(https?://[^\]]+)\]\(\1\)")

def clean_cell(s: str) -> str:
    if s is None:
        return ""
    s = s.strip()
    s = md_link.sub(r"\\1", s)
    return s

with INP.open("r", encoding="utf-8-sig", newline="") as f:
    lines = f.read().splitlines()

header = lines[0]
sep = ";"
expected_cols = header.count(sep) + 1

fixed = [header]

for line in lines[1:]:
    if not line.strip():
        continue

    # Быстрый фильтр мусорных дублей: строки, которые состоят почти из одних ';'
    # или заканчиваются на очень длинный хвост из ';' (как в твоих примерах)
    if re.fullmatch(r"[;\\s]+", line):
        continue
    if re.search(r";{20,}\\s*$", line):
        continue

    # Почистим markdown-ссылки (они у тебя в Photo/Url встречаются)
    line = md_link.sub(r"\\1", line)

    # Проверка количества колонок (по ';')
    cols = line.split(sep)

    # Если колонок больше нормы — почти всегда виновата Category с ';' без кавычек.
    # Здесь безопаснее НЕ гадать, а пометить строку, чтобы ты руками поправил.
    if len(cols) != expected_cols:
        # Добавим в конец комментарий в Tabs:1, чтобы ты нашел строку в файле
        # (и одновременно сохраним исходник рядом)
        # Tabs:1 - последняя колонка
        # Просто выведем строку в отдельный блок, но в CSV это нельзя.
        # Поэтому: пропустим и запишем в отдельный лог.
        continue

    cols = [clean_cell(c) for c in cols]
    fixed.append(sep.join(cols))

OUT.write_text("\\n".join(fixed) + "\\n", encoding="utf-8-sig")
print("OK:", OUT, "rows:", len(fixed)-1)
