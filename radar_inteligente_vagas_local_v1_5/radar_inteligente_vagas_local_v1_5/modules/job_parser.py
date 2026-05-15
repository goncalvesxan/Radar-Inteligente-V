import re
import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36"
}

def is_linkedin(url: str) -> bool:
    return "linkedin.com" in (url or "").lower()


def clean_text(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def extract_from_public_url(url: str) -> dict:
    """Extrai texto de páginas públicas. LinkedIn fica em captura manual para evitar scraping massivo."""
    if not url:
        return {"ok": False, "error": "Informe uma URL."}
    if is_linkedin(url):
        return {
            "ok": False,
            "linkedin_manual": True,
            "error": "Para LinkedIn, use a aba 'Captura Manual / LinkedIn' e cole o texto visível da vaga."
        }
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        for tag in soup(["script", "style", "noscript", "svg"]):
            tag.extract()
        title = clean_text(soup.title.get_text(" ")) if soup.title else ""
        h1_tag = soup.find("h1")
        h1 = clean_text(h1_tag.get_text(" ")) if h1_tag else ""
        meta_desc = ""
        meta = soup.find("meta", attrs={"name": "description"}) or soup.find("meta", attrs={"property": "og:description"})
        if meta and meta.get("content"):
            meta_desc = clean_text(meta.get("content"))
        body = clean_text(soup.get_text(" "))
        return {
            "ok": True,
            "url": url,
            "titulo": h1 or title,
            "descricao_curta": meta_desc,
            "texto": body[:30000]
        }
    except Exception as exc:
        return {"ok": False, "error": f"Não foi possível ler a página: {exc}"}


def infer_job_fields(text: str, url: str = "") -> dict:
    raw = text or ""
    lines = [clean_text(x) for x in raw.splitlines() if clean_text(x)]
    cargo = lines[0][:120] if lines else ""
    empresa = ""
    local = ""
    patterns = {
        "empresa": [r"Empresa[:\-]\s*(.+)", r"Company[:\-]\s*(.+)", r"Organização[:\-]\s*(.+)"],
        "local": [r"Local[:\-]\s*(.+)", r"Localização[:\-]\s*(.+)", r"Location[:\-]\s*(.+)", r"Cidade[:\-]\s*(.+)"]
    }
    for field, pats in patterns.items():
        for p in pats:
            m = re.search(p, raw, flags=re.I)
            if m:
                val = clean_text(m.group(1))[:120]
                if field == "empresa": empresa = val
                if field == "local": local = val
                break
    return {"cargo": cargo, "empresa": empresa, "local": local, "link": url}
