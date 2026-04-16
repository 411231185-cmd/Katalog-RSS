#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re, time, os, sys
from pathlib import Path
from datetime import datetime

BASE         = Path(r"C:\GitHub-Repositories\Katalog-RSS\Directus-RSS\Товары")
DIRECTUS_DIR = BASE / "Directus-офферы сайта"
OFER_FILE    = BASE / "Офферы - ТОЛЬКО ОПИСАНИЕ И META.md"
LOG_FILE     = BASE / "watcher_log.txt"
SNAPSHOT     = BASE / ".snapshot_count.txt"

SEP  = "=" * 62
SEP2 = "-" * 62

def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def get_md_files():
    if not DIRECTUS_DIR.exists(): return set()
    return set(f.stem for f in DIRECTUS_DIR.glob("*.md"))

def count_big_file(path):
    if not path.exists(): return 0
    text = path.read_text(encoding="utf-8", errors="replace")
    return len([b.strip() for b in re.split(r"\n---\n", text) if b.strip()])

def log(msg):
    print(msg)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(msg + "\n")

def load_snapshot():
    if SNAPSHOT.exists():
        return set(SNAPSHOT.read_text(encoding="utf-8").splitlines())
    return None

def save_snapshot(s):
    SNAPSHOT.write_text("\n".join(sorted(s)), encoding="utf-8")

def print_header(files, n_ofer):
    os.system("cls")
    print(f"\n{SEP}")
    print("  📦 РУССтанкоСбыт — МОНИТОРИНГ КАТАЛОГА  [активен]")
    print(f"  🕐 {now()}")
    print(SEP)
    print(f"\n  ✅ Файлов Directus  : {len(files):>4} шт.")
    print(f"  ✅ Блоков в офферах : {n_ofer:>4} шт.")
    print(f"  ✅ ИТОГО            : {len(files)+n_ofer:>4} шт.")
    print(f"\n{SEP2}")
    print("  🔍 Слежу за изменениями... (Ctrl+C для остановки)")
    print(SEP2)

def main():
    log(f"\n{'#'*62}\n# СТАРТ  {now()}\n{'#'*62}")
    current = get_md_files()
    n_ofer  = count_big_file(OFER_FILE)
    prev    = load_snapshot()
    if prev is None:
        save_snapshot(current)
        log(f"[{now()}] 📸 Первый запуск. Снимок: {len(current)} файлов.")
    else:
        for nm in sorted(current - prev):
            log(f"[{now()}] 🆕 НОВЫЙ с прошлого сеанса: {nm}")
        for nm in sorted(prev - current):
            log(f"[{now()}] 🗑️  УДАЛЁН с прошлого сеанса: {nm}")
        if current == prev:
            log(f"[{now()}] ✔️  Без изменений с прошлого сеанса.")
        save_snapshot(current)

    print_header(current, n_ofer)
    known = current.copy()
    try:
        while True:
            time.sleep(3)
            fresh    = get_md_files()
            new_ofer = count_big_file(OFER_FILE)
            added    = fresh - known
            removed  = known - fresh
            if added or removed:
                print_header(fresh, new_ofer)
                for nm in sorted(added):
                    msg = f"  🆕 [{now()}] ДОБАВЛЕН : {nm}"
                    log(msg); print(msg)
                for nm in sorted(removed):
                    msg = f"  🗑️  [{now()}] УДАЛЁН   : {nm}"
                    log(msg); print(msg)
                save_snapshot(fresh)
                known = fresh
            else:
                sys.stdout.write(
                    f"\r  ⏱  {now()} | Файлов: {len(known)} | "
                    f"Офферов: {new_ofer} | Всего: {len(known)+new_ofer}   "
                )
                sys.stdout.flush()
    except KeyboardInterrupt:
        print(f"\n\n  ⛔ Остановлен: {now()}")
        log(f"[{now()}] ⛔ Остановлен.")

if __name__ == "__main__":
    main()