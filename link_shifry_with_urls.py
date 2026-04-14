from pathlib import Path
from urllib.parse import urlparse
import re

BASE_DIR = Path(r"C:\GitHub-Repositories\Katalog-RSS\Kinematika-Chertegi")

# тут лежат все ссылки страниц товаров
STRANICY = BASE_DIR / "stranicy.md"

# тут ТОЛЬКО список шифров БЕЗ ссылок
CODES_FILE = BASE_DIR / "Vse Shifri-ONLY.md"

# сюда запишем кликабельные шифры
OUT_FILE = BASE_DIR / "Vse Shifri-Perelinkovka-Directus.md"

TRASH_TOKENS = {
    "koleso", "zubcatoe", "val", "val-1", "val-2", "mufta",
    "prjvoda", "stola", "stanka", "korobkj", "skorostei",
    "mehanjzma", "sesterna",
}

def normalize_code_from_slug(slug: str) -> str | None:
    parts = [p for p in slug.split("-") if p]
    filtered = [p for p in parts if p not in TRASH_TOKENS]
    if not filtered:
        return None

    code_blocks = []
    for p in filtered:
        if re.search(r"\d", p):
            code_blocks.append(p)
        elif code_blocks:
            break

    if not code_blocks:
        return None

    code_blocks = code_blocks[:3]
    norm_blocks = [b.upper() for b in code_blocks]
    return ".".join(norm_blocks)

def extract_urls_from_text(text: str):
    url_re = re.compile(r"https?://[^\s\)\]]+")
    return url_re.findall(text)

def url_to_code(url: str) -> str | None:
    parsed = urlparse(url)
    path = parsed.path
    segments = [s for s in path.split("/") if s]
    if not segments:
        return None
    slug = segments[-1]
    return normalize_code_from_slug(slug)

def main():
    # читаем список шифров из Vse Shifri-ONLY.md
    raw_codes = CODES_FILE.read_text(encoding="utf-8", errors="ignore")
    wanted_codes = [c.strip() for c in raw_codes.split(",") if c.strip()]
    wanted_set = set(wanted_codes)

    # читаем все URL из stranicy.md и строим code -> url
    stranicy_text = STRANICY.read_text(encoding="utf-8", errors="ignore")
    urls = extract_urls_from_text(stranicy_text)

    code_to_url = {}
    for url in urls:
        code = url_to_code(url)
        if not code:
            continue
        if code not in wanted_set:
            continue
        if code not in code_to_url:
            code_to_url[code] = url

    # собираем кликабельный список в исходном порядке шифров
    items = []
    for code in wanted_codes:
        url = code_to_url.get(code)
        if not url:
            # шифр есть, но ссылку не нашли — просто добавим голый шифр
            items.append(code)
            continue
        items.append(f"[{code}]({url})")

    OUT_FILE.write_text(", ".join(items), encoding="utf-8")

    print(f"Шифров во входном списке: {len(wanted_codes)}")
    print(f"Нашли ссылок для шифров: {sum(1 for c in wanted_codes if c in code_to_url)}")
    print(f"Результат записан в: {OUT_FILE}")

if __name__ == "__main__":
    main()