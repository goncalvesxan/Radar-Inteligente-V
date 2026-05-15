import re
from typing import Dict, List, Tuple


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").lower()).strip()


def extract_keywords(text: str) -> List[str]:
    text_n = _normalize(text)
    base_terms = [
        "capex", "ativo imobilizado", "ifrs16", "ifrs 16", "controle financeiro",
        "controladoria", "contabilidade", "análise tributária", "tributário", "power bi",
        "excel", "vba", "as400", "erp", "sap", "depreciação", "orçamento",
        "budget", "forecast", "fechamento contábil", "centro de serviços compartilhados",
        "ssc", "gestão de projetos", "automação", "inteligência artificial", "ia",
        "relatórios gerenciais", "dashboard", "custos", "cpc", "ifrs"
    ]
    found = []
    for term in base_terms:
        if term in text_n:
            found.append(term)
    return sorted(set(found))


def score_job(profile: Dict, job_text: str, job_title: str = "") -> Dict:
    job_all = _normalize(f"{job_title} {job_text}")
    profile_skills = profile.get("competencias_chave", [])
    profile_exp = profile.get("experiencias_relevantes", [])
    target_roles = profile.get("preferencias_vaga", {}).get("cargos_alvo", [])

    matched_skills = []
    missing_skills = []

    for skill in profile_skills:
        skill_n = _normalize(skill)
        if skill_n and skill_n in job_all:
            matched_skills.append(skill)
        else:
            missing_skills.append(skill)

    job_keywords = extract_keywords(job_all)

    title_score = 0
    for role in target_roles:
        role_words = [w for w in _normalize(role).split() if len(w) > 3]
        if role_words:
            overlap = sum(1 for w in role_words if w in job_all) / len(role_words)
            title_score = max(title_score, overlap)

    skill_score = min(len(matched_skills) / max(len(profile_skills), 1), 1)
    keyword_boost = min(len(job_keywords) / 10, 1)
    exp_boost = 0
    for exp in profile_exp:
        exp_words = [w for w in _normalize(exp).split() if len(w) > 5]
        if exp_words and sum(1 for w in exp_words if w in job_all) >= 2:
            exp_boost += 0.04
    exp_boost = min(exp_boost, 0.20)

    final_score = round((skill_score * 60) + (title_score * 25) + (keyword_boost * 15) + (exp_boost * 100), 1)
    final_score = min(final_score, 100)

    if final_score >= 85:
        recommendation = "Aplicar com prioridade alta + mensagem ao recrutador."
    elif final_score >= 70:
        recommendation = "Aplicar após revisão + adaptar currículo e mensagem."
    elif final_score >= 55:
        recommendation = "Fazer networking primeiro e avaliar gaps."
    else:
        recommendation = "Baixa aderência. Aplicar somente se houver interesse estratégico."

    return {
        "score": final_score,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills[:12],
        "job_keywords": job_keywords,
        "recommendation": recommendation
    }
