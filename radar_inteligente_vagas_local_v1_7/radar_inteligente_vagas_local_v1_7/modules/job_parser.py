import re
from bs4 import BeautifulSoup

STOP_LINES = {"salvar", "candidatar-se", "candidate-se", "compartilhar", "denunciar", "exibir mais", "mostrar mais"}

def clean_text(text: str) -> str:
    if not text:
        return ""
    text = BeautifulSoup(text, "html.parser").get_text("\n") if "<" in text and ">" in text else text
    lines = []
    seen = set()
    for raw in text.replace("\r", "\n").split("\n"):
        line = re.sub(r"\s+", " ", raw).strip()
        if not line or line.lower() in STOP_LINES:
            continue
        if len(line) <= 2:
            continue
        key = line.lower()
        if key in seen:
            continue
        seen.add(key)
        lines.append(line)
    return "\n".join(lines)

def infer_company(lines):
    for i, line in enumerate(lines[:30]):
        low = line.lower()
        if "empresa" in low and i+1 < len(lines):
            return lines[i+1]
        if " · " in line:
            return line.split(" · ")[0].strip()
    # LinkedIn often title, company, location in first lines
    if len(lines) > 1 and len(lines[1]) < 80:
        return lines[1]
    return ""

def infer_title(lines):
    for line in lines[:20]:
        low = line.lower()
        if any(k in low for k in ["analista", "especialista", "coordenador", "gerente", "controller", "contábil", "financeiro", "accountant", "analyst"]):
            if len(line) < 120:
                return line
    return lines[0] if lines else ""

def infer_location(lines):
    patterns = ["brasil", "são paulo", "santos", "osasco", "remoto", "híbrido", "presencial", "rio de janeiro", "curitiba", "campinas"]
    for line in lines[:50]:
        low = line.lower()
        if any(p in low for p in patterns) and len(line) < 140:
            return line
    return ""

def infer_modality(text):
    low = text.lower()
    if "remoto" in low or "remote" in low:
        return "Remoto"
    if "híbrido" in low or "hybrid" in low:
        return "Híbrido"
    if "presencial" in low or "on-site" in low or "onsite" in low:
        return "Presencial"
    return "Não identificado"

def infer_seniority(text):
    low = text.lower()
    if any(k in low for k in ["sênior", "senior", "sr.", "sr "]):
        return "Sênior"
    if any(k in low for k in ["pleno", "jr/pl", "middle"]):
        return "Pleno"
    if any(k in low for k in ["júnior", "junior", "jr.", "jr "]):
        return "Júnior"
    if any(k in low for k in ["especialista", "specialist"]):
        return "Especialista"
    if any(k in low for k in ["coordenador", "coordenação", "coordinator"]):
        return "Coordenação"
    return "Não identificado"

def extract_requirements(text):
    lines = text.splitlines()
    start_idx = 0
    keys = ["requisitos", "qualificações", "requirements", "o que esperamos", "necessário", "você precisa", "responsabilidades", "atividades"]
    for i, line in enumerate(lines):
        if any(k in line.lower() for k in keys):
            start_idx = i
            break
    return "\n".join(lines[start_idx:start_idx+80]) if lines else ""

def parse_job_text(raw_text: str, url: str = "") -> dict:
    text = clean_text(raw_text)
    lines = text.splitlines()
    return {
        "cargo": infer_title(lines),
        "empresa": infer_company(lines),
        "local": infer_location(lines),
        "modalidade": infer_modality(text),
        "senioridade": infer_seniority(text),
        "descricao": text[:12000],
        "requisitos": extract_requirements(text),
        "link": url,
    }
