from pathlib import Path
from datetime import datetime
import pandas as pd

PIPELINE = Path("data/pipeline.csv")

def load_pipeline():
    PIPELINE.parent.mkdir(exist_ok=True)
    if not PIPELINE.exists():
        PIPELINE.write_text("data,cargo,empresa,link,score,status,observacoes\n", encoding="utf-8")
    return pd.read_csv(PIPELINE)

def save_application(job, score, status="Analisada", obs=""):
    df = load_pipeline()
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
    df.to_csv(PIPELINE, index=False)
    return df
