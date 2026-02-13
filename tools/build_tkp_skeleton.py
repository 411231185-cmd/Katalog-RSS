from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

AUTO_BEGIN = "<!-- AUTO:BEGIN {name} -->"
AUTO_END = "<!-- AUTO:END {name} -->"

UZLY_FILES: List[Tuple[str, str, str]] = [
    ("Фартук.md", "Фартук", "Узел подачи/перемещений, фрикционы, шестерни, валы, механизмы включения."),
    ("Коробка_подач.md", "Коробка подач", "Узел формирования подач/резьб, содержит валы, шестерни, муфты, подшипники."),
    ("Передняя_бабка.md", "Передняя бабка", "Шпиндельный узел: шпиндель, передачи, подшипники, элементы привода."),
    ("Задняя_бабка.md", "Задняя бабка", "Опора детали: пиноль, корпус, фиксаторы, элементы перемещения."),
    ("Суппорт.md", "Суппорт", "Узел резания: салазки, резцедержатель, винты/гайки, направляющие элементы."),
    ("Каретка.md", "Каретка", "Продольное перемещение суппорта: направляющие, механизмы перемещения, элементы фиксации."),
    ("Станина.md", "Станина", "Основание станка: направляющие, выемка (если есть), элементы базирования."),
    ("Электрооборудование.md", "Электрооборудование", "Шкаф/пускатели/датчики/концевики/двигатели; всё, что связано с электрикой."),
    ("Смазка_СОЖ.md", "Смазка и СОЖ", "Насосы, распределители, фильтры, магистрали, системы охлаждения."),
]

KIN1_ORDER = [
    "Передняя_бабка.md",
    "Коробка_подач.md",
    "Фартук.md",
]

KIN2_ORDER = [
    "Суппорт.md",
    "Каретка.md",
    "Задняя_бабка.md",
    "Станина.md",
    "Электрооборудование.md",
    "Смазка_СОЖ.md",
]

CATALOG_LINKS: List[Tuple[str, str]] = [
    ("Шпиндельные бабки", "https://tdrusstankosbyt.ru/shpindelnyibabki"),
    ("Коробки подач", "https://tdrusstankosbyt.ru/korobkipodach"),
    ("Фартуки", "https://tdrusstankosbyt.ru/fartuki"),
    ("Валы", "https://tdrusstankosbyt.ru/valy"),
    ("Винты", "https://tdrusstankosbyt.ru/vinty"),
    ("Шестерни на заказ", "https://tdrusstankosbyt.ru/shesterninazakaz"),
    ("Каретки", "https://tdrusstankosbyt.ru/karetki"),
    ("Суппорты", "https://tdrusstankosbyt.ru/support"),
    ("Кулачки", "https://tdrusstankosbyt.ru/kulachki"),
    ("Резцовые блоки", "https://tdrusstankosbyt.ru/rezcovyblok"),
    ("ШВП", "https://tdrusstankosbyt.ru/shvp"),
    ("Задние бабки", "https://tdrusstankosbyt.ru/zadniibabki"),
    ("Револьверные головки", "https://tdrusstankosbyt.ru/remontrevolvernyhgolovok"),
    ("Комплектующие к узлам", "https://tdrusstankosbyt.ru/komplektujushiekuzlam"),
]

@dataclass
class Report:
    models_total: int = 0
    models_created: int = 0
    models_updated: int = 0
    models_missing_source: int = 0
    files_created: int = 0
    files_updated: int = 0
    warnings: List[str] = None

    def __post_init__(self) -> None:
        if self.warnings is None:
            self.warnings = []

def repo_root_from_script() -> Path:
    # tools/build_tkp_skeleton.py -> repo root is parent of "tools"
    return Path(__file__).resolve().parents[1]

def safe_read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8-sig")

def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")

def slugify_model(name: str) -> str:
    s = name.strip().lower()
    s = s.replace(" ", "")
    s = re.sub(r"[^a-z0-9._-]+", "", s)
    return s

def parse_index_yml(index_path: Path) -> List[str]:
    # Мини-парсер YAML-списка:
    # models:
    #   - 16k20
    #   - 16m30f3
    text = safe_read_text(index_path)
    models: List[str] = []
    for line in text.splitlines():
        m = re.match(r"^\s*-\s*([A-Za-z0-9._-]+)\s*$", line)
        if m:
            models.append(slugify_model(m.group(1)))
    return [m for m in models if m]

def discover_models(machines_dir: Path, tkp_dir: Path) -> List[str]:
    index_yml = tkp_dir / "_index.yml"
    if index_yml.exists():
        models = parse_index_yml(index_yml)
        return sorted(set(models))

    models: List[str] = []
    if not machines_dir.exists():
        return []

    for p in machines_dir.glob("*.md"):
        stem = slugify_model(p.stem)
        if not stem:
            continue
        # фильтр “похоже на модель”: есть цифра
        if re.search(r"\d", stem):
            models.append(stem)

    return sorted(set(models))

def ensure_auto_block(text: str, name: str, block_content: str) -> Tuple[str, bool]:
    begin = AUTO_BEGIN.format(name=name)
    end = AUTO_END.format(name=name)
    pattern = re.compile(re.escape(begin) + r".*?" + re.escape(end), re.DOTALL)
    new_block = f"{begin}\n{block_content.strip()}\n{end}"

    if pattern.search(text):
        # Используем lambda для защиты от ошибок group reference ($1, $2 и т.д.)
        new_text = pattern.sub(lambda _: new_block, text)
        changed = (new_text != text)
        return new_text, changed

    # Если блока нет — добавляем в конец
    new_text = text.rstrip() + f"\n\n{new_block}\n"
    return new_text, True

def extract_section_by_heading(md_text: str, heading_title: str) -> Optional[str]:
    # Ищем заголовок вида "## Технические характеристики" (любой уровень, регистр неважен)
    # Берем текст до следующего заголовка.
    lines = md_text.splitlines()
    heading_re = re.compile(r"^(#{1,6})\s*(.+?)\s*$")

    start_idx = None
    start_level = None

    target = heading_title.strip().lower()

    for i, line in enumerate(lines):
        m = heading_re.match(line)
        if not m:
            continue
        level = len(m.group(1))
        title = m.group(2).strip().lower()
        if title == target:
            start_idx = i + 1
            start_level = level
            break

    if start_idx is None:
        return None

    end_idx = len(lines)
    for j in range(start_idx, len(lines)):
        m = heading_re.match(lines[j])
        if not m:
            continue
        level = len(m.group(1))
        if level <= (start_level or 6):
            end_idx = j
            break

    section_lines = lines[start_idx:end_idx]
    # чистим ведущие пустые строки
    while section_lines and not section_lines[0].strip():
        section_lines.pop(0)
    # и хвост
    while section_lines and not section_lines[-1].strip():
        section_lines.pop()

    section = "\n".join(section_lines).strip()
    return section if section else None

def render_tkp_readme(model: str, source_rel: str, tth_block: str) -> str:
    title = f"# Технико-коммерческое предложение (ТКП) на станок {model.upper()}"
    toc = "\n".join([
        "<a id=\"oglavlenie\"></a>",
        "## Оглавление",
        "- [Описание станка](#opisanie)",
        "- [Назначение и возможности](#naznachenie)",
        "- [Ключевые преимущества](#preim)",
        "- [Области применения](#oblasti)",
        "- [Поставка и сервис](#service)",
        "- [Технические характеристики](#tth)",
        "- [Кинематика — Часть 1](#kin1)",
        "- [Кинематика — Часть 2](#kin2)",
        "- [Раздел 5: Общие запчасти (не в кинематике)](#common)",
        "- [Раздел 6: Ссылки на каталог](#links)",
        "- [Раздел 7: Контактная информация](#contacts)",
    ])

    source_block = "\n".join([
        f"- Источник описания/ТТХ: `{source_rel}`",
        "- Правило: ТТХ только из файла этой модели (не копировать из 1Н65).",
    ])

    links_block = "\n".join([f"- [{name}]({url})" for name, url in CATALOG_LINKS])

    def build_uzel_title_map() -> Dict[str, str]:
        return {fname: title for fname, title, _about in UZLY_FILES}

    def render_kin_links(order: List[str]) -> str:
        title_map = build_uzel_title_map()
        lines = []
        for fname in order:
            title = title_map.get(fname, fname.replace(".md", "").replace("_", " "))
            lines.append(f"- [{title}](./узлы/{fname})")
        return "\n".join(lines)

    base = "\n".join([
        title,
        "",
        "<!-- MANUAL: можно добавлять любые блоки вне AUTO-секций; AUTO-секции перезаписываются скриптом -->",
        "",
        AUTO_BEGIN.format(name="TOC"),
        toc,
        AUTO_END.format(name="TOC"),
        "",
        "<a id=\"opisanie\"></a>",
        "## Описание станка",
        "",
        AUTO_BEGIN.format(name="SOURCE"),
        source_block,
        AUTO_END.format(name="SOURCE"),
        "",
        "TODO: вставить краткое описание (можно сжать текст из источника, без воды).",
        "",
        "<a id=\"naznachenie\"></a>",
        "## Назначение и возможности",
        "",
        "TODO",
        "",
        "<a id=\"preim\"></a>",
        "## Ключевые преимущества",
        "",
        "TODO",
        "",
        "<a id=\"oblasti\"></a>",
        "## Области применения",
        "",
        "TODO",
        "",
        "<a id=\"service\"></a>",
        "## Поставка и сервис",
        "",
        "TODO",
        "",
        "<a id=\"tth\"></a>",
        "## Технические характеристики",
        "",
        AUTO_BEGIN.format(name="TTH"),
        tth_block.strip(),
        AUTO_END.format(name="TTH"),
        "",
        "<a id=\"kin1\"></a>",
        "## Кинематика — Часть 1",
        "",
        AUTO_BEGIN.format(name="KIN1"),
        render_kin_links(KIN1_ORDER),
        AUTO_END.format(name="KIN1"),
        "",
        "TODO: позже добавим схемы/позиции, сейчас это навигационный каркас.",
        "",
        "<a id=\"kin2\"></a>",
        "## Кинематика — Часть 2",
        "",
        AUTO_BEGIN.format(name="KIN2"),
        render_kin_links(KIN2_ORDER),
        AUTO_END.format(name="KIN2"),
        "",
        "TODO: позже добавим схемы/позиции, сейчас это навигационный каркас.",
        "",
        "<a id=\"common\"></a>",
        "## Раздел 5: Общие запчасти (не в кинематике)",
        "",
        "TODO: список категорий/комплектующих + ссылки.",
        "",
        "<a id=\"links\"></a>",
        "## Раздел 6: Ссылки на каталог",
        "",
        links_block,
        "",
        "<a id=\"contacts\"></a>",
        "## Раздел 7: Контактная информация",
        "",
        "TODO: телефон, email, адрес, график.",
        "",
    ])
    return base

def render_uzel_md(model: str, uzel_title: str, uzel_about: str) -> str:
    links = "\n".join([f"- [{name}]({url})" for name, url in CATALOG_LINKS])

    return "\n".join([
        f"# {uzel_title} — {model.upper()}",
        "",
        "<a id=\"top\"></a>",
        "## Коротко об узле",
        "",
        f"{uzel_about}",
        "",
        "## Что делаем по узлу",
        "",
        "- Подбор/поставка узла в сборе (если применимо).",
        "- Подбор/поставка деталей узла (по чертежу/обозначению/фото).",
        "- Восстановление/изготовление (если применимо).",
        "",
        "## Быстрые ссылки (перелинковка)",
        "",
        links,
        "",
        "## Файлы в репозитории по теме",
        "",
        "- TODO: добавить ссылки на релевантные файлы в `docs/` (комплектующие/запчасти/инструкции/паспорт).",
        "",
        "## Посадочные страницы (Tilda)",
        "",
        "- TODO: ссылка на посадочную узла (если будет).",
        "- TODO: ссылки на детали/комплектующие (если будут).",
        "",
        "[↑ к началу](#top)",
        "",
    ])

def ensure_template_files(tkp_dir: Path) -> None:
    tpl_dir = tkp_dir / "_TEMPLATE"
    tpl_dir.mkdir(parents=True, exist_ok=True)

    tkp_tpl = tpl_dir / "ТКП-ШАБЛОН.md"
    if not tkp_tpl.exists():
        write_text(tkp_tpl, "\n".join([
            "# ТКП-ШАБЛОН",
            "",
            "Этот файл — ориентир структуры (как у 1Н65): якоря фиксированные, оглавление кликабельное.",
            "Скрипт генерирует README.md для каждой модели по этой структуре.",
            "",
        ]))

    uzel_tpl = tpl_dir / "УЗЕЛ-ШАБЛОН.md"
    if not uzel_tpl.exists():
        write_text(uzel_tpl, "\n".join([
            "# УЗЕЛ-ШАБЛОН",
            "",
            "Рекомендуемая структура мини-ТКП узла (используется скриптом при создании файлов узлов).",
            "",
            "## Коротко об узле",
            "TODO",
            "",
            "## Быстрые ссылки (перелинковка)",
            "TODO",
            "",
            "## Файлы в репозитории по теме",
            "- TODO",
            "",
            "## Посадочные страницы (Tilda)",
            "- TODO",
            "",
        ]))

def build_index_readme(tkp_dir: Path, models: List[str]) -> str:
    lines = [
        "# ТКП — индекс",
        "",
        "## Станки",
    ]
    for m in models:
        lines.append(f"- [{m}](./{m}/README.md)")
    lines.append("")
    return "\n".join(lines)

def main() -> int:
    repo_root = repo_root_from_script()
    docs_dir = repo_root / "docs"
    tkp_dir = docs_dir / "ТКП"
    machines_dir = docs_dir / "Станки"

    if not tkp_dir.exists():
        print(f"ERROR: не найдена папка {tkp_dir}")
        return 2

    ensure_template_files(tkp_dir)

    models = discover_models(machines_dir, tkp_dir)
    report = Report(models_total=len(models))

    if not models:
        print("WARNING: модели не найдены. Проверь docs/Станки/*.md или создай docs/ТКП/_index.yml")
        return 1

    # индексный README
    index_readme = tkp_dir / "README.md"
    index_content = build_index_readme(tkp_dir, models)
    if index_readme.exists():
        old = safe_read_text(index_readme)
        if old != index_content:
            write_text(index_readme, index_content)
            report.files_updated += 1
    else:
        write_text(index_readme, index_content)
        report.files_created += 1

    for model in models:
        model_dir = tkp_dir / model
        uzly_dir = model_dir / "узлы"
        uzly_dir.mkdir(parents=True, exist_ok=True)

        src_md = machines_dir / f"{model}.md"
        source_rel = str(Path("..") / ".." / "Станки" / f"{model}.md")  # из docs/ТКП/<model>/README.md

        tth_block = "TODO: ТТХ не найдено в источнике."
        if src_md.exists():
            md = safe_read_text(src_md)
            extracted = extract_section_by_heading(md, "Технические характеристики")
            if extracted:
                tth_block = extracted
            else:
                tth_block = "TODO: ТТХ не найдено в источнике (нет заголовка «Технические характеристики»)."
        else:
            report.models_missing_source += 1
            report.warnings.append(f"{model}: нет источника {src_md}")

        readme_path = model_dir / "README.md"
        generated = render_tkp_readme(model=model, source_rel=source_rel, tth_block=tth_block)

        if readme_path.exists():
            old = safe_read_text(readme_path)

            # Обновляем только AUTO-блоки, если пользователь уже вносил правки
            new = old

            # TOC
            toc_content = re.search(
                re.escape(AUTO_BEGIN.format(name="TOC")) + r"(.*?)" + re.escape(AUTO_END.format(name="TOC")),
                generated,
                flags=re.DOTALL
            )
            if toc_content:
                new, ch1 = ensure_auto_block(new, "TOC", toc_content.group(1).strip())

            # SOURCE
            src_content = re.search(
                re.escape(AUTO_BEGIN.format(name="SOURCE")) + r"(.*?)" + re.escape(AUTO_END.format(name="SOURCE")),
                generated,
                flags=re.DOTALL
            )
            if src_content:
                new, ch2 = ensure_auto_block(new, "SOURCE", src_content.group(1).strip())

            # TTH
            tth_content = re.search(
                re.escape(AUTO_BEGIN.format(name="TTH")) + r"(.*?)" + re.escape(AUTO_END.format(name="TTH")),
                generated,
                flags=re.DOTALL
            )
            if tth_content:
                new, ch3 = ensure_auto_block(new, "TTH", tth_content.group(1).strip())
            else:
                ch3 = False

            # KIN1
            kin1_content = re.search(
                re.escape(AUTO_BEGIN.format(name="KIN1")) + r"(.*?)" + re.escape(AUTO_END.format(name="KIN1")),
                generated,
                flags=re.DOTALL
            )
            if kin1_content:
                new, _ = ensure_auto_block(new, "KIN1", kin1_content.group(1).strip())

            # KIN2
            kin2_content = re.search(
                re.escape(AUTO_BEGIN.format(name="KIN2")) + r"(.*?)" + re.escape(AUTO_END.format(name="KIN2")),
                generated,
                flags=re.DOTALL
            )
            if kin2_content:
                new, _ = ensure_auto_block(new, "KIN2", kin2_content.group(1).strip())

            if new != old:
                write_text(readme_path, new)
                report.models_updated += 1
                report.files_updated += 1
        else:
            write_text(readme_path, generated)
            report.models_created += 1
            report.files_created += 1

        # узлы
        for fname, title, about in UZLY_FILES:
            p = uzly_dir / fname
            if p.exists():
                continue
            write_text(p, render_uzel_md(model=model, uzel_title=title, uzel_about=about))
            report.files_created += 1

    print("=== build_tkp_skeleton report ===")
    print(f"Models total: {report.models_total}")
    print(f"Models created: {report.models_created}")
    print(f"Models updated: {report.models_updated}")
    print(f"Models missing source in docs/Станки: {report.models_missing_source}")
    print(f"Files created: {report.files_created}")
    print(f"Files updated: {report.files_updated}")
    if report.warnings:
        print("Warnings:")
        for w in report.warnings:
            print(f"- {w}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
