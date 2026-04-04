#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
from pathlib import Path

BASE         = Path(r"C:\GitHub-Repositories\Katalog-RSS\Directus-RSS\Товары")
OFER_FILE    = BASE / "Офферы - ТОЛЬКО ОПИСАНИЕ И META.md"
DIRECTUS_DIR = BASE / "Directus-офферы сайта"
SEP = "=" * 62

def count_big_file(path):
    if not path.exists(): print(f"  ⚠️  НЕ НАЙДЕН: {path}"); return 0, []
    text   = path.read_text(encoding="utf-8", errors="replace")
    blocks = [b.strip() for b in re.split(r"\n---\n", text) if b.strip()]
    return len(blocks), [b.splitlines()[0].lstrip("#").strip() for b in blocks]

def count_folder(folder):
    if not folder.exists(): print(f"  ⚠️  НЕ НАЙДЕНА: {folder}"); return 0, []
    files = sorted(folder.glob("*.md"))
    return len(files), [f.stem for f in files]

def show(items, label):
    for i, x in enumerate(items[:10], 1): print(f"   {i:>3}. {x[:75]}")
    if len(items)>10: print(f"        ... и ещё {len(items)-10} {label}")

print(); print(SEP)
print("  📦 РУССтанкоСбыт — ПОДСЧЁТ ТОВАРОВ"); print(SEP)
n1,t1 = count_big_file(OFER_FILE)
print(f"\n📄 {OFER_FILE.name}\n   ✅ Блоков: {n1}")
if t1: print(); show(t1,"позиций")
n2,t2 = count_folder(DIRECTUS_DIR)
print(f"\n{SEP}\n📁 {DIRECTUS_DIR.name}\n   ✅ Файлов: {n2}")
if t2: print(); show(t2,"файлов")
print(f"\n{SEP}\n  ИТОГО: {n1+n2} шт.\n{SEP}")
input("\n  ENTER для выхода...")
