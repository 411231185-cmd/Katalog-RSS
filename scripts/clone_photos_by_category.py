# -- coding: utf-8 --

import pandas as pd
from pathlib import Path

# Входной и выходной файлы каталога
INPUTCSV = Path(r"C:\GitHub-Repositories\Katalog-RSS\catalogs\KATALOG-NEWyanvar.csv")
OUTPUTCSV = Path(r"C:\GitHub-Repositories\Katalog-RSS\catalogs\KATALOG-NEWyanvar-CLONED.csv")

# URL логотипа Тильды (чёрная заглушка) — оставим как маркер "нет фото"
FALLBACK_LOGO = "9ccd5bf24410bd9dfaa9c7a5b0184fed.jpg"  # часть пути, по которой узнаём логотип


def is_logo(url: str) -> bool:
    """Проверить, что это URL логотипа (fallback), а не нормальное фото."""
    if not isinstance(url, str):
        return True
    return FALLBACK_LOGO in url


def main():
    if not INPUTCSV.exists():
        print(f"Файл каталога не найден: {INPUTCSV}")
        return

    print("Читаем каталог...")
    df = pd.read_csv(INPUTCSV, sep=";", encoding="utf-8-sig")
    print("Строк в каталоге:", len(df))
    print("Колонки:", list(df.columns))

    if "Category" not in df.columns or "Photo" not in df.columns:
        print("В CSV нет нужных колонок 'Category' или 'Photo'.")
        return

    updated_rows = 0
    total_with_photo_before = df["Photo"].notna().sum()

    # Группировка по полю Category (по точному значению)
    for category_value, group_idx in df.groupby("Category").groups.items():
        idx_list = list(group_idx)
        if not idx_list:
            continue

        # Среди этой категории ищем эталонные фото (не логотип и не пустые)
        group = df.loc[idx_list]
        mask_good = group["Photo"].apply(lambda x: isinstance(x, str) and not is_logo(x) and x.strip() != "")
        good_photos = group.loc[mask_good, "Photo"]

        if good_photos.empty:
            # В этой категории нет ни одного нормального фото — пока пропускаем
            continue

        # Берём первое нормальное фото этой категории как эталон
        template_photo = good_photos.iloc[0]

        # Кому клонируем: пустые или логотипные
        def need_clone(x):
            if not isinstance(x, str) or x.strip() == "":
                return True
            if is_logo(x):
                return True
            return False

        mask_need_clone = group["Photo"].apply(need_clone)

        # Обновляем только те строки, где нужно клонировать
        clone_idx = group.loc[mask_need_clone].index
        if len(clone_idx) == 0:
            continue

        df.loc[clone_idx, "Photo"] = template_photo
        updated_rows += len(clone_idx)

        print(f"[CATEGORY] {category_value[:80]}...")
        print(f"  Эталонное фото: {template_photo}")
        print(f"  Клонировано в строк: {len(clone_idx)}")

    total_with_photo_after = df["Photo"].notna().sum()

    print("---- ИТОГИ ----")
    print("Было строк с непустым Photo:", total_with_photo_before)
    print("Стало строк с непустым Photo:", total_with_photo_after)
    print("Всего строк, где фото было клонировано:", updated_rows)

    print("Сохраняем результат...")
    df.to_csv(OUTPUTCSV, sep=";", index=False, encoding="utf-8-sig")
    print("Готово:", OUTPUTCSV)


if __name__ == "__main__":
    main()
