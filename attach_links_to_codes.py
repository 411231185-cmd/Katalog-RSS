from pathlib import Path
import re

# файл со страницами/ссылками
STRANICY = Path(r"C:\GitHub-Repositories\Katalog-RSS\Kinematika-Chertegi\stranicy.md")
# файл с «чистыми» шифрами по одному в строку
CODES_SRC = Path(r"C:\GitHub-Repositories\Katalog-RSS\Kinematika-Chertegi\Vse - Vse-Vse Shifri - final.md")
# КУДА писать результат
OUT_MD    = Path(r"C:\GitHub-Repositories\Katalog-RSS\Kinematika-Chertegi\stranicy -ссылки +шифры.md")


# вытащить карту шифр -> url из stranicy.md
LINK_RE = re.compile(r"\[([0-9A-Za-zА-Яа-яЁё\.\-]+)\]\((https?://[^\)]+)\)")

def build_map():
    text = STRANICY.read_text(encoding="utf-8", errors="ignore")
    mapping = {}

    for m in LINK_RE.finditer(text):
        code = m.group(1).strip()
        url  = m.group(2).strip()

        has_letter = bool(re.search(r"[A-Za-zА-Яа-яЁё]", code))
        has_digit  = bool(re.search(r"\d", code))
        if not (has_letter and has_digit):
            continue

        if code not in mapping:
            mapping[code] = url

    return mapping


def main():
    mapping = build_map()

    codes = [
        l.strip()
        for l in CODES_SRC.read_text(encoding="utf-8").splitlines()
        if l.strip()
    ]

    out_lines = []
    without_url = []

    for code in codes:
        url = mapping.get(code)
        if url:
            out_lines.append(f"[{code}]({url})")
        else:
            out_lines.append(code)
            without_url.append(code)

    OUT_MD.write_text("\n".join(out_lines), encoding="utf-8")

    print(f"Всего шифров: {len(codes)}")
    print(f"Со ссылками: {len(codes) - len(without_url)}")
    print(f"Без ссылок: {len(without_url)}")
    print(f"Результат: {OUT_MD}")

    if without_url:
        missing = OUT_MD.with_name("stranicy -шифры без ссылок.md")
        missing.write_text("\n".join(without_url), encoding="utf-8")
        print(f"Список шифров без URL: {missing}")


if __name__ == "__main__":
    main()