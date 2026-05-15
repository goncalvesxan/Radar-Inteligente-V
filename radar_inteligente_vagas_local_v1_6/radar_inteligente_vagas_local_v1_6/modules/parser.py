import re
from bs4 import BeautifulSoup
import requests

HEADERS = {"User-Agent": "Mozilla/5.0"}


def clean_text(text: str) -> str:
    text = re.sub(r"\r", "\n", text or "")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def is_linkedin(url: str) -> bool:
    return "linkedin.com" in (url or "").lower()


def fetch_public_page(url: str) -> dict:
    if is_linkedin(url):
        return {"ok": False, "error": "Link do LinkedIn: use abertura assistida e cole o texto visível/manual no campo de captura."}
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()
        title = soup.find("title").get_text(" ", strip=True) if soup.find("title") else ""
        text = clean_text(soup.get_text("\n"))
        return {"ok": True, "title": title, "text": text[:25000]}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def extract_job_fields(raw_text: str, url: str = "") -> dict:
    text = clean_text(raw_text)
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    joined = "\n".join(lines)

    cargo = ""
    empresa = ""
    local = ""
    modalidade = ""

    # Heurísticas simples para LinkedIn e ATS comuns
    if lines:
        for ln in lines[:20]:
            low = ln.lower()
            if not cargo and len(ln) <= 120 and not any(x in low for x in ["linkedin", "candidatar", "vaga", "jobs"]):
                cargo = ln
                break

    patterns_empresa = [r"Empresa\s*[:\-]\s*(.+)", r"Company\s*[:\-]\s*(.+)", r"na empresa\s+(.+)"]
    for p in patterns_empresa:
        m = re.search(p, joined, re.I)
        if m:
            empresa = m.group(1).strip()[:100]
            break

    patterns_local = [r"Local(?:ização)?\s*[:\-]\s*(.+)", r"Location\s*[:\-]\s*(.+)"]
    for p in patterns_local:
        m = re.search(p, joined, re.I)
        if m:
            local = m.group(1).strip()[:120]
            break

    # Caso comum no LinkedIn: Cargo / Empresa / Local nas primeiras linhas
    if not empresa and len(lines) >= 2:
        for i, ln in enumerate(lines[:12]):
            if cargo and i > 0 and ln != cargo and len(ln) <= 100 and not any(k in ln.lower() for k in ["tempo", "candid", "visualiza", "conex"]):
                empresa = ln
                break
    if not local:
        loc_candidates = [ln for ln in lines[:25] if any(x in ln.lower() for x in ["brasil", "são paulo", "santos", "remoto", "híbrido", "presencial"])]
        if loc_candidates:
            local = loc_candidates[0][:120]

    low_text = joined.lower()
    if "remoto" in low_text:
        modalidade = "Remoto"
    elif "híbrido" in low_text or "hibrido" in low_text:
        modalidade = "Híbrido"
    elif "presencial" in low_text:
        modalidade = "Presencial"

    req_markers = ["requisitos", "qualificações", "qualificacoes", "requirements", "perfil", "o que você precisa"]
    requisitos = []
    capture = False
    for ln in lines:
        low = ln.lower()
        if any(m in low for m in req_markers):
            capture = True
            continue
        if capture and len(requisitos) < 25:
            if any(end in low for end in ["benefícios", "beneficios", "sobre a empresa", "about us", "informações adicionais"]):
                break
            requisitos.append(ln)
    requisitos_txt = "\n".join(requisitos).strip()

    return {
        "cargo": cargo,
        "empresa": empresa,
        "local": local,
        "modalidade": modalidade,
        "requisitos": requisitos_txt,
        "descricao": joined[:20000],
        "link": url,
    }
