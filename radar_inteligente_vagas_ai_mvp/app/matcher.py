from __future__ import annotations
import re
from rapidfuzz import fuzz


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").lower()).strip()


def keyword_score(job_text: str, profile: dict) -> dict:
    text = normalize(job_text)
    skills = profile.get("skills", []) + profile.get("areas_alvo", [])
    hits, partials, missing = [], [], []

    for skill in skills:
        s = normalize(skill)
        if not s:
            continue
        if s in text:
            hits.append(skill)
        else:
            ratio = fuzz.partial_ratio(s, text)
            if ratio >= 82:
                partials.append(skill)
            else:
                missing.append(skill)

    total = max(len(skills), 1)
    score = round(((len(hits) * 1.0) + (len(partials) * 0.65)) / total * 100, 1)
    return {
        "score": min(score, 100),
        "aderentes": hits,
        "parciais": partials,
        "gaps": missing[:12],
        "recomendacao": recommend(score)
    }


def recommend(score: float) -> str:
    if score >= 85:
        return "Aplicar imediatamente + mensagem ao recrutador"
    if score >= 70:
        return "Aplicar após ajuste do currículo + mensagem contextual"
    if score >= 55:
        return "Fazer networking antes; candidatura apenas se houver forte interesse"
    return "Baixa prioridade"
