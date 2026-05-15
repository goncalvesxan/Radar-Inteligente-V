import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
PROFILE_PATH = DATA_DIR / "perfil_candidato.json"
PIPELINE_PATH = DATA_DIR / "pipeline.csv"

DEFAULT_PROFILE = {
    "nome": "Alexandre Gonçalves da Silva",
    "titulo": "Analista de Contabilidade Sênior | Ativo Imobilizado | CAPEX | IFRS16 | Controladoria | Power BI | Automação VBA | IA aplicada",
    "email": "",
    "telefone": "",
    "linkedin": "",
    "cidade": "São Paulo/SP",
    "resumo": "Profissional sênior de contabilidade, controladoria e gestão de ativos, com experiência em CAPEX, ativo imobilizado, IFRS16, análise tributária, automação de processos, Power BI, projetos financeiros e melhoria de controles.",
    "competencias": ["Ativo Imobilizado", "CAPEX", "IFRS16", "Controladoria", "Contabilidade", "Power BI", "Excel Avançado", "VBA", "Análise Tributária", "AS400", "Gestão de Projetos", "Automação", "IA aplicada"],
    "cargos_alvo": ["Analista de Contabilidade Sênior", "Especialista Contábil", "Analista de Controladoria", "Especialista em Ativo Imobilizado", "Analista Financeiro Sênior"],
    "setores_alvo": ["Indústria", "Educação", "Serviços", "CSC", "Tecnologia", "Saúde"],
    "pretensao_salarial": "A combinar",
    "disponibilidade": "A combinar"
}

def ensure_files():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not PROFILE_PATH.exists():
        PROFILE_PATH.write_text(json.dumps(DEFAULT_PROFILE, ensure_ascii=False, indent=2), encoding="utf-8")
    if not PIPELINE_PATH.exists():
        PIPELINE_PATH.write_text("data,cargo,empresa,local,modalidade,score,status,link,observacoes\n", encoding="utf-8")

def load_profile():
    ensure_files()
    try:
        return json.loads(PROFILE_PATH.read_text(encoding="utf-8"))
    except Exception:
        PROFILE_PATH.write_text(json.dumps(DEFAULT_PROFILE, ensure_ascii=False, indent=2), encoding="utf-8")
        return DEFAULT_PROFILE.copy()

def save_profile(profile: dict):
    ensure_files()
    PROFILE_PATH.write_text(json.dumps(profile, ensure_ascii=False, indent=2), encoding="utf-8")
