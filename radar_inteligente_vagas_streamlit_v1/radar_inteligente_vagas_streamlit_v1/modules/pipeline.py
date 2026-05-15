from pathlib import Path
from datetime import datetime
import pandas as pd

COLUMNS = ["data", "cargo", "empresa", "link", "score", "status", "contato", "mensagem", "resumo"]


def load_pipeline(path: str) -> pd.DataFrame:
    p = Path(path)
    if not p.exists():
        return pd.DataFrame(columns=COLUMNS)
    df = pd.read_csv(p)
    for col in COLUMNS:
        if col not in df.columns:
            df[col] = ""
    return df[COLUMNS]


def save_application(path: str, cargo: str, empresa: str, link: str, score: float, status: str, contato: str, mensagem: str, resumo: str) -> None:
    df = load_pipeline(path)
    row = {
        "data": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "cargo": cargo,
        "empresa": empresa,
        "link": link,
        "score": score,
        "status": status,
        "contato": contato,
        "mensagem": mensagem,
        "resumo": resumo
    }
    df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    df.to_csv(path, index=False)
