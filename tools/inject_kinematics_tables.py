import re
from pathlib import Path

# --- KINEMATICS ORDER (copied from buildtkpskeleton.py) ---
KIN1ORDER = [
    "Передняя бабка", "Патрон", "Сменные колеса", "Коробка подач основная", "Коробка подач питчевая"
]
KIN2ORDER = [
    "Коробка подач", "Фартук", "Станина", "Задняя бабка", "Каретка", "Суппорт"
]

KIN_TABLE_HEADER = """
| Поз. | Z | Модуль | Ширина | Обозначение | Название |
|---|---|---|---|---|---|
| — | — | — | — | — | — |
""".strip()

KIN_DESC = """
Техническое описание узла готовится. Узел предназначен для передачи движения и обеспечения точности обработки. Типовые износы и поломки уточняются. Поставка возможна в сборе и по деталям. Для подбора необходим паспорт или фото.
""".strip()

INDEX_YML = Path("docs/ТКП/index.yml")
TKP_DIR = Path("docs/ТКП")

# --- Read models from index.yml ---
def get_models():
    models = []
    if not INDEX_YML.exists():
        return models
    for line in INDEX_YML.read_text(encoding="utf-8").splitlines():
        m = re.match(r"-\s*(\w+)", line)
        if m:
            model = m.group(1).lower()
            if model != "1n65":
                models.append(model)
    return models

# --- Ensure autoblock ---
def ensure_autoblock(md, block, content):
    pat = re.compile(rf"(<!-- AUTO:BEGIN {block} -->)(.*?)(<!-- AUTO:END {block} -->)", re.S)
    if pat.search(md):
        return pat.sub(rf"\1\n{content}\n\3", md)
    else:
        return md + f"\n<!-- AUTO:BEGIN {block} -->\n{content}\n<!-- AUTO:END {block} -->\n"

# --- Generate kinematics content ---
def gen_kin_block(order):
    out = []
    for uzel in order:
        out.append(f"### {uzel}\n{KIN_DESC}\n{KIN_TABLE_HEADER}\n")
    return "\n".join(out)

# --- Main injection ---
def main():
    models = get_models()
    for model in models:
        readme = TKP_DIR / model / "README.md"
        if not readme.exists():
            continue
        md = readme.read_text(encoding="utf-8")
        kin1 = gen_kin_block(KIN1ORDER)
        kin2 = gen_kin_block(KIN2ORDER)
        md = ensure_autoblock(md, "KIN1", kin1)
        md = ensure_autoblock(md, "KIN2", kin2)
        readme.write_text(md, encoding="utf-8")

if __name__ == "__main__":
    main()
