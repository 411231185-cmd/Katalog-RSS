from pathlib import Path

# ПРАВИЛЬНЫЕ ПУТИ ПОД ТВОЮ СХЕМУ
BASE = Path(r"C:\GitHub-Repositories\Katalog-RSS\docs\PLOSIADKI-RSS\МашПорт")
input_file = BASE / "НЕ ХВАТАЕТ.md"
tkp_dir = BASE / "ТКП-отдельные"
output_file = BASE / "НЕ ХВАТАЕТ copy.md"

def make_filename_from_line(line: str) -> str:
    # Берём "название позиции" до двух пробелов подряд или до сильного обрезания описания
    # На практике: берём всё до первого двухпробельного разрыва или до 120 символов
    core = line.strip()
    if "  " in core:
        core = core.split("  ", 1)[0]
    # если строка очень длинная, чуть обрежем
    if len(core) > 120:
        core = core[:120]

    # Имя файла: пробелы -> "_", остальное оставляем как есть
    filename = core.replace(" ", "_") + ".md"
    return filename

def is_file_nonempty(path: Path) -> bool:
    return path.exists() and path.is_file() and path.stat().st_size > 0

def main():
    if not input_file.exists():
        print(f"Не найден входной файл: {input_file}")
        return
    if not tkp_dir.exists():
        print(f"Не найдена папка с ТКП: {tkp_dir}")
        return

    not_done_lines = []

    with input_file.open("r", encoding="utf-8") as f:
        for line in f:
            stripped = line.strip()
            if not stripped:
                continue  # пропускаем пустые строки

            filename = make_filename_from_line(stripped)
            tkp_path = tkp_dir / filename

            if not is_file_nonempty(tkp_path):
                # файла нет или он пустой -> считаем "НЕ сделано"
                not_done_lines.append(line.rstrip("\n"))

    # пишем результат
    with output_file.open("w", encoding="utf-8") as out:
        for l in not_done_lines:
            out.write(l + "\n")

    print(f"Готово. В файл '{output_file}' записано {len(not_done_lines)} строк, которые ещё НЕ сделаны.")

if __name__ == "__main__":
    main()