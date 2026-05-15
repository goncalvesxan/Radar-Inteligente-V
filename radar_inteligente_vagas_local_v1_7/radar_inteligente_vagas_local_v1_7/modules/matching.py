import re

def norm(s):
    return re.sub(r"[^a-z0-9áéíóúâêôãõç]+", " ", str(s).lower()).strip()

def analyze_fit(job, profile):
    text = norm(" ".join([job.get("cargo",""), job.get("descricao",""), job.get("requisitos","")]))
    skills = profile.get("competencias", []) or []
    targets = profile.get("cargos_alvo", []) or []
    found = []
    missing = []
    for skill in skills:
        terms = [norm(skill)]
        if "ifrs" in norm(skill): terms.append("ifrs")
        if "power bi" in norm(skill): terms.append("powerbi")
        hit = any(t and t in text for t in terms)
        (found if hit else missing).append(skill)
    title_bonus = 0
    cargo = norm(job.get("cargo", ""))
    for target in targets:
        words = [w for w in norm(target).split() if len(w) > 4]
        if any(w in cargo for w in words):
            title_bonus = 15
            break
    skill_score = int((len(found) / max(len(skills), 1)) * 70)
    score = min(100, skill_score + title_bonus + (10 if job.get("senioridade") in ["Sênior", "Especialista", "Coordenação"] else 0))
    if score >= 80:
        rec = "Alta aderência: priorizar candidatura e contato com recrutador."
    elif score >= 60:
        rec = "Boa aderência: revisar gaps e adaptar currículo antes de aplicar."
    elif score >= 40:
        rec = "Aderência média: vale networking antes da candidatura."
    else:
        rec = "Baixa aderência: aplicar somente se houver interesse estratégico."
    return {"score": score, "competencias_encontradas": found, "gaps": missing[:12], "recomendacao": rec}

def recruiter_message(job, profile, analysis):
    found = ", ".join(analysis.get("competencias_encontradas", [])[:6]) or "minha experiência em contabilidade, controladoria e melhoria de processos"
    cargo = job.get("cargo") or "a oportunidade"
    empresa = job.get("empresa") or "a empresa"
    return f"Olá, tudo bem? Vi a oportunidade de {cargo} na {empresa} e acredito ter boa aderência ao desafio. Minha experiência envolve {found}, além de atuação com análise financeira, controles e automação de processos. A vaga chamou minha atenção principalmente pela conexão com os requisitos apresentados. Fico à disposição para conversar e compartilhar mais detalhes do meu perfil."
