
def recruiter_message(job: dict, profile: dict, analysis: dict) -> str:
    nome = profile.get("nome", "")
    cargo = job.get("cargo") or "oportunidade"
    empresa = job.get("empresa") or "empresa"
    skills = ", ".join(analysis.get("competencias_encontradas", [])[:5])
    return f"""Olá, tudo bem?

Vi a oportunidade de {cargo} na {empresa} e acredito ter boa aderência ao desafio. Minha experiência envolve {skills or 'contabilidade, controladoria, automação financeira e gestão de ativos'}, com atuação em rotinas de melhoria de processos e controles corporativos.

Pelo escopo da vaga, acredito que posso contribuir principalmente com análise contábil/financeira, organização de processos, indicadores e automações para ganho de eficiência.

Fico à disposição para conversarmos.

{nome}""".strip()


def application_summary(job: dict, profile: dict, analysis: dict) -> str:
    return f"""Cargo: {job.get('cargo','')}
Empresa: {job.get('empresa','')}
Local/modalidade: {job.get('local','')} | {job.get('modalidade','')}
Score: {analysis.get('score')}%
Recomendação: {analysis.get('recomendacao')}

Pontos fortes identificados:
- """ + "\n- ".join(analysis.get("competencias_encontradas", []) or ["Não identificado automaticamente"]) + "\n\nGaps/revisão:\n- " + "\n- ".join(analysis.get("gaps", []) or ["Sem gaps relevantes identificados"])
