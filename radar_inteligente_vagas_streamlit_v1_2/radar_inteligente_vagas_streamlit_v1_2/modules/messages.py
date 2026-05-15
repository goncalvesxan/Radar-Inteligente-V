from typing import Dict, List


def build_recruiter_message(profile: Dict, job_title: str, company: str, matched_skills: List[str], contact_name: str = "") -> str:
    nome = profile.get("nome", "")
    skills = ", ".join(matched_skills[:6]) if matched_skills else "minha experiência em contabilidade, controladoria e melhoria de processos"
    saudacao = f"Olá {contact_name}," if contact_name else "Olá,"
    return f"""{saudacao}

Vi a oportunidade de {job_title} na {company} e acredito ter forte aderência ao desafio, principalmente pela minha atuação com {skills}.

Tenho experiência em gestão de ativos imobilizados, CAPEX, IFRS16, automações financeiras, Power BI, VBA e projetos de melhoria em rotinas contábeis e de controladoria.

Atualmente também conduzo um projeto estratégico voltado à capitalização e controle de investimentos aplicados em unidades educacionais, com reconhecimento contábil, depreciação e análise financeira dos ativos.

Fico à disposição para conversarmos sobre como posso contribuir para a posição.

Atenciosamente,
{nome}"""


def build_application_summary(profile: Dict, job_title: str, company: str, matched_skills: List[str]) -> str:
    skills = ", ".join(matched_skills[:8]) if matched_skills else "contabilidade, controladoria, automação e análise financeira"
    return (
        f"Candidatura para {job_title} na {company}. "
        f"Principais pontos de aderência: {skills}. "
        "Recomenda-se adaptar o currículo destacando resultados em CAPEX, ativo imobilizado, IFRS16, Power BI, VBA e projetos de melhoria."
    )
