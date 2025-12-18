-- 🗄️ SQL СКРИПТ ДЛЯ ВСТАВКИ UID/SKU В БАЗУ ДАННЫХ
-- Совместим с: MySQL, PostgreSQL, SQLite, SQL Server

-- ============================================================================
-- ВАРИАНТ 1: SQLite (Рекомендуется для простоты)
-- ============================================================================

-- Создание таблицы (если её нет)
CREATE TABLE IF NOT EXISTS catalog_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    uid TEXT UNIQUE NOT NULL,
    sku TEXT UNIQUE NOT NULL,
    category TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Создание индексов для быстрого поиска
CREATE INDEX IF NOT EXISTS idx_uid ON catalog_items(uid);
CREATE INDEX IF NOT EXISTS idx_sku ON catalog_items(sku);
CREATE INDEX IF NOT EXISTS idx_category ON catalog_items(category);

-- Вставка данных (при конфликте обновить существующую запись)
INSERT INTO catalog_items (uid, sku, category) 
VALUES 
('ITEM.Барабан - копир на фартук станка 16К20', 'Барабан - копир на фартук станка 16К20', 'ITEM'),
('KOLZUB.1М63Б_60_281', '1М63Б_60_281', 'KOLZUB'),
('ITEM.Блок-шестерни 28/49 консольно-фрезерных станков мо', 'Блок-шестерни 28/49 консольно-фрезерных станков мо', 'ITEM'),
('VAL.VS-1K62', 'VS-1K62', 'VAL'),
('KOLZUB.РТ502_33_152', 'РТ502_33_152', 'KOLZUB'),
('STANOK.16K20', '16K20', 'STANOK'),
('STANOK.16R25', '16R25', 'STANOK'),
('STANOK.1M63N', '1M63N', 'STANOK'),
('STANOK.1N65', '1N65', 'STANOK'),
('STANOK.16K40', '16K40', 'STANOK'),
('STANOK.16M30F3', '16M30F3', 'STANOK'),
('STANOK.RT117', 'RT117', 'STANOK'),
('STANOK.RT817', 'RT817', 'STANOK'),
('STANOK.RT755F3', 'RT755F3', 'STANOK'),
('STANOK.RT305M', 'RT305M', 'STANOK'),
('STANOK.16A20F3', '16A20F3', 'STANOK'),
('STANOK.RT779F3', 'RT779F3', 'STANOK'),
('STANOK.RT301', 'RT301', 'STANOK'),
('STANOK.RT301.01', 'RT301.01', 'STANOK'),
('STANOK.RT301.02', 'RT301.02', 'STANOK'),
('STANOK.RT5001', 'RT5001', 'STANOK'),
('STANOK.RT5003', 'RT5003', 'STANOK'),
('STANOK.RT5004', 'RT5004', 'STANOK'),
('STANOK.RT91', 'RT91', 'STANOK')
ON CONFLICT(uid) DO UPDATE SET 
    sku=excluded.sku, 
    category=excluded.category,
    updated_at=CURRENT_TIMESTAMP;

-- Проверка результатов
SELECT COUNT(*) as total_items FROM catalog_items;
SELECT category, COUNT(*) as count FROM catalog_items GROUP BY category ORDER BY count DESC;

-- ============================================================================
-- ВАРИАНТ 2: MySQL
-- ============================================================================

-- Создание таблицы
CREATE TABLE IF NOT EXISTS catalog_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    uid VARCHAR(255) UNIQUE NOT NULL,
    sku VARCHAR(255) UNIQUE NOT NULL,
    category VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_uid (uid),
    INDEX idx_sku (sku),
    INDEX idx_category (category)
) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Вставка данных
INSERT INTO catalog_items (uid, sku, category) VALUES 
('STANOK.16K20', '16K20', 'STANOK'),
('STANOK.16R25', '16R25', 'STANOK'),
('STANOK.1M63N', '1M63N', 'STANOK'),
('STANOK.1N65', '1N65', 'STANOK')
ON DUPLICATE KEY UPDATE 
    sku=VALUES(sku),
    category=VALUES(category),
    updated_at=CURRENT_TIMESTAMP;

-- ============================================================================
-- ВАРИАНТ 3: PostgreSQL
-- ============================================================================

-- Создание таблицы
CREATE TABLE IF NOT EXISTS catalog_items (
    id SERIAL PRIMARY KEY,
    uid TEXT UNIQUE NOT NULL,
    sku TEXT UNIQUE NOT NULL,
    category VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Создание индексов
CREATE INDEX IF NOT EXISTS idx_uid ON catalog_items(uid);
CREATE INDEX IF NOT EXISTS idx_sku ON catalog_items(sku);
CREATE INDEX IF NOT EXISTS idx_category ON catalog_items(category);

-- Вставка данных (upsert)
INSERT INTO catalog_items (uid, sku, category) VALUES 
('STANOK.16K20', '16K20', 'STANOK'),
('STANOK.16R25', '16R25', 'STANOK'),
('STANOK.1M63N', '1M63N', 'STANOK')
ON CONFLICT(uid) DO UPDATE SET 
    sku=EXCLUDED.sku,
    category=EXCLUDED.category,
    updated_at=CURRENT_TIMESTAMP;

-- ============================================================================
-- ПОЛЕЗНЫЕ ЗАПРОСЫ
-- ============================================================================

-- Поиск по UID
SELECT * FROM catalog_items WHERE uid LIKE '%STANOK%';

-- Поиск по SKU
SELECT * FROM catalog_items WHERE sku = '16K20';

-- Статистика по категориям
SELECT category, COUNT(*) as count 
FROM catalog_items 
GROUP BY category 
ORDER BY count DESC;

-- Проверка дубликатов
SELECT sku, COUNT(*) as count 
FROM catalog_items 
GROUP BY sku 
HAVING COUNT(*) > 1;

-- Экспорт в CSV
SELECT uid, sku FROM catalog_items ORDER BY uid;

-- Удаление по категории
DELETE FROM catalog_items WHERE category = 'ITEM';

-- Обновление категории
UPDATE catalog_items SET category = 'SHESTER' WHERE uid LIKE 'SHESTER.%';

-- Очистка старых данных (старше 30 дней)
DELETE FROM catalog_items WHERE updated_at < DATE_SUB(NOW(), INTERVAL 30 DAY);
