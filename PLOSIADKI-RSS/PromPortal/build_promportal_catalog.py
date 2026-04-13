#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ТД РУССтанкоСбыт — Сборщик каталога для PromPortal
Запуск: python build_promportal_catalog.py
Результат: PROMPORTAL_READY.xlsx — готов к импорту на promportal.su
"""

import os
import re
import pandas as pd
from pathlib import Path

BASE = Path(r"C:\GitHub-Repositories\Katalog-RSS")

# ════════════════════════════════════════════
# 1. ИСТОЧНИКИ — откуда берём товары
# ════════════════════════════════════════════
SOURCES = {
    "rzn_offers":   BASE / "PLOSIADKI-RSS" / "PromPortal" / "RZN-список офферов.md",
    "catalog_oleg": BASE / "CATALOG_OLEG_FINAL_100.xlsx",
    "zap_chasti":   BASE / "RZN-сайт" / "Запасные части для токарно-винторезных станков мод. 1М63Н(1М63),16К40 (1А64),1Н65(1М65),РТ117,РТ817.md",
}

# ════════════════════════════════════════════
# 2. ИСКЛЮЧЕНИЯ — что уже загружено (30 офферов)
# ════════════════════════════════════════════
EXCLUDE_FILE = BASE / "PLOSIADKI-RSS" / "PromPortal" / "СПИСОК ОФФЕРОВ.md"

# ════════════════════════════════════════════
# 3. ШАБЛОН — колонки promportal.su
# ════════════════════════════════════════════
TEMPLATE_COLS = [
    "Наименование", "Описание", "Единица измерения", "Цена", "Валюта",
    "Код товара", "Производитель", "Наличие", "Раздел", "Товарная группа",
    "Поисковая фраза 1", "Поисковая фраза 2", "Поисковая фраза 3",
    "Поисковая фраза 4", "Поисковая фраза 5", "Поисковая фраза 6",
    "Поисковая фраза 7", "Поисковая фраза 8", "Поисковая фраза 9",
    "Поисковая фраза 10",
    "Характеристика 1 название", "Характеристика 1 значение", "Характеристика 1 единица",
    "Характеристика 2 название", "Характеристика 2 значение", "Характеристика 2 единица",
    "Характеристика 3 название", "Характеристика 3 значение", "Характеристика 3 единица",
    "Характеристика 4 название", "Характеристика 4 значение", "Характеристика 4 единица",
    "Характеристика 5 название", "Характеристика 5 значение", "Характеристика 5 единица",
]

# ════════════════════════════════════════════
# 4. МАППИНГ категорий по ключевым словам
# ════════════════════════════════════════════
CATEGORY_MAP = [
    (["резец", "резцы", "проходной", "подрезной", "отрезной", "расточной", "канавочный"],
     "Режущий инструмент", "Резцы токарные"),
    (["патрон", "патроны", "кулачковый", "трёхкулачковый", "четырёхкулачковый"],
     "Оснастка токарная", "Патроны токарные"),
    (["пиноль"], "Узлы и детали станков", "Пиноли"),
    (["суппорт"], "Узлы и детали станков", "Суппорты"),
    (["оправка", "оправки"], "Оснастка токарная", "Оправки"),
    (["втулка", "втулки", "переходная"], "Оснастка токарная", "Втулки переходные"),
    (["люнет"], "Оснастка токарная", "Люнеты"),
    (["планшайба"], "Оснастка токарная", "Планшайбы"),
    (["ходовой винт", "ходовой вал"], "Узлы и детали станков", "Ходовые винты и валы"),
    (["коробка подач", "коробка скоростей", "фартук"], "Узлы и детали станков", "Коробки передач"),
    (["шестерня", "шестерни", "зубчатое колесо"], "Узлы и детали станков", "Шестерни и зубчатые колёса"),
    (["подшипник"], "Узлы и детали станков", "Подшипники"),
    (["шпиндель"], "Узлы и детали станков", "Шпиндели"),
    (["направляющая"], "Узлы и детали станков", "Направляющие"),
    (["станок", "токарный станок", "1м63", "16к20", "1н65", "рт117", "рт817", "рт983", "16к40"],
     "Токарные станки", "Токарно-винторезные станки"),
]

def get_category(name: str):
    name_lower = name.lower()
    for keywords, section, group in CATEGORY_MAP:
        if any(kw in name_lower for kw in keywords):
            return section, group
    return "Запасные части к станкам", "Комплектующие токарных станков"

# ════════════════════════════════════════════
# 5. SEO: поисковые фразы по наименованию
# ════════════════════════════════════════════
MODELS = ["1М63", "16К20", "1Н65", "РТ117", "РТ817", "РТ983", "16К40", "1М65",
          "ДИП500", "1А64", "МК6056", "МК6057", "1М63Н"]

def gen_search_phrases(name: str) -> list:
    phrases = []
    # Фраза 1: само наименование (до 50 символов)
    phrases.append(name[:50])
    # Фраза 2: купить + наименование
    phrases.append(f"купить {name[:43]}"[:50])
    # Фраза 3: цена
    phrases.append(f"{name[:40]} цена"[:50])
    # Фраза 4-6: модели станков из названия
    found_models = [m for m in MODELS if m.lower() in name.lower()]
    for m in found_models[:3]:
        phrases.append(f"запчасти {m} {name[:30]}"[:50])
    # Фраза 7: завод
    phrases.append("запчасти токарный станок купить")
    phrases.append("комплектующие токарного станка")
    phrases.append("запасные части станок РУССтанкоСбыт")
    # Дополнить до 10
    while len(phrases) < 10:
        phrases.append("")
    return phrases[:10]

# ════════════════════════════════════════════
# 6. ПАРСЕРЫ источников
# ════════════════════════════════════════════

def parse_md_names(filepath: Path) -> list:
    """Извлекает наименования товаров из .md файлов"""
    names = []
    if not filepath.exists():
        print(f"⚠️  Файл не найден: {filepath}")
        return names
    with open(filepath, encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            # Пропускаем заголовки, пустые строки, разделители
            if not line or line.startswith("#") or line.startswith("---") or line.startswith("|"):
                continue
            # Убираем markdown-маркеры списков
            line = re.sub(r"^[-*•]\s+", "", line)
            line = re.sub(r"^\d+\.\s+", "", line)
            # Убираем лишние спецсимволы
            line = re.sub(r"\*+", "", line).strip()
            if len(line) > 5:  # минимальная длина наименования
                names.append(line)
    print(f"✅ {filepath.name}: {len(names)} строк")
    return names

def parse_xlsx_names(filepath: Path) -> list:
    """Извлекает наименования из xlsx"""
    if not filepath.exists():
        print(f"⚠️  Файл не найден: {filepath}")
        return []
    df = pd.read_excel(filepath, engine="openpyxl")
    # Ищем колонку с наименованием
    name_col = None
    for col in df.columns:
        if any(kw in str(col).lower() for kw in ["наименование", "название", "name", "title", "товар"]):
            name_col = col
            break
    if name_col is None:
        name_col = df.columns[0]  # берём первую колонку
    names = df[name_col].dropna().astype(str).tolist()
    names = [n.strip() for n in names if len(n.strip()) > 5]
    print(f"✅ {filepath.name}: {len(names)} строк (колонка: {name_col})")
    return names

def load_exclusions(filepath: Path) -> set:
    """Загружает список уже загруженных офферов"""
    if not filepath.exists():
        print(f"⚠️  Файл исключений не найден: {filepath}")
        return set()
    names = parse_md_names(filepath)
    excl = {n.lower().strip() for n in names}
    print(f"🚫 Исключений (уже на портале): {len(excl)}")
    return excl

# ════════════════════════════════════════════
# 7. ОСНОВНАЯ ЛОГИКА
# ════════════════════════════════════════════

def build_catalog():
    print("\n🚀 ТД РУССтанкоСбыт — Сборка каталога PromPortal")
    print("=" * 55)

    # Загружаем исключения
    exclusions = load_exclusions(EXCLUDE_FILE)

    # Собираем все наименования из источников
    all_names = []
    all_names += parse_md_names(SOURCES["rzn_offers"])
    all_names += parse_xlsx_names(SOURCES["catalog_oleg"])
    all_names += parse_md_names(SOURCES["zap_chasti"])

    print(f"\n📦 Всего до очистки: {len(all_names)}")

    # Дедупликация (нечувствительная к регистру)
    seen = set()
    unique_names = []
    for name in all_names:
        key = name.lower().strip()
        if key not in seen and key not in exclusions and len(name) > 5:
            seen.add(key)
            unique_names.append(name)

    print(f"✅ Уникальных новых позиций: {len(unique_names)}")
    print(f"🗑️  Дублей удалено: {len(all_names) - len(unique_names)}")

    # ════════════════════════════════════════
    # Строим DataFrame по шаблону promportal
    # ════════════════════════════════════════
    rows = []
    for name in unique_names:
        section, group = get_category(name)
        phrases = gen_search_phrases(name)
        row = {
            "Наименование": name,
            "Описание": f"Запасная часть к токарному станку — {name}. "
                        f"Производство и поставка комплектующих для токарно-винторезных станков. "
                        f"ТД РУССтанкоСбыт — поставщик запасных частей к станкам серий "
                        f"1М63, 16К20, 1Н65, РТ117, РТ817, РТ983, 16К40.",
            "Единица измерения": "шт",
            "Цена": "",
            "Валюта": "RUB",
            "Код товара": "",
            "Производитель": "ТД РУССтанкоСбыт",
            "Наличие": "в наличии",
            "Раздел": section,
            "Товарная группа": group,
        }
        # Поисковые фразы
        for i, phrase in enumerate(phrases, 1):
            row[f"Поисковая фраза {i}"] = phrase
        # Характеристики — заглушки (потом заполним)
        for i in range(1, 6):
            row[f"Характеристика {i} название"] = ""
            row[f"Характеристика {i} значение"] = ""
            row[f"Характеристика {i} единица"] = ""
        rows.append(row)

    df = pd.DataFrame(rows, columns=TEMPLATE_COLS)

    # ════════════════════════════════════════
    # Сохраняем результат
    # ════════════════════════════════════════
    out_path = BASE / "PLOSIADKI-RSS" / "PromPortal" / "PROMPORTAL_READY.xlsx"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_excel(out_path, index=False, engine="openpyxl")

    print(f"\n🎉 ГОТОВО! Файл сохранён:")
    print(f"   {out_path}")
    print(f"\n📊 Итог:")
    print(f"   Позиций для загрузки: {len(df)}")
    print(f"\n📂 Распределение по разделам:")
    print(df["Раздел"].value_counts().to_string())
    print(f"\n📂 Топ товарных групп:")
    print(df["Товарная группа"].value_counts().head(15).to_string())

if __name__ == "__main__":
    build_catalog()