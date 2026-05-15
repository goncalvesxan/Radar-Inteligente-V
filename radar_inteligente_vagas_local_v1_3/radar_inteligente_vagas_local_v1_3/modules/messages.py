def recruiter_message(profile, job, analysis):
    nome = profile.get("nome", "")
    cargo = job.get("cargo") or "a oportunidade"
    empresa = job.get("empresa") or "a empresa"
    fortes = ", ".join(analysis.get("competencias_encontradas", [])[:6]) or "minha experiência em contabilidade, controladoria e projetos financeiros"
    return f"""Olá, tudo bem? Vi a oportunidade para {cargo} na {empresa} e acredito ter boa aderência ao desafio.

Tenho experiência com {fortes}, além de atuação em automação de processos, análise financeira e melhoria de controles contábeis.

Pelo escopo da vaga, acredito que posso contribuir principalmente na organização dos processos, qualidade das informações e entrega de resultados com visão técnica e prática.

Fico à disposição para conversar.\n\n{nome}"""

def application_summary(profile, job, analysis):
    return f"""Resumo para candidatura

Cargo: {job.get('cargo','')}
Empresa: {job.get('empresa','')}
Score de aderência: {analysis.get('score',0)}%
Recomendação: {analysis.get('recomendacao','')}

Pontos fortes identificados:
- """ + "\n- ".join(analysis.get("competencias_encontradas", [])[:10]) + "\n\nPontos para revisar/adaptar no currículo:\n- " + "\n- ".join(analysis.get("competencias_nao_identificadas", [])[:8])
