# Папка Exel-Claude

Рабочее пространство для совместной работы с Claude в Excel по каталогам (1bm.ru; Бизнес онлайн (bizon.ru); ВсеСтанки (vsestankirf.ru); ЕПМ (portalmetalloobrabotki.ru); ИнтехСервис; КООП Платформа-Яндекс (platforma.coop-tech.ru); МашПорт.ру (mashport.ru); МетаПром (metaprom.ru); МЕХАНИЗАЦИЯ (mechanization.ru); МирПром (mirprom.com); Москва Ouuuu (moskva.ouuo.ru); Моя ЖД (myrailway.ru); Нефтегаз (neftegaz.ru, neftgaz-company.ru); Оборудуй (oboruduy.com); ПромИндекс (promindex.ru, my.promindex.ru); Промоборудование (промоборудование.рф); ПромПортал-2 (promportal.pro); РОСТИП (rosstip.ru); Сделано у НАС (sdelanounas.ru); СПР (spr.ru); ТенЧат; Яндекс-исполнитель (uslugi.yandex.ru); Яндекс.Директ (direct.yandex.ru); BIG-BOOK-CITY.RU (big-book-city.ru); BIZLY.RU (bizly.ru); Cataloxy (cataloxy.ru); EQUIPNET (equipnet.ru); Fabricators (fabricators.ru); firmap.ru; IsFirm (isfirm.ru); JSprav (jsprav.ru); LiveJournal (livejournal.com); Machinebook (machinebook.ru); metaltorg (metaltorg.ru); moskva.yacatalog.com; msk.spravker.ru; neftgaz-company.ru; PolskiPro (poiski.pro); PROСтанки (prostanki.com); prom-market.com; promplace (promplace.ru); PromPortal (promportal.su); promPR (prompr.ru); ProPartner (propartner.ru); RegTorg (regtorg.ru); S2s (s2s.ru); SOVOK.RU (sovok.ru); spravokno.ru; Stanoktrading (stanok-trading.ru); SteelLand.Ru (steelland.ru); X-Tool (xtool.ru); YP.RU (yp.ru); Zoon (zoon.ru). Directus).

## Структура

- `prompts/` — промты и SKILL-описания для Клода.
- `templates/` — Excel-шаблоны батчей (формат входных данных для ИИ).
- `batches/` — реальные батчи (подмножества строк из каталогов) для обработки.
- `scripts/` — Python-скрипты для слияния результатов, добавления перелинковки и др.
- `logs/` — выгруженные CSV/результаты от Клода для истории и отладки.

## Базовый workflow для PromPortal

1. Берём исходный файл `PLOSIADKI-RSS/PromPortal/PromPortal-РОВНЫЙ copy.xlsx`.
2. Формируем батч (20–50 строк) и сохраняем в `Exel-Claude\\batches\\promportal_batch_XXX.xlsx` по шаблону `templates/batch_template.xlsx`.
3. В Excel + Claude:
   - открываем батч;
   - вызываем скилл `/catalog-descriptions-xls` (описан в `prompts/PromPortal-SKILL.md`);
   - получаем колонки `new_description_top`, `quality_flag` для этих строк.
4. Сохраняем результат батча.
5. Скриптом `scripts/merge_descriptions.py`:
   - сливаем все обработанные батчи в основной файл;
   - добавляем блок перелинковки;
   - сохраняем финальный `PromPortal-FINAL-with-descriptions-v2.xlsx`.
