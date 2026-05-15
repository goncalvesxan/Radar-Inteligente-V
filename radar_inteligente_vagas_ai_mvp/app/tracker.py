from __future__ import annotations
from datetime import datetime
import pandas as pd
from pathlib import Path

TRACKER_PATH = Path("data/application_tracker.csv")


def save_application(job: dict, score: float, status: str = "analisada") -> None:
    row = {
        "data": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "titulo": job.get("titulo", ""),
        "empresa": job.get("empresa", ""),
        "local": job.get("local", ""),
        "link": job.get("link", ""),
        "score": score,
        "status": status,
    }
    if TRACKER_PATH.exists():
        df = pd.read_csv(TRACKER_PATH)
        df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    else:
        df = pd.DataFrame([row])
    df.to_csv(TRACKER_PATH, index=False)
