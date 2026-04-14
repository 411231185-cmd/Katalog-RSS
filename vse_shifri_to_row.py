from pathlib import Path

src = Path(r"C:\GitHub-Repositories\Katalog-RSS\Kinematika-Chertegi\Vse - Vse Shifri .md")
dst = Path(r"C:\GitHub-Repositories\Katalog-RSS\Kinematika-Chertegi\Vse - Vse Shifri - v stroku.md")

text = src.read_text(encoding="utf-8")

lines = [l.strip() for l in text.splitlines() if l.strip()]

# здесь уже должны быть чистые шифры, просто соединяем
unique = []
seen = set()
for l in lines:
    if l not in seen:
        seen.add(l)
        unique.append(l)

result = ", ".join(unique)

dst.write_text(result, encoding="utf-8")

print(f"Шифров в строке: {len(unique)}")
print(f"Результат: {dst}")