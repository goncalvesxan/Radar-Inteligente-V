from pathlib import Path
from datetime import datetime
import pandas as pd

COLUMNS = ["data", "cargo", "empresa", "link", "score", "status", "observacoes"]

def pipeline_path(base_dir=None):
    base = Path(base_dir) if base_dir else Path(__file__).resolve().parents[1]
    return base / "data" / "pipeline.csv"

def load_pipeline(base_dir=None):
    path = pipeline_path(base_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        pd.DataFrame(columns=COLUMNS).to_csv(path, index=False, encoding="utf-8")
    try:
        df = pd.read_csv(path)
    except Exception:
        df = pd.DataFrame(columns=COLUMNS)
    for col in COLUMNS:
        if col not in df.columns:
            df[col] = ""
    return df[COLUMNS]

def save_application(job, score, status="Analisada", obs="", base_dir=None):
    path = pipeline_path(base_dir)
    df = load_pipeline(base_dir)
    row = {
        "data": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "cargo": job.get("cargo", ""),
        "empresa": job.get("empresa", ""),
        "link": job.get("link", ""),
        "score": score,
        "status": status,
        "observacoes": obs
    }
    df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    df.to_csv(path, index=False, encoding="utf-8")
    return df
