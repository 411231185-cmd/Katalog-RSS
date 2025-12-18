# 🔧 СКРИПТ ИНТЕГРАЦИИ UID/SKU В КАТАЛОГ СТАНКОАРТЕЛЬ
# Путь к файлу: C:\Users\User\Dropbox\ООО РУССтанкоСБыт\ПРАЙСЫ РСС\UIDSKU_ABSOLUT_FINAL.csv

import csv
import os
from datetime import datetime
from pathlib import Path

# ============================================================================
# КОНФИГУРАЦИЯ
# ============================================================================

CSV_SOURCE = r"C:\Users\User\Dropbox\ООО РУССтанкоСБыт\ПРАЙСЫ РСС\UIDSKU_ABSOLUT_FINAL.csv"
DATABASE_PATH = r"C:\Users\User\[YOUR_DATABASE_PATH]"  # Укажи свой путь
BACKUP_FOLDER = r"C:\Users\User\Dropbox\ООО РУССтанкоСБыт\BACKUP"
LOG_FILE = "integration_log.txt"

# ============================================================================
# ФУНКЦИИ ИНТЕГРАЦИИ
# ============================================================================

def create_backup(db_path):
    """Создаёт резервную копию перед интеграцией"""
    backup_path = os.path.join(
        BACKUP_FOLDER, 
        f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    )
    
    if os.path.exists(db_path):
        os.makedirs(BACKUP_FOLDER, exist_ok=True)
        with open(db_path, 'r', encoding='utf-8') as src:
            with open(backup_path, 'w', encoding='utf-8') as dst:
                dst.write(src.read())
        return backup_path
    return None

def read_csv_data(csv_path):
    """Читает CSV файл с UID и SKU"""
    data = {}
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter=';')
            for row in reader:
                uid = row.get('UID', '').strip()
                sku = row.get('SKU', '').strip()
                if uid and sku:
                    data[sku] = uid
        return data
    except Exception as e:
        print(f"❌ ОШИБКА чтения CSV: {e}")
        return None

def merge_with_database(csv_data, db_path):
    """Объединяет CSV данные с существующей БД"""
    merged = []
    updated_count = 0
    new_count = 0
    
    # Если БД существует, читаем её
    existing = {}
    if os.path.exists(db_path):
        with open(db_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter=';')
            for row in reader:
                existing[row.get('SKU', '')] = row
    
    # Объединяем данные
    for sku, uid in csv_data.items():
        if sku in existing:
            existing[sku]['UID'] = uid
            updated_count += 1
        else:
            merged.append({'UID': uid, 'SKU': sku})
            new_count += 1
    
    # Добавляем существующие записи
    for sku, row in existing.items():
        merged.append(row)
    
    return merged, updated_count, new_count

def write_database(data, db_path):
    """Записывает данные в БД"""
    try:
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        with open(db_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['UID', 'SKU'], delimiter=';')
            writer.writeheader()
            writer.writerows(data)
        return True
    except Exception as e:
        print(f"❌ ОШИБКА записи БД: {e}")
        return False

def log_action(message):
    """Логирует действие"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_msg = f"[{timestamp}] {message}"
    print(log_msg)
    
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(log_msg + '\n')

# ============================================================================
# ОСНОВНОЙ ПРОЦЕСС
# ============================================================================

def main():
    print("=" * 80)
    print("🚀 ИНТЕГРАЦИЯ UID/SKU В КАТАЛОГ СТАНКОАРТЕЛЬ")
    print("=" * 80)
    
    # 1. Проверяем файл источника
    if not os.path.exists(CSV_SOURCE):
        log_action(f"❌ ОШИБКА: Файл не найден - {CSV_SOURCE}")
        return
    
    log_action(f"✅ Источник найден: {CSV_SOURCE}")
    
    # 2. Читаем CSV данные
    csv_data = read_csv_data(CSV_SOURCE)
    if not csv_data:
        log_action("❌ Не удалось прочитать CSV данные")
        return
    
    log_action(f"✅ Загружено {len(csv_data)} артикулов из CSV")
    
    # 3. Создаём резервную копию
    backup_path = create_backup(DATABASE_PATH)
    if backup_path:
        log_action(f"✅ Резервная копия создана: {backup_path}")
    
    # 4. Объединяем с БД
    merged_data, updated, new = merge_with_database(csv_data, DATABASE_PATH)
    log_action(f"✅ Объединение завершено:")
    log_action(f"   • Обновлено: {updated}")
    log_action(f"   • Новых: {new}")
    log_action(f"   • Всего: {len(merged_data)}")
    
    # 5. Записываем результат
    if write_database(merged_data, DATABASE_PATH):
        log_action(f"✅ УСПЕШНО: Данные записаны в {DATABASE_PATH}")
        
        # Статистика
        categories = {}
        for row in merged_data:
            cat = row['UID'].split('.')[0] if '.' in row['UID'] else 'UNKNOWN'
            categories[cat] = categories.get(cat, 0) + 1
        
        log_action("📊 Статистика по категориям:")
        for cat, count in sorted(categories.items()):
            log_action(f"   {cat:20} → {count:3} шт.")
    else:
        log_action("❌ Ошибка при записи данных")
        return
    
    print("=" * 80)
    log_action("✨ ИНТЕГРАЦИЯ ЗАВЕРШЕНА УСПЕШНО!")
    print("=" * 80)

if __name__ == "__main__":
    main()
