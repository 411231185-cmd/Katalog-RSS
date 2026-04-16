import os
import pandas as pd

def extract_from_csv(file_path):
    try:
        df = pd.read_csv(file_path)
        if 'name' in df.columns:
            return df['name'].dropna().tolist()
        elif 'наименование' in df.columns:
            return df['наименование'].dropna().tolist()
        elif 'название' in df.columns:
            return df['название'].dropna().tolist()
        elif 'товар' in df.columns:
            return df['товар'].dropna().tolist()
        elif 'title' in df.columns:
            return df['title'].dropna().tolist()
    except Exception as e:
        print(f"Ошибка при чтении {file_path}: {e}")
    return []

def extract_from_xlsx(file_path):
    try:
        df = pd.read_excel(file_path)
        return df.iloc[:, 0].dropna().tolist()  # Первая колонка
    except Exception as e:
        print(f"Ошибка при чтении {file_path}: {e}")
    return []

def extract_from_md(file_path):
    items = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):  # Пропускаем заголовки
                    items.append(line)
    except Exception as e:
        print(f"Ошибка при чтении {file_path}: {e}")
    return items

def main():
    output_file = r'C:\GitHub-Repositories\Katalog-RSS\NOMENCLATURA RSS-2026.md'
    all_items = []

    for root, dirs, files in os.walk(r'C:\GitHub-Repositories\Katalog-RSS'):
        for file in files:
            file_path = os.path.join(root, file)
            if file.endswith('.csv'):
                all_items.extend(extract_from_csv(file_path))
            elif file.endswith('.xlsx'):
                all_items.extend(extract_from_xlsx(file_path))
            elif file.endswith('.md') and file != 'README.md':
                all_items.extend(extract_from_md(file_path))

    with open(output_file, 'w', encoding='utf-8') as f:
        for item in all_items:
            f.write(f"{item}\n")
        f.write(f"# Итого позиций (с дублями): {len(all_items)}\n")

if __name__ == "__main__":
    main()
