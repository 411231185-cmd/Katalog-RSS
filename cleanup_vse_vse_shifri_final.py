from pathlib import Path
import re

SRC = Path(r"C:\GitHub-Repositories\Katalog-RSS\Kinematika-Chertegi\Vse - Vse-Vse Shifri  .md")
DST = Path(r"C:\GitHub-Repositories\Katalog-RSS\Kinematika-Chertegi\Vse - Vse-Vse Shifri - final.md")

# ядро шифра вида 1А64.02.942, 165.02.001, 1М63Н.20.185 и т.п.
PAT_CODE_CORE = re.compile(r"[0-9А-Яа-яЁё]+(?:\.[0-9А-Яа-яЁё]+)+")

# общий кандидат: буквы+цифры+./- длиной >= 3
PAT_CANDIDATE = re.compile(r"[0-9A-Za-zА-Яа-яЁё\.\-/]{3,}")


def extract_codes_from_piece(piece: str):
    res = []

    t = piece.strip(" \t,;()")

    if not t:
        return res

    # 1) ядра шифров (разбивает склейки типа СВ141П.11.000СВ141П)
    inner = PAT_CODE_CORE.findall(t)
    for code in inner:
        res.append(code)

    # 2) плюс общие кандидаты (для шифров без точек, типа РТ755Ф3, 1М63Н)
    for cand in PAT_CANDIDATE.findall(t):
        cand = cand.strip(" \t,;()")
        if not cand:
            continue

        # уже есть как ядро
        if cand in inner:
            continue

        low = cand.lower()

        # отсекаем размеры/диаметры/резьбу
        if "мм" in low:
            continue
        if low.startswith("ф") or "ф." in low:
            continue
        if re.fullmatch(r"м\d+х\d+.*", low):
            continue  # М16х2мм и т.п.

        # должны быть буквы и цифры
        has_letter = bool(re.search(r"[A-Za-zА-Яа-яЁё]", cand))
        has_digit = bool(re.search(r"\d", cand))
        if not (has_letter and has_digit):
            continue

        # отсекаем короткие хвосты типа 010, 020, \1
        if len(cand) <= 3 and "." not in cand:
            continue

        # не берем явные мусорные окончания типа 'и' на конце после кода
        if cand.endswith("и") and not cand[:-1].endswith("Ф3"):
            cand = cand[:-1]

        res.append(cand)

    return res


def main():
    text = SRC.read_text(encoding="utf-8", errors="ignore")

    # поддержим оба варианта: либо всё через запятую, либо уже по строкам
    if "," in text:
        raw_pieces = [p.strip() for p in text.split(",") if p.strip()]
    else:
        raw_pieces = [p.strip() for p in text.splitlines() if p.strip()]

    all_codes = []
    for piece in raw_pieces:
        all_codes.extend(extract_codes_from_piece(piece))

    # убираем дубли, сохраняем порядок
    seen = set()
    unique = []
    for c in all_codes:
        if c not in seen:
            seen.add(c)
            unique.append(c)

    # пишем по одному шифру в строку
    DST.write_text("\n".join(unique), encoding="utf-8")

    print(f"Всего шифров после финальной очистки: {len(unique)}")
    print(f"Результат: {DST}")


if __name__ == "__main__":
    main()