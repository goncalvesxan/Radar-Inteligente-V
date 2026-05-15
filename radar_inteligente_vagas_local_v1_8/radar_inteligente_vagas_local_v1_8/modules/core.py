import re
import json
import csv
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
PROFILE_PATH = DATA_DIR / "perfil_candidato.json"
PIPELINE_PATH = DATA_DIR / "pipeline.csv"

DEFAULT_PROFILE = {
    "nome": "Alexandre Gonçalves da Silva",
    "titulo": "Analista de Contabilidade Sênior | Ativo Imobilizado | CAPEX | IFRS16 | Controladoria | Power BI | Automação VBA",
    "email": "",
    "telefone": "",
    "linkedin": "",
    "cidade": "Santos / São Paulo",
    "resumo": "Profissional sênior de contabilidade, controladoria e gestão de ativos imobilizados, com experiência em CAPEX, IFRS16, análise tributária, automações em Excel/VBA, Power BI, gestão de projetos, controle financeiro e melhoria de processos.",
    "competencias": ["Ativo Imobilizado", "CAPEX", "IFRS16", "Controladoria", "Contabilidade", "Power BI", "Excel Avançado", "VBA", "Análise Tributária", "Gestão de Projetos", "AS400", "SAP", "Centro de Serviços Compartilhados", "Depreciação", "Conciliação", "Fechamento Contábil"],
    "experiencias_chave": ["Gestão de ativos imobilizados", "Capitalização de investimentos", "Controle de CAPEX", "Projetos de automação financeira", "Análise e melhoria de processos contábeis"],
    "idiomas": ["Português", "Espanhol intermediário"],
    "pretensao_salarial": "A combinar",
    "disponibilidade": "A combinar"
}


def ensure_files():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not PROFILE_PATH.exists():
        PROFILE_PATH.write_text(json.dumps(DEFAULT_PROFILE, ensure_ascii=False, indent=2), encoding="utf-8")
    if not PIPELINE_PATH.exists():
        PIPELINE_PATH.write_text("data,cargo,empresa,link,score,status,observacoes\n", encoding="utf-8")


def load_profile():
    ensure_files()
    try:
        return json.loads(PROFILE_PATH.read_text(encoding="utf-8"))
    except Exception:
        PROFILE_PATH.write_text(json.dumps(DEFAULT_PROFILE, ensure_ascii=False, indent=2), encoding="utf-8")
        return DEFAULT_PROFILE.copy()


def save_profile(profile: dict):
    ensure_files()
    PROFILE_PATH.write_text(json.dumps(profile, ensure_ascii=False, indent=2), encoding="utf-8")


def normalize_text(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r"\r", "\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def extract_job_fields(text: str, url: str = "") -> dict:
    text = normalize_text(text)
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    joined = "\n".join(lines)
    cargo = ""
    empresa = ""
    local = ""
    modalidade = ""
    senioridade = ""

    # Heurísticas LinkedIn: primeiras linhas costumam conter cargo, empresa e localização.
    if lines:
        ignore = {"linkedin", "jobs", "vagas", "entrar", "cadastre-se", "salvar", "candidatar-se"}
        useful = [l for l in lines[:25] if l.lower() not in ignore and len(l) > 2]
        if useful:
            cargo = useful[0][:160]
        if len(useful) > 1:
            empresa = useful[1][:120]
        for l in useful[1:8]:
            if any(x in l.lower() for x in ["brasil", "são paulo", "santos", "remoto", "híbrido", "presencial", "rio de janeiro", "barueri", "osasco"]):
                local = l[:160]
                break

    low = joined.lower()
    if "remoto" in low:
        modalidade = "Remoto"
    if "híbrido" in low or "hibrido" in low:
        modalidade = "Híbrido" if not modalidade else modalidade + " / Híbrido"
    if "presencial" in low:
        modalidade = "Presencial" if not modalidade else modalidade + " / Presencial"

    for term in ["estágio", "júnior", "junior", "pleno", "sênior", "senior", "especialista", "coordenador", "gerente"]:
        if term in low:
            senioridade = term.capitalize()
            break

    # Campos mais confiáveis se existir padrão explícito
    cargo_match = re.search(r"(?:cargo|posição|vaga)[:\-]\s*(.+)", joined, flags=re.I)
    emp_match = re.search(r"(?:empresa|company)[:\-]\s*(.+)", joined, flags=re.I)
    loc_match = re.search(r"(?:local|localização|location)[:\-]\s*(.+)", joined, flags=re.I)
    if cargo_match:
        cargo = cargo_match.group(1).strip()[:160]
    if emp_match:
        empresa = emp_match.group(1).strip()[:120]
    if loc_match:
        local = loc_match.group(1).strip()[:160]

    return {
        "cargo": cargo,
        "empresa": empresa,
        "local": local,
        "modalidade": modalidade,
        "senioridade": senioridade,
        "descricao": joined,
        "link": url
    }


def fetch_public_page(url: str) -> dict:
    if not url:
        return {"ok": False, "error": "Informe uma URL."}
    domain = urlparse(url).netloc.lower()
    if "linkedin.com" in domain:
        return {"ok": False, "error": "Links do LinkedIn devem ser usados no modo assistido/local ou com texto copiado manualmente."}
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36",
        "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8"
    }
    try:
        r = requests.get(url, headers=headers, timeout=20)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        for tag in soup(["script", "style", "noscript", "svg"]):
            tag.decompose()
        title = soup.title.get_text(" ", strip=True) if soup.title else ""
        body = soup.get_text("\n", strip=True)
        text = normalize_text(title + "\n" + body)
        return {"ok": True, "text": text, "fields": extract_job_fields(text, url)}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def score_job(description: str, profile: dict) -> dict:
    desc = (description or "").lower()
    skills = profile.get("competencias", [])
    matched = []
    missing = []
    for s in skills:
        if s.lower() in desc:
            matched.append(s)
        else:
            missing.append(s)
    base = int((len(matched) / max(1, len(skills))) * 70)
    senior_bonus = 0
    title = profile.get("titulo", "").lower()
    for term in ["sênior", "senior", "especialista", "controladoria", "contabilidade", "capex", "ifrs16"]:
        if term in desc and term in title:
            senior_bonus += 4
    score = min(100, base + min(30, senior_bonus))
    if score >= 80:
        rec = "Aplicar com prioridade alta"
    elif score >= 65:
        rec = "Aplicar após ajustar currículo/mensagem"
    elif score >= 45:
        rec = "Avaliar gaps antes de aplicar"
    else:
        rec = "Baixa aderência; aplicar somente se houver interesse estratégico"
    return {"score": score, "matched": matched, "missing": missing[:12], "recommendation": rec}


def generate_recruiter_message(fields: dict, profile: dict, score_info: dict) -> str:
    cargo = fields.get("cargo") or "a oportunidade"
    empresa = fields.get("empresa") or "a empresa"
    pontos = ", ".join(score_info.get("matched", [])[:6]) or "minha experiência em contabilidade, controladoria e automação de processos"
    return (
        f"Olá, tudo bem? Vi a oportunidade para {cargo} na {empresa} e acredito ter boa aderência ao desafio. "
        f"Minha experiência envolve {pontos}, além de atuação com melhoria de processos, análise contábil/financeira e projetos corporativos. "
        "Gostaria de me colocar à disposição para conversar sobre como posso contribuir para a posição."
    )


def save_pipeline(fields: dict, score: int, status: str, notes: str = ""):
    ensure_files()
    with PIPELINE_PATH.open("a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow([datetime.now().strftime("%Y-%m-%d %H:%M"), fields.get("cargo", ""), fields.get("empresa", ""), fields.get("link", ""), score, status, notes])


def load_pipeline_df():
    import pandas as pd
    ensure_files()
    return pd.read_csv(PIPELINE_PATH)
