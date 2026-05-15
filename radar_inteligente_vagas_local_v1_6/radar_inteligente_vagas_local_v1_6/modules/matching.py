import re


def tokenize(text: str):
    return set(re.findall(r"[a-zA-ZÀ-ÿ0-9\+\#\.]{3,}", (text or "").lower()))


def analyze_match(job: dict, profile: dict) -> dict:
    job_text = " ".join(str(job.get(k, "")) for k in ["cargo","empresa","local","modalidade","requisitos","descricao"])
    skills = profile.get("competencias", []) or []
    prefs = profile.get("preferencias", {}) or {}
    target_roles = prefs.get("cargos_alvo", []) or []

    job_tokens = tokenize(job_text)
    matched_skills = []
    missing_skills = []
    for skill in skills:
        skill_tokens = tokenize(skill)
        if skill_tokens and (skill.lower() in job_text.lower() or skill_tokens & job_tokens):
            matched_skills.append(skill)
        else:
            missing_skills.append(skill)

    role_score = 0
    cargo = (job.get("cargo") or "").lower()
    for role in target_roles:
        role_tokens = tokenize(role)
        if role_tokens and (role.lower() in cargo or role_tokens & tokenize(cargo)):
            role_score = max(role_score, 20)

    skill_score = min(60, int((len(matched_skills) / max(1, len(skills))) * 60))
    text_bonus = 0
    important = ["capex", "ifrs16", "ativo", "imobilizado", "controladoria", "power bi", "vba", "tribut"]
    for word in important:
        if word in job_text.lower():
            text_bonus += 3
    score = min(100, role_score + skill_score + min(text_bonus, 20))

    if score >= 80:
        rec = "Alta aderência: aplicar e abordar recrutador."
    elif score >= 65:
        rec = "Boa aderência: revisar gaps e aplicar com mensagem personalizada."
    elif score >= 50:
        rec = "Aderência média: aplicar apenas se a vaga for estratégica."
    else:
        rec = "Baixa aderência: priorizar outras vagas."

    return {"score": score, "recomendacao": rec, "competencias_encontradas": matched_skills[:15], "gaps": missing_skills[:10]}
