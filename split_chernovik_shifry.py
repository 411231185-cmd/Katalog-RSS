from pathlib import Path
import re

SRC = Path(r"C:\GitHub-Repositories\Katalog-RSS\Kinematika-Chertegi\Шифры RSS\ЧЕРНОВИК-ВСЕ-ШИФРЫ-В-СТРОКУ.md")
DST = Path(r"C:\GitHub-Repositories\Katalog-RSS\Kinematika-Chertegi\Шифры RSS\ЧЕРНОВИК-ВСЕ-ШИФРЫ-В-СТОЛБИК.md")

# ядро шифра вида 16К20Т1.153.000.000, 55Ф359.50.000, ЗЛ722В.323.000
PAT_CODE_CORE = re.compile(r"[0-9А-Яа-яЁё]+(?:\.[0-9А-Яа-яЁё]+)+")

# общий кандидат: буквы+цифры+./- длиной >= 3
PAT_CANDIDATE = re.compile(r"[0-9A-Za-zА-Яа-яЁё\.\-/]{3,}")


def extract_codes_from_piece(piece: str):
    res = []

    # убираем слово "ШВП" и пробелы вокруг
    t = piece.replace("ШВП", "").strip(" \t,;")

    if not t:
        return res

    # 1) ядра шифров (разбивает склейки вида СВ141П.11.000СВ141П)
    inner = PAT_CODE_CORE.findall(t)
    for code in inner:
        res.append(code)

    # 2) плюс простые шифры без точек (типа РТ755Ф3.70.000РТ -> РТ755Ф3.70.000)
    for cand in PAT_CANDIDATE.findall(t):
        cand = cand.strip(" \t,;()")
        if not cand:
            continue

        # если это уже одно из "ядро"-код, пропускаем
        if cand in inner:
            continue

        low = cand.lower()

        # отсечь размеры/резьбы/диаметры
        if "мм" in low:
            continue
        if low.startswith("ф") or "ф." in low:
            continue
        if re.fullmatch(r"м\d+х\d+.*", low):
            continue

        # должны быть буквы и цифры
        has_letter = bool(re.search(r"[A-Za-zА-Яа-яЁё]", cand))
        has_digit  = bool(re.search(r"\d", cand))
        if not (has_letter and has_digit):
            continue

        # короткие хвосты типа 010, 020, \1 не берём
        if len(cand) <= 3 and "." not in cand:
            continue

        # типичные хвосты "РТ" в конце склейки: РТ755Ф3.70.000РТ
        if cand.endswith("РТ") and "." in cand:
            cand = cand[:-2]

        res.append(cand)

    return res


def main():
    text = SRC.read_text(encoding="utf-8", errors="ignore")

    # разбиваем исходную строку по запятым на куски
    pieces = [p.strip() for p in text.split(",") if p.strip()]

    all_codes = []
    for p in pieces:
        all_codes.extend(extract_codes_from_piece(p))

    # убираем дубли, сохраняем порядок
    seen = set()
    unique = []
    for c in all_codes:
        if c not in seen:
            seen.add(c)
            unique.append(c)

    # пишем по одному шифру в строку
    DST.write_text("\n".join(unique), encoding="utf-8")

    print(f"Всего шифров (уникальных): {len(unique)}")
    print(f"Результат записан в: {DST}")


if __name__ == "__main__":
    main()