import pandas as pd
from pathlib import Path

root = Path(r"C:\GitHub-Repositories\Katalog-RSS")
src = root / "Exel-Claude" / "PromPortal-ROVNY-BATCHES.csv"
out = root / "Exel-Claude" / "generated" / "PromPortal-READY-FOR-TILDA.csv"

df = pd.read_csv(src, encoding="utf-8")

needed_cols = []
for col in ["row", "code", "name", "category", "batch_id",
            "description_draft", "sourceflag",
            "new_description_top", "quality_flag", "edit_flag"]:
    if col in df.columns:
        needed_cols.append(col)

ready = df[needed_cols].copy()
out.parent.mkdir(parents=True, exist_ok=True)
ready.to_csv(out, index=False, encoding="utf-8-sig")
print("Saved:", out)
