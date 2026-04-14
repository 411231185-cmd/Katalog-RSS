from pathlib import Path
import re
import pandas as pd

# Сканируем только кинематику (чтобы не тащить мусор с моделями и т.п.)
ROOT = Path(r"C:\GitHub-Repositories\Katalog-RSS\Kinematika-Chertegi")

# Куда складываем все шифры
DST = Path(r"C:\GitHub-Repositories\Katalog-RSS\Kinematika-Chertegi\Vse - Vse-Vse Shifri  .md")

TEXT_EXT = {".md", ".txt"}
EXCEL_EXT = {".xls", ".xlsx"}

# Шаблон для "внутреннего" шифра вида 1А64.02.942, 165.02.001, 1М63Н.20.185 и т.п.
PAT_CODE_CORE = re.compile(r"[0-9А-Яа-яЁё]+(?:\.[0-9А-Яа-яЁё]+)+")

# Более широкий паттерн-кандидат: буквы+цифры + .-/ длиной >= 3
PAT_CANDIDATE = re.compile(r"[0-9A-Za-zА-Яа-яЁё\.\-/]{3,}")


def split_line_to_candidates(line: str):
    """
    Разбиваем строку на кандидатов (по запятым и табам).
    """
    tokens = re.split(r"[,\t]+", line)
    return [t.strip() for t in tokens if t.strip()]


def extract_core_codes(text: str):
    """
    Из произвольного текста вытаскиваем все шифры:
    - сначала по широкому паттерну-кандидату;
    - затем внутри каждого кандидата ищем "ядро" шифров по PAT_CODE_CORE;
    - фильтруем очевидный мусор.
    """
    results = []

    for cand in PAT_CANDIDATE.findall(text):
        cand = cand.strip(" ,;()")

        if not cand:
            continue

        # Внутри кандидата ищем все "ядра" шифров вида 1А64.02.942, 165.02.160 и т.п.
        inner_codes = PAT_CODE_CORE.findall(cand)

        # Если такие "ядра" нашли — используем их
        if inner_codes:
            for code in inner_codes:
                results.append(code)
            continue

        # Иначе оставляем кандидата, если это "типичный" маркировочный код (буквы+цифры)
        has_letter = bool(re.search(r"[A-Za-zА-Яа-яЁё]", cand))
        has_digit = bool(re.search(r"\d", cand))
        if not (has_letter and has_digit):
            continue

        low = cand.lower()
        # отсечём явные размеры/мм/ф/резьбы
        if "мм" in low:
            continue
        if low.startswith("ф") or "ф." in low:
            continue
        if re.fullmatch(r"м\d+х\d+.*", low):
            continue  # типа М16х2мм

        results.append(cand)

    return results


def extract_codes_from_text(text: str):
    codes = []
    for line in text.splitlines():
        # игнорируем явные заголовки типа "1 вал", "2 вал", "угол"
        if re.match(r"^\s*\d+\s+вал\b", line, flags=re.IGNORECASE):
            continue
        if " угол" in line.lower():
            continue

        for token in split_line_to_candidates(line):
            codes.extend(extract_core_codes(token))
    return codes


def extract_codes_from_excel(path: Path):
    codes = []
    try:
        xls = pd.read_excel(path, sheet_name=None, header=None, dtype=str)
    except Exception:
        return codes

    for sheet_name, df in xls.items():
        for value in df.values.ravel():
            if pd.isna(value):
                continue
            s = str(value)
            codes.extend(extract_codes_from_text(s))
    return codes


def main():
    all_codes = []

    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue

        ext = path.suffix.lower()

        # не обрабатываем файл, в который пишем результат
        if path.resolve() == DST.resolve():
            continue

        try:
            if ext in TEXT_EXT:
                text = path.read_text(encoding="utf-8", errors="ignore")
                codes = extract_codes_from_text(text)
                if codes:
                    all_codes.extend(codes)

            elif ext in EXCEL_EXT:
                codes = extract_codes_from_excel(path)
                if codes:
                    all_codes.extend(codes)

        except Exception as e:
            print(f"Ошибка при обработке {path}: {e}")

    # убираем дубли, сохраняем порядок
    seen = set()
    unique = []
    for c in all_codes:
        if c not in seen:
            seen.add(c)
            unique.append(c)

    DST.parent.mkdir(parents=True, exist_ok=True)
    DST.write_text(", ".join(unique), encoding="utf-8")

    print(f"Найдено всего шифров (уникальных): {len(unique)}")
    print(f"Результат записан в: {DST}")


if __name__ == "__main__":
    main()