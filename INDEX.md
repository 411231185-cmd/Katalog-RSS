# 📋 Katalog-RSS — Навигация

> Каталог запчастей для токарных станков РУССтанкоСбыт

---

## 🎯 Быстрый старт

| Что нужно | Куда идти |
|-----------|-----------|
| **Мастер-каталог** | `MASTER_CATALOG_RSS.csv` |
| **Готово для Tilda** | `catalogs/FINAL_TILDA_CATALOG.csv` |
| **ТКП всех офферов** | `ТКП всех офферов.txt` |

---

## 🗂️ Структура

```
Katalog-RSS/
├── 📄 МАСТЕР-ФАЙЛЫ
│   ├── MASTER_CATALOG_RSS.csv           # Главный каталог
│   ├── MASTER_CATALOG_WITH_DESCRIPTIONS.csv
│   └── MASTER_CATALOG_CLEANED.csv
│
├── 📁 catalogs/                         # Каталоги и экспорты
│   ├── yml/                             # YML для Яндекс.Маркет
│   ├── csv/                             # CSV экспорты
│   └── FINAL_TILDA_CATALOG.csv          # Готово для Tilda
│
├── 📁 scripts/                          # Python скрипты
│   ├── seo_optimizer.py                 # SEO оптимизация
│   ├── tilda_upload.py                  # Загрузка в Tilda
│   └── ...
│
├── 📁 descriptions/                     # Описания товаров
├── 📁 ТКП/                              # Технико-коммерческие предложения
├── 📁 Kinematika-Chertegi/              # Чертежи кинематики
├── 📁 slovari/                          # Словари и справочники
│
└── 📄 ОФФЕРЫ (MD файлы)                 # 80+ описаний товаров
    ├── Револьверные головки.md
    ├── Шпиндельные бабки.md
    ├── Фартуки токарных станков.md
    └── ...
```

---

## 📊 Ключевые CSV

| Файл | Записей | Назначение |
|------|---------|------------|
| `MASTER_CATALOG_RSS.csv` | 500+ | Главный каталог |
| `OFFERS_FILLED.csv` | 400+ | Офферы с описаниями |
| `catalogs/FINAL_TILDA_CATALOG.csv` | 400+ | Импорт в Tilda |

---

## 🛠️ Скрипты

### Работа с каталогом
- `clean_master.py` — Очистка мастер-каталога
- `add_html_links_to_catalog.py` — Добавление HTML-ссылок
- `optimize_catalog.py` — Оптимизация каталога

### Парсинг и описания
- `parse_websites_fill_descriptions.py` — Парсинг с сайтов
- `fill_descriptions_from_text.py` — Заполнение описаний
- `enrich_text_from_competitors.py` — Обогащение из конкурентов

### Tilda интеграция
- `scripts/tilda_upload.py` — Загрузка в Tilda
- `scripts/uploadcare_upload.py` — Загрузка фото

---

## 📦 Категории товаров

- Револьверные головки
- Шпиндельные бабки
- Фартуки токарных станков
- Суппорты и каретки
- ШВП (шарико-винтовые пары)
- Патроны токарные
- Шестерни и зубчатые колеса
- Электрооборудование

---

## 🔗 Связанные репозитории

| Репо | Связь |
|------|-------|
| SAYT-RSS | Сайт tdrusstankosbyt.ru |
| YANDEX-DIRECT | Рекламные кампании |
| TSO-RSS-1 | Проект ТСО |

---

*Обновлено: 04.02.2026*
