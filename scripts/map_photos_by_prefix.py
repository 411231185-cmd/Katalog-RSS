# -- coding: utf-8 --

import os
from pathlib import Path


# Основной каталог офферов (работаем по копии)
CATALOGCSV = r"C:\GitHub-Repositories\Старые репозитории\Katalog-RSS\catalogs\Топ КАТАЛОГИ\TOP-KATALOG-s-prefiksami-i-foto copy.csv"


# Словари префиксов
SLOVAR_OFFER = r"C:\GitHub-Repositories\Katalog-RSS\slovari\SLOVAR-PREFIKSOV-offery.txt"
PREFIKSY_ALL = r"C:\GitHub-Repositories\Katalog-RSS\slovari\PREFIKSY-VSE.txt"


# Папки с фото
PHOTOFOLDERS = [
    r"C:\Users\User\Dropbox\ООО РУССтанкоСБыт\База РСС\Каталог\Узлы станков",
    r"C:\Users\User\OneDrive\Рабочий стол\507 фото для тильды",
]


# Куда потом будем сохранять каталог с заполненными фото
OUTPUTCSV = r"C:\GitHub-Repositories\Старые репозитории\Katalog-RSS\catalogs\TOP-KATALOG-s-prefiksami-i-foto-with-photos.csv"


def collect_photofiles():
    """Собрать все фотки из указанных папок в словарь name_lower -> full_path."""
    photofiles = {}
    for base in PHOTOFOLDERS:
        p = Path(base)
        if not p.exists():
            print(f"Папка не найдена: {base}")
            continue
        for root, dirs, files in os.walk(p):
            for name in files:
                if name.lower().endswith((".jpg", ".jpeg", ".png")):
                    full = str(Path(root) / name)
                    photofiles[name.lower()] = full
    print(f"Всего фотофайлов найдено: {len(photofiles)}")
    return photofiles


def load_prefix_lines(path):
    """Считать строки словаря, игнорируя пустые и начинающиеся с #."""
    lines = []
    p = Path(path)
    if not p.exists():
        print(f"Файл словаря не найден: {path}")
        return lines
    for raw in p.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        lines.append(line)
    return lines


def load_offer_prefixes():
    """Словарь offerprefix -> список шаблонов для поиска в SKU/UID/Title."""
    lines = load_prefix_lines(SLOVAR_OFFER)
    offer_prefixes = {}
    for line in lines:
        # допустим формат: offerprefix;pattern1;pattern2;...
        parts = [p.strip() for p in line.split(";") if p.strip()]
        if not parts:
            continue
        key = parts[0].lower()
        patterns = [p.lower() for p in parts[1:]] or [key]
        offer_prefixes[key] = patterns
    print(f"Префиксов офферов: {len(offer_prefixes)}")
    return offer_prefixes


def main():
    photofiles = collect_photofiles()
    offer_prefixes = load_offer_prefixes()

    print("Всего фотофайлов:", len(photofiles))
    print("Префиксов офферов:", len(offer_prefixes))

    print("Примеры offer-префиксов:")
    for i, (k, v) in enumerate(offer_prefixes.items()):
        if i >= 5:
            break
        print(f"  {k} -> {v}")

    print("Примеры файлов с фото:")
    for i, (name, path) in enumerate(photofiles.items()):
        if i >= 5:
            break
        print(f"  {name} -> {path}")


if __name__ == "__main__":
    main()
