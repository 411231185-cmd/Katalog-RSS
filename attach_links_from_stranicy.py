from pathlib import Path
import re

SRC = Path(r"C:\GitHub-Repositories\Katalog-RSS\Kinematika-Chertegi\stranicy.md")
DST = Path(r"C:\GitHub-Repositories\Katalog-RSS\Kinematika-Chertegi\stranicy -ссылки +шифры.md")

# Ищем Markdown-ссылки вида [РТ755Ф3](https://...)
LINK_RE = re.compile(r"\[([0-9A-Za-zА-Яа-яЁё\.\-]+)\]\((https?://[^\)]+)\)")

def main():
    text = SRC.read_text(encoding="utf-8", errors="ignore")

    pairs = []
    for m in LINK_RE.finditer(text):
        code = m.group(1).strip()
        url  = m.group(2).strip()

        # фильтр: это должен быть шифр (и буквы, и цифры)
        has_letter = bool(re.search(r"[A-Za-zА-Яа-яЁё]", code))
        has_digit  = bool(re.search(r"\d", code))
        if not (has_letter and has_digit):
            continue

        pairs.append((code, url))

    # убираем дубли по шифру, порядок первого вхождения
    seen = set()
    unique = []
    for code, url in pairs:
        if code in seen:
            continue
        seen.add(code)
        unique.append((code, url))

    # формируем одну строку: [КОД](URL), [КОД](URL), ...
    items = [f"[{code}]({url})" for code, url in unique]
    line = ", ".join(items)

    DST.write_text(line, encoding="utf-8")

    print(f"Найдено шифров: {len(unique)}")
    print(f"Результат записан в: {DST}")

if __name__ == "__main__":
    main()