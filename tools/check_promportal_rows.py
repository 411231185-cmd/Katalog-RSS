import html
import re
from pathlib import Path

import pandas as pd


PROMPORTAL_FINAL = Path(
    r"C:\GitHub-Repositories\Katalog-RSS\PLOSIADKI-RSS\PromPortal\Каталоги\PromPortal-FINAL-with-descriptions.xlsx"
)
PROMPORTAL_ROVNIY = Path(
    r"C:\GitHub-Repositories\Katalog-RSS\PLOSIADKI-RSS\PromPortal\PromPortal-РОВНЫЙ.xlsx"
)
PROMPORTAL_SHIFRY_NEW = Path(
    r"C:\GitHub-Repositories\Katalog-RSS\PLOSIADKI-RSS\PromPortal\PromPortal+шифры-NEW.xlsx"
)
OLD_EXPORT = Path(
    r"C:\GitHub-Repositories\Katalog-RSS\PLOSIADKI-RSS\PromPortal\Каталоги\export от Кристины.xlsx"
)
DIRECTUS_CSV = Path(
    r"C:\GitHub-Repositories\Katalog-RSS\Directus-RSS\Directus-Catalog-Actuality.csv"
)
DESCRIPTION_CSV = Path(
    r"C:\GitHub-Repositories\Katalog-RSS\PLOSIADKI-RSS\PromPortal\Каталоги\description_new_full.csv"
)

ALL_PATHS = [
    PROMPORTAL_FINAL,
    PROMPORTAL_ROVNIY,
    PROMPORTAL_SHIFRY_NEW,
    OLD_EXPORT,
    DIRECTUS_CSV,
    DESCRIPTION_CSV,
]

KEY_CANDIDATES = [
    "row",
    "Row",
    "ROW",
    "id",
    "ID",
    "Id",
    "offer_id",
    "OfferID",
    "uuid",
    "UID",
    "uid",
    "sku",
    "SKU",
    "title",
    "Title",
    "name",
    "Name",
]

CODE_COLUMN_CANDIDATES = [
    "Код",
    "код",
    "Артикул",
    "артикул",
    "SKU",
    "sku",
    "Vendor code",
    "vendor_code",
    "Код товара",
    "Наименование 1С",
]
NAME_COLUMN_CANDIDATES = [
    "Наименование",
    "наименование",
    "Title",
    "title",
    "name",
    "Name",
    "Название",
    "Номенклатура",
]
DESCRIPTION_COLUMN_CANDIDATES = [
    "description_new",
    "Description",
    "description",
    "Описание",
    "Текст",
    "text",
]

SERVICE_BLOCK = (
    "Подобрать конкретную запчасть вы можете у нас на сайте в разделе Каталог ТД РУССтанкоСбыт.\n"
    "Поставка и изготовление ПАТРОНОВ для станков — токарные и специальные патроны.\n"
    "Поставка ПОДШИПНИКОВ для станков — шариковые, роликовые и упорные подшипники.\n"
    "Поставка и изготовление ЦЕНТРОВ для токарных станков — центры с конусом Морзе.\n"
    "Изготовление СУППОРТОВ для токарных станков — суппорты в сборе под заказ.\n"
    "Изготовление ПЛАНШАЙБ для токарных станков — планшайбы под заказ.\n"
    "Изготовление ШВП для станков — шарико‑винтовые пары под заказ.\n"
    "Изготовление ВИНТОВ для станков — ходовые винты, винты подачи и специальные винты под заказ.\n"
    "Изготовление ВАЛОВ для станков — вал‑шестерни, шлицевые и приводные валы под заказ.\n"
    "Изготовление ВТУЛОК для станков — переходные, опорные и направляющие втулки под заказ.\n"
    "Изготовление ШЕСТЕРЁН для станков — зубчатые колёса и шестерни под заказ.\n"
    "Изготовление ЛЮНЕТОВ для токарных станков — неподвижные и подвижные люнеты под заказ.\n"
    "Изготовление ЗАЩИТНЫХ КОЖУХОВ для станков любой сложности.\n"
    "Изготовление КАБИНЕТНЫХ ЗАЩИТ для станков любой сложности.\n"
    "Изготовление ВКЛАДЫШЕЙ и ЗАХВАТОВ для станков — оснастка под заказ."
)

BRAND_PATTERNS = [
    (re.compile(r"\btd\s*russtankosbyt\b", flags=re.IGNORECASE), "ТД РУССтанкоСбыт"),
    (re.compile(r"\bтд\s*русстанкосбыт\b", flags=re.IGNORECASE), "ТД РУССтанкоСбыт"),
    (re.compile(r"\brusstanko[-\s]?rzn\b", flags=re.IGNORECASE), "производитель"),
    (re.compile(r"\brosstanko\b", flags=re.IGNORECASE), "производитель"),
    (re.compile(r"\bstankilife\b", flags=re.IGNORECASE), "производитель"),
    (re.compile(r"\bkpsk\b", flags=re.IGNORECASE), "производитель"),
    (re.compile(r"\bvse-k-stankam\b", flags=re.IGNORECASE), "производитель"),
    (re.compile(r"\btdrusstankosbyt\b", flags=re.IGNORECASE), "ТД РУССтанкоСбыт"),
    (re.compile(r"\bооо\b[^.\n,;:]{0,40}", flags=re.IGNORECASE), "производитель"),
    (re.compile(r"\bзао\b[^.\n,;:]{0,40}", flags=re.IGNORECASE), "производитель"),
    (re.compile(r"\bao\b[^.\n,;:]{0,40}", flags=re.IGNORECASE), "производитель"),
    (re.compile(r"\bип\b[^.\n,;:]{0,40}", flags=re.IGNORECASE), "производитель"),
]

DETAIL_TYPE_PATTERNS = [
    ("вал-шестерня", "вал-шестерня"),
    ("вал шестерня", "вал-шестерня"),
    ("шестерня-вал", "вал-шестерня"),
    ("шестерня вал", "вал-шестерня"),
    ("колесо зубчат", "колесо зубчатое"),
    ("шестерн", "шестерня"),
    ("колесо червяч", "колесо червячное"),
    ("червяк", "червячный вал"),
    ("гайка", "гайка"),
    ("винт", "винт"),
    ("швп", "ШВП"),
    ("втулк", "втулка"),
    ("муфт", "муфта"),
    ("люнет", "люнет"),
    ("суппорт", "суппорт"),
    ("фартук", "фартук"),
    ("коробка подач", "коробка подач"),
    ("коробка скорост", "коробка скоростей"),
    ("шпиндел", "шпиндельный узел"),
    ("патрон", "патрон"),
    ("планшайб", "планшайба"),
    ("центр", "центр"),
    ("подшип", "подшипник"),
    ("рейка", "рейка"),
    ("вкладыш", "вкладыш"),
    ("захват", "захват"),
]

MACHINE_PATTERNS = re.compile(
    r"\b(?:1[мнmнhн][0-9]{2}[а-яa-z0-9\-]*|16[кkрpm][0-9]{2}[а-яa-z0-9\-]*|"
    r"6[рpнhмm][0-9]{2}[а-яa-z0-9\-]*|дип\s*[- ]?(?:300|500)|165|1м65|1н65|1м63|16к40|16к20|"
    r"рт\s*[- ]?\d+[а-яa-z0-9\-]*|fss\s*400|уг\d+[.\d]*|ир\d+[а-яa-z0-9\-]*)\b",
    flags=re.IGNORECASE,
)


def detect_join_key(final_df: pd.DataFrame, descriptions_df: pd.DataFrame) -> str:
    for column in KEY_CANDIDATES:
        if column in final_df.columns and column in descriptions_df.columns:
            return column

    common_columns = [column for column in final_df.columns if column in descriptions_df.columns]
    if common_columns:
        return common_columns[0]

    raise ValueError(
        "Не найден общий столбец для сопоставления строк между Excel и CSV."
    )


def normalize_key_series(series: pd.Series) -> pd.Series:
    return (
        series.astype("string")
        .fillna("")
        .str.strip()
        .str.replace(r"\s+", " ", regex=True)
        .str.lower()
    )


def normalize_text(value: object) -> str:
    if value is None or pd.isna(value):
        return ""
    return str(value).strip()


def normalize_code(value: object) -> str:
    text = normalize_text(value).upper()
    text = text.replace("Ё", "Е")
    text = re.sub(r"[\s_/\\\-]+", "", text)
    return text


def normalize_name(value: object) -> str:
    text = normalize_text(value).lower().replace("ё", "е")
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"[^a-zа-я0-9\s.-]+", " ", text, flags=re.IGNORECASE)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def find_column(df: pd.DataFrame, candidates: list[str]) -> str | None:
    lowered = {str(col).strip().lower(): col for col in df.columns}
    for candidate in candidates:
        found = lowered.get(candidate.strip().lower())
        if found is not None:
            return found

    for col in df.columns:
        col_l = str(col).strip().lower()
        for candidate in candidates:
            if candidate.strip().lower() in col_l:
                return col
    return None


def load_table(path: Path) -> pd.DataFrame:
    if path.suffix.lower() == ".csv":
        try:
            return pd.read_csv(path)
        except UnicodeDecodeError:
            return pd.read_csv(path, encoding="cp1251")
    return pd.read_excel(path, engine="openpyxl")


def collect_text_parts(record: dict[str, str]) -> list[str]:
    parts = []
    for value in record.values():
        text = normalize_text(value)
        if text:
            parts.append(text)
    return parts


def detect_detail_type(text: str) -> str:
    text_l = normalize_name(text)
    for needle, label in DETAIL_TYPE_PATTERNS:
        if needle in text_l:
            return label
    return "деталь"


def extract_machine_models(text: str) -> list[str]:
    found = MACHINE_PATTERNS.findall(text.replace("РТ", "рт").replace("RT", "рт"))
    unique = []
    seen = set()
    for item in found:
        cleaned = re.sub(r"\s+", "", item.upper().replace("Ё", "Е"))
        cleaned = cleaned.replace("ДИП", "ДИП")
        if cleaned not in seen:
            seen.add(cleaned)
            unique.append(cleaned)
    return unique[:6]


def infer_function(detail_type: str, text: str) -> str:
    text_l = normalize_name(text)
    if detail_type in {"вал", "вал-шестерня", "червячный вал"}:
        return "передаёт крутящий момент и связывает элементы привода в механизмах станка"
    if detail_type in {"шестерня", "колесо зубчатое", "колесо червячное"}:
        return "передаёт вращение между узлами коробки скоростей, коробки подач и приводов"
    if detail_type in {"гайка", "винт", "ШВП"}:
        return "обеспечивает продольные или поперечные подачи и точное перемещение рабочих узлов"
    if detail_type in {"люнет"}:
        return "фиксирует и центрирует заготовку при обработке длинномерных деталей"
    if detail_type in {"суппорт", "фартук"}:
        return "обеспечивает перемещение и работу исполнительных узлов токарного станка"
    if detail_type in {"коробка подач", "коробка скоростей"}:
        return "распределяет передаточные отношения и обеспечивает выбор режимов работы станка"
    if detail_type in {"муфта"}:
        return "соединяет элементы привода и передаёт вращение между сопрягаемыми узлами"
    if detail_type in {"патрон", "центр", "планшайба"}:
        return "обеспечивает установку, фиксацию и центрирование заготовки"
    if "шпиндел" in text_l:
        return "формирует и передаёт вращение шпиндельному узлу"
    return "используется в составе механических узлов станка и обеспечивает штатную работу привода и подач"


def first_non_empty(row: pd.Series, columns: list[str]) -> str:
    for column in columns:
        if column in row.index:
            value = normalize_text(row[column])
            if value:
                return value
    return ""


def build_lookup_records(df: pd.DataFrame, source_name: str) -> list[dict[str, str]]:
    code_col = find_column(df, CODE_COLUMN_CANDIDATES)
    name_col = find_column(df, NAME_COLUMN_CANDIDATES)
    records = []

    for _, row in df.iterrows():
        record = {
            "source": source_name,
            "code": normalize_text(row[code_col]) if code_col else "",
            "name": normalize_text(row[name_col]) if name_col else "",
        }
        for column in df.columns:
            record[str(column)] = normalize_text(row[column])
        records.append(record)
    return records


def build_indexes(source_frames: list[tuple[str, pd.DataFrame]]) -> tuple[dict[str, list[dict[str, str]]], dict[str, list[dict[str, str]]]]:
    by_code: dict[str, list[dict[str, str]]] = {}
    by_name: dict[str, list[dict[str, str]]] = {}

    for source_name, df in source_frames:
        for record in build_lookup_records(df, source_name):
            code_key = normalize_code(record.get("code", ""))
            name_key = normalize_name(record.get("name", ""))
            if code_key:
                by_code.setdefault(code_key, []).append(record)
            if name_key:
                by_name.setdefault(name_key, []).append(record)

    return by_code, by_name


def get_related_records(row: pd.Series, code_col: str | None, name_col: str | None, by_code: dict[str, list[dict[str, str]]], by_name: dict[str, list[dict[str, str]]]) -> list[dict[str, str]]:
    matches: list[dict[str, str]] = []

    code_value = normalize_code(row[code_col]) if code_col else ""
    name_value = normalize_name(row[name_col]) if name_col else ""

    if code_value and code_value in by_code:
        matches.extend(by_code[code_value])
    if name_value and name_value in by_name:
        matches.extend(by_name[name_value])

    deduped: list[dict[str, str]] = []
    seen = set()
    for item in matches:
        marker = (item.get("source", ""), item.get("code", ""), item.get("name", ""))
        if marker not in seen:
            seen.add(marker)
            deduped.append(item)
    return deduped


def make_technical_description(row: pd.Series, related_records: list[dict[str, str]], code_col: str | None, name_col: str | None) -> str:
    code_value = normalize_text(row[code_col]) if code_col else ""
    name_value = normalize_text(row[name_col]) if name_col else ""

    combined_parts = [name_value, code_value]
    for record in related_records:
        combined_parts.extend(collect_text_parts(record))
    combined_text = " ".join(part for part in combined_parts if part)

    detail_type = detect_detail_type(combined_text or name_value)
    models = extract_machine_models(combined_text)
    models_text = ", ".join(models) if models else "токарных, фрезерных и специальных станков"
    function_text = infer_function(detail_type, combined_text)

    sentence_1 = (
        f"{name_value or 'Данная позиция'} — это {detail_type}, применяемая в составе "
        f"{models_text}."
    )
    if code_value:
        sentence_1 = (
            f"{name_value or 'Данная позиция'} ({code_value}) — это {detail_type}, "
            f"применяемая в составе {models_text}."
        )

    sentence_2 = (
        f"Деталь используется в узлах привода и кинематики оборудования и {function_text}."
    )

    if models:
        sentence_3 = (
            f"Исполнение подбирается по коду детали, модели станка и сопрягаемому узлу, "
            f"что важно при ремонте коробки скоростей, коробки подач, суппорта, шпиндельной бабки и других механизмов."
        )
    else:
        sentence_3 = (
            "Конкретное исполнение подбирается по коду детали, размерам и узлу установки, "
            "чтобы обеспечить совместимость при ремонте и восстановлении оборудования."
        )

    return " ".join([sentence_1, sentence_2, sentence_3])


def strip_html_and_noise(text: str) -> str:
    if not text:
        return ""

    cleaned = html.unescape(str(text))
    cleaned = cleaned.replace("\\n", "\n")
    cleaned = re.sub(r"<\s*br\s*/?>", "\n", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"</\s*p\s*>", "\n", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"<[^>]+>", " ", cleaned)
    cleaned = re.sub(r"\{[^{}]*tilda[^{}]*\}", " ", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"tilda[\w\-:;/.,=#%+?& ]*", " ", cleaned, flags=re.IGNORECASE)
    cleaned = cleaned.replace("????", " ")
    cleaned = cleaned.replace("\xa0", " ")
    cleaned = re.sub(r"[•●▪◦◆■►]", " ", cleaned)
    cleaned = re.sub(r"[ \t]+\n", "\n", cleaned)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    cleaned = re.sub(r"[^\S\r\n]+", " ", cleaned)
    cleaned = re.sub(r"[^\w\s.,;:!?()%/\-«»№\n—‑]", " ", cleaned, flags=re.UNICODE)
    cleaned = re.sub(r"\s+([,.;:!?])", r"\1", cleaned)
    cleaned = re.sub(r"([,.;:!?])([^\s\n])", r"\1 \2", cleaned)
    cleaned = re.sub(r" {2,}", " ", cleaned)
    return cleaned.strip()


def anonymize_brands(text: str) -> str:
    cleaned = text
    for pattern, replacement in BRAND_PATTERNS:
        cleaned = pattern.sub(replacement, cleaned)

    cleaned = re.sub(
        r"(?:https?://|www\.)[^\s]+",
        "",
        cleaned,
        flags=re.IGNORECASE,
    )
    cleaned = re.sub(r"\b(?:tdrusstankosbyt\.ru|russtanko-rzn\.ru|rosstanko\.com|stankilife\.ru|kpsk\.ru|vse-k-stankam\.ru)\b", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\b(компания|фирма|бренд)\s+производитель\b", "производитель", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\bзавод[\s-]*изготовитель\b", "завод-изготовитель", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r" {2,}", " ", cleaned)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip()


def clean_description(text: str) -> str:
    cleaned = strip_html_and_noise(text)
    cleaned = anonymize_brands(cleaned)
    cleaned = re.sub(r"\s*\n\s*", "\n", cleaned)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip()


def main() -> None:
    print("Проверка путей:")
    missing_paths = []

    for path in ALL_PATHS:
        exists = path.exists()
        print(f"[{'OK' if exists else 'NO'}] {path}")
        if not exists:
            missing_paths.append(path)

    if missing_paths:
        raise FileNotFoundError(
            "Не найдены файлы:\n" + "\n".join(str(path) for path in missing_paths)
        )

    final_df = pd.read_excel(PROMPORTAL_FINAL, engine="openpyxl")
    descriptions_df = pd.read_csv(DESCRIPTION_CSV)
    rovniy_df = pd.read_excel(PROMPORTAL_ROVNIY, engine="openpyxl")
    shifry_df = pd.read_excel(PROMPORTAL_SHIFRY_NEW, engine="openpyxl")
    old_export_df = pd.read_excel(OLD_EXPORT, engine="openpyxl")
    directus_df = load_table(DIRECTUS_CSV)

    join_key = detect_join_key(final_df, descriptions_df)
    print(f"Ключ сопоставления: {join_key}")

    final_keys = normalize_key_series(final_df[join_key])
    description_keys = set(normalize_key_series(descriptions_df[join_key]).tolist())

    final_df["source_flag"] = final_keys.map(
        lambda value: "generated" if value in description_keys else "copied_with_services"
    )

    description_col = find_column(final_df, DESCRIPTION_COLUMN_CANDIDATES)
    if description_col is None:
        raise ValueError("В финальном файле не найден столбец description_new/Описание.")

    code_col = find_column(final_df, CODE_COLUMN_CANDIDATES)
    name_col = find_column(final_df, NAME_COLUMN_CANDIDATES)
    if name_col is None:
        raise ValueError("В финальном файле не найден столбец с наименованием товара.")

    source_frames = [
        ("PromPortal-РОВНЫЙ", rovniy_df),
        ("PromPortal+шифры-NEW", shifry_df),
        ("export от Кристины", old_export_df),
        ("Directus-Catalog-Actuality", directus_df),
    ]
    by_code, by_name = build_indexes(source_frames)

    copied_mask = final_df["source_flag"].eq("copied_with_services")
    copied_indices = final_df.index[copied_mask].tolist()

    for idx in copied_indices:
        row = final_df.loc[idx]
        related_records = get_related_records(
            row=row,
            code_col=code_col,
            name_col=name_col,
            by_code=by_code,
            by_name=by_name,
        )
        technical_description = make_technical_description(
            row=row,
            related_records=related_records,
            code_col=code_col,
            name_col=name_col,
        )
        final_df.at[idx, description_col] = f"{technical_description}\n{SERVICE_BLOCK}"

    final_df[description_col] = final_df[description_col].fillna("").map(clean_description)

    final_df.to_excel(PROMPORTAL_FINAL, index=False, engine="openpyxl")

    total_rows = len(final_df)
    generated_count = int((final_df["source_flag"] == "generated").sum())
    copied_count = int((final_df["source_flag"] == "copied_with_services").sum())

    print(f"Количество строк в PromPortal-FINAL-with-descriptions.xlsx: {total_rows}")
    print(f"Количество строк в description_new_full.csv: {len(descriptions_df)}")
    print(f"source_flag='generated': {generated_count}")
    print(f"source_flag='copied_with_services': {copied_count}")
    print(
        f"Подтверждение: описание для всех {copied_count} строк с source_flag='copied_with_services' перегенерировано и очищено."
    )

    code_col_out = code_col if code_col is not None else join_key
    examples = final_df.loc[copied_mask, [code_col_out, name_col, description_col]].head(3)

    for i, (_, example_row) in enumerate(examples.iterrows(), start=1):
        snippet = normalize_text(example_row[description_col]).replace("\n", " ")[:220]
        print(
            f"Пример {i}: Код={normalize_text(example_row[code_col_out])} | "
            f"Наименование={normalize_text(example_row[name_col])} | "
            f"description_new={snippet}"
        )


if __name__ == "__main__":
    main()
