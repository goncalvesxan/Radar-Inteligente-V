from __future__ import annotations


def recruiter_message(profile: dict, job: dict, analysis: dict) -> str:
    nome = profile.get("nome", "")
    titulo = job.get("titulo", "a oportunidade")
    empresa = job.get("empresa", "empresa")
    aderentes = ", ".join(analysis.get("aderentes", [])[:5]) or "minha experiência em controladoria e finanças"

    return f"""Olá [Nome], tudo bem?

Vi a oportunidade de {titulo} na {empresa} e acredito ter forte aderência ao desafio, principalmente por minha experiência com {aderentes}.

Atualmente atuo com gestão de ativos, CAPEX, automações financeiras/contábeis e projetos de melhoria de processos, incluindo reconhecimento de investimentos no ativo fixo, controle de depreciação e análise financeira.

Fiquei interessado porque a vaga parece exigir um perfil técnico, analítico e voltado a melhoria de processos. Posso encaminhar meu currículo ou conversar rapidamente sobre como minha experiência pode contribuir?

Obrigado,
{nome}"""


def cover_note(profile: dict, job: dict, analysis: dict) -> str:
    aderentes = ", ".join(analysis.get("aderentes", [])[:8])
    return f"""Resumo para candidatura:
Perfil com aderência de {analysis.get('score')}% para a vaga de {job.get('titulo')}.
Principais pontos de aderência: {aderentes}.
Recomendação: {analysis.get('recomendacao')}.
"""
