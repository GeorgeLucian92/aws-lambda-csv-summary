import csv
import json
from pathlib import Path
from collections import Counter
from datetime import datetime, timezone
from typing import Dict, Any, List

PROJECT_ROOT = Path(__file__).resolve().parents[1]
INPUT_CSV = PROJECT_ROOT / "data" / "sample_input.csv"
OUTPUT_DIR = PROJECT_ROOT / "output"
OUTPUT_JSON = OUTPUT_DIR / "summary.json"


def summarize_rows(rows: List[Dict[str, str]]) -> Dict[str, Any]:
    cleaned = []
    for r in rows:
        title = (r.get("title") or "").strip()
        category = (r.get("category") or "").strip()
        if title and category:
            cleaned.append({"title": title, "category": category})

    counts = Counter([r["category"] for r in cleaned])
    top_categories = [{"category": k, "count": v} for k, v in counts.most_common(5)]

    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "rows_total": len(rows),
        "rows_valid": len(cleaned),
        "unique_categories": len(counts),
        "top_categories": top_categories,
    }


def main() -> int:
    if not INPUT_CSV.exists():
        print(f"Missing input file: {INPUT_CSV}")
        return 1

    with INPUT_CSV.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    summary = summarize_rows(rows)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_JSON.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print("✅ Local summary generated:")
    print(OUTPUT_JSON)
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
