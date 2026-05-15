import json
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
PROFILE_PATH = DATA_DIR / "perfil_candidato.json"
PIPELINE_PATH = DATA_DIR / "pipeline.csv"

DEFAULT_PROFILE = {
    "nome": "",
    "headline": "",
    "localizacao": "",
    "email": "",
    "telefone": "",
    "linkedin": "",
    "resumo": "",
    "competencias": [],
    "experiencias_chave": [],
    "idiomas": [],
    "preferencias": {"cargos_alvo": [], "modelo": [], "senioridade": []},
}


def ensure_files():
    DATA_DIR.mkdir(exist_ok=True)
    if not PROFILE_PATH.exists():
        PROFILE_PATH.write_text(json.dumps(DEFAULT_PROFILE, ensure_ascii=False, indent=2), encoding="utf-8")
    if not PIPELINE_PATH.exists():
        pd.DataFrame(columns=["data","cargo","empresa","local","link","score","recomendacao","status"]).to_csv(PIPELINE_PATH, index=False)


def load_profile():
    ensure_files()
    try:
        return json.loads(PROFILE_PATH.read_text(encoding="utf-8"))
    except Exception:
        return DEFAULT_PROFILE.copy()


def save_profile(profile: dict):
    ensure_files()
    PROFILE_PATH.write_text(json.dumps(profile, ensure_ascii=False, indent=2), encoding="utf-8")


def load_pipeline():
    ensure_files()
    return pd.read_csv(PIPELINE_PATH)


def append_pipeline(row: dict):
    ensure_files()
    df = load_pipeline()
    df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    df.to_csv(PIPELINE_PATH, index=False)
