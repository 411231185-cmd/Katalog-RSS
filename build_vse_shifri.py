from pathlib import Path
from urllib.parse import urlparse
import re

STRANICY = Path(r"C:\GitHub-Repositories\Katalog-RSS\Kinematika-Chertegi\stranicy.md")
OUT_FILE = Path(r"C:\GitHub-Repositories\Katalog-RSS\Kinematika-Chertegi\Vse Shifri.md")

# если для части URL хочешь задать шифры руками
URL_TO_CODE_MANUAL = {
    # пример:
    # "https://tdrusstankosbyt.ru/stanokrtrt30101": "РТ30101",
    # "https://tdrusstankosbyt.ru/stanokrtrt30102": "РТ30102",
}


TRASH_TOKENS = {
    "koleso", "zubcatoe", "val", "val-1", "val-2", "mufta",
    "prjvoda", "stola", "stanka", "korobkj", "skorostei",
    "mehanjzma", "sesterna",
}


def normalize_detail_code_from_slug(slug: str) -> str | None:
    # из koleso-zubcatoe-1m63b-08-164 -> 1M63B.08.164
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
    if url in URL_TO_CODE_MANUAL:
        return URL_TO_CODE_MANUAL[url]

    parsed = urlparse(url)
    path = parsed.path
    segments = [s for s in path.split("/") if s]
    if not segments:
        return None
    slug = segments[-1]
    return normalize_detail_code_from_slug(slug)


def main():
    text = STRANICY.read_text(encoding="utf-8", errors="ignore")
    urls = extract_urls_from_text(text)

    codes = []
    seen = set()

    for url in urls:
        code = url_to_code(url)
        if not code:
            continue
        if code in seen:
            continue
        seen.add(code)
        codes.append(code)

    OUT_FILE.write_text(", ".join(codes), encoding="utf-8")
    print(f"Уникальных шифров: {len(codes)}")
    print(f"Записано в: {OUT_FILE}")


if __name__ == "__main__":
    main()