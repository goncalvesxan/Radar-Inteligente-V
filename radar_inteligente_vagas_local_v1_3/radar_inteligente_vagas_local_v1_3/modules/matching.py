import re
from collections import Counter

def tokenize(text):
    return re.findall(r"[a-zA-ZÀ-ÿ0-9+#./-]{3,}", (text or "").lower())

def analyze_match(job_text: str, profile: dict) -> dict:
    skills = profile.get("competencias_fortes", [])
    job_low = (job_text or "").lower()
    found = []
    missing = []
    for s in skills:
        if s.lower() in job_low:
            found.append(s)
        else:
            missing.append(s)
    area_hits = []
    for a in profile.get("preferencias", {}).get("areas", []):
        if a.lower() in job_low:
            area_hits.append(a)
    base = int((len(found) / max(len(skills), 1)) * 70)
    bonus = min(20, len(area_hits) * 5)
    senior_bonus = 10 if any(x in job_low for x in ["sênior", "senior", "especialista", "pleno", "sr"]) else 0
    score = min(100, base + bonus + senior_bonus)
    if score >= 80:
        recomendacao = "Aplicar imediatamente e enviar mensagem personalizada."
    elif score >= 65:
        recomendacao = "Aplicar após revisar gaps e adaptar currículo."
    elif score >= 50:
        recomendacao = "Fazer networking antes de aplicar."
    else:
        recomendacao = "Baixa aderência; aplicar apenas se houver interesse estratégico."
    tokens = [x for x in tokenize(job_text) if len(x) > 3]
    common = [w for w, _ in Counter(tokens).most_common(20)]
    return {
        "score": score,
        "competencias_encontradas": found,
        "competencias_nao_identificadas": missing[:12],
        "areas_encontradas": area_hits,
        "palavras_chave": common,
        "recomendacao": recomendacao
    }
