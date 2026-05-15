import json
from pathlib import Path
import streamlit as st
import pandas as pd

from modules.job_parser import extract_from_public_url, infer_job_fields
from modules.matching import analyze_match
from modules.messages import recruiter_message, application_summary
from modules.pipeline import load_pipeline, save_application

BASE_DIR = Path(__file__).resolve().parent
PROFILE_PATH = BASE_DIR / "perfil_candidato.json"

DEFAULT_PROFILE = {
    "nome": "Alexandre Gonçalves da Silva",
    "resumo": "Analista de Contabilidade Sênior com atuação em ativo imobilizado, CAPEX, IFRS16, controle financeiro, automação e análise tributária.",
    "competencias_fortes": [
        "Ativo Imobilizado", "CAPEX", "IFRS16", "Controladoria", "Contabilidade", "Power BI", "Excel", "VBA", "Automação", "AS400", "SAP", "Análise Tributária", "Gestão de Projetos", "Depreciação", "Centro de Serviços Compartilhados"
    ],
    "preferencias": {"areas": ["Controladoria", "Contabilidade", "Financeiro", "Ativo Imobilizado", "CAPEX", "Projetos", "Fiscal"]}
}

def ensure_profile_file() -> None:
    if not PROFILE_PATH.exists():
        PROFILE_PATH.write_text(json.dumps(DEFAULT_PROFILE, ensure_ascii=False, indent=2), encoding="utf-8")

@st.cache_data(show_spinner=False)
def load_profile_cached(profile_mtime: float):
    ensure_profile_file()
    return json.loads(PROFILE_PATH.read_text(encoding="utf-8"))

def load_profile():
    ensure_profile_file()
    return load_profile_cached(PROFILE_PATH.stat().st_mtime)

st.set_page_config(page_title="Radar Inteligente de Vagas AI", layout="wide")

try:
    profile = load_profile()
except Exception as exc:
    st.error(f"Erro ao carregar perfil_candidato.json: {exc}")
    st.info("Recriei um perfil padrão. Revise o arquivo perfil_candidato.json e rode novamente se necessário.")
    PROFILE_PATH.write_text(json.dumps(DEFAULT_PROFILE, ensure_ascii=False, indent=2), encoding="utf-8")
    profile = DEFAULT_PROFILE

st.title("Radar Inteligente de Vagas AI — Local V1.5")
st.caption("Copiloto local para análise de vagas, abertura assistida de links do LinkedIn, captura manual, leitura de páginas públicas e pipeline de candidatura.")

with st.sidebar:
    st.header("Perfil")
    st.write(profile.get("nome", ""))
    st.write(profile.get("resumo", ""))
    st.divider()
    st.info("LinkedIn: cole o link, abra em nova aba pelo botão e copie manualmente o texto visível. Sites públicos externos podem ser lidos por URL.")
    st.caption(f"Base local: {BASE_DIR}")

tab1, tab2, tab3, tab4 = st.tabs(["Analisar vaga", "Captura Manual / LinkedIn", "Pipeline", "Guia local"])

with tab1:
    st.subheader("Buscar detalhes por link público")
    url = st.text_input("Cole o link da vaga", placeholder="https://...")
    col_a, col_b = st.columns([1, 1])
    with col_a:
        fetch = st.button("Buscar detalhes da vaga pelo link", type="primary")
    with col_b:
        if url and "linkedin.com" in url.lower():
            st.link_button("Abrir vaga do LinkedIn em nova aba", url, use_container_width=True)
        else:
            st.caption("Para LinkedIn, cole o link e use o botão de abertura assistida.")

    if fetch and url:
        with st.spinner("Lendo página pública..."):
            result = extract_from_public_url(url)
        if not result.get("ok"):
            if result.get("linkedin_manual"):
                st.warning(result.get("error"))
            else:
                st.error(result.get("error"))
        else:
            text = result.get("texto", "")
            inferred = infer_job_fields(text, url=url)
            inferred["cargo"] = result.get("titulo") or inferred.get("cargo", "")
            st.session_state["job_text"] = text
            st.session_state["job"] = inferred
            st.success("Detalhes capturados. Revise abaixo.")

    job_default = st.session_state.get("job", {"cargo": "", "empresa": "", "local": "", "link": url})
    c1, c2, c3 = st.columns(3)
    with c1:
        cargo = st.text_input("Cargo", value=job_default.get("cargo", ""), key="cargo_url")
    with c2:
        empresa = st.text_input("Empresa", value=job_default.get("empresa", ""), key="empresa_url")
    with c3:
        local = st.text_input("Local", value=job_default.get("local", ""), key="local_url")
    job_text = st.text_area("Descrição da vaga", value=st.session_state.get("job_text", ""), height=260)
    job = {"cargo": cargo, "empresa": empresa, "local": local, "link": url or job_default.get("link", "")}

    if st.button("Analisar aderência", key="analisar_url"):
        analysis = analyze_match(job_text, profile)
        st.session_state["analysis"] = analysis
        st.session_state["job"] = job
        st.session_state["last_origin"] = "URL/manual"
        st.metric("Score de aderência", f"{analysis['score']}%")
        st.success(analysis["recomendacao"])
        st.write("Competências encontradas:", ", ".join(analysis["competencias_encontradas"]) or "Nenhuma")
        st.write("Palavras-chave:", ", ".join(analysis["palavras_chave"][:15]))

    if "analysis" in st.session_state and st.session_state.get("job"):
        st.divider()
        st.subheader("Mensagem para recrutador")
        st.text_area("Mensagem gerada", recruiter_message(profile, st.session_state["job"], st.session_state["analysis"]), height=220)
        st.subheader("Resumo para candidatura")
        st.text_area("Resumo", application_summary(profile, st.session_state["job"], st.session_state["analysis"]), height=220)
        if st.button("Salvar no pipeline", key="save_url"):
            save_application(st.session_state["job"], st.session_state["analysis"]["score"], obs="Salvo pela análise por URL/manual", base_dir=BASE_DIR)
            st.success("Candidatura registrada no pipeline.")

with tab2:
    st.subheader("Captura Manual / LinkedIn")
    st.write("Cole o link do LinkedIn, abra a página em nova aba, copie o texto visível da vaga e cole abaixo. A ferramenta não faz scraping do LinkedIn; ela apenas ajuda a abrir a página e analisar o conteúdo que você copiar.")
    link_manual = st.text_input("Link da vaga para referência", key="link_manual", placeholder="https://www.linkedin.com/jobs/view/...")
    if link_manual and "linkedin.com" in link_manual.lower():
        st.link_button("Abrir página da vaga no LinkedIn", link_manual, use_container_width=True)
        st.caption("Depois de abrir, copie manualmente título, empresa, local e descrição da vaga e cole no campo abaixo.")
    elif link_manual:
        st.link_button("Abrir link em nova aba", link_manual, use_container_width=True)
    manual_text = st.text_area("Cole aqui o texto copiado da vaga", height=360, key="manual_text")
    cm1, cm2, cm3 = st.columns(3)
    with cm1:
        cargo_manual = st.text_input("Cargo", key="cargo_manual")
    with cm2:
        empresa_manual = st.text_input("Empresa", key="empresa_manual")
    with cm3:
        local_manual = st.text_input("Local", key="local_manual")

    if st.button("Analisar texto colado", type="primary", key="analisar_manual"):
        inferred = infer_job_fields(manual_text, url=link_manual)
        job_m = {
            "cargo": cargo_manual or inferred.get("cargo", ""),
            "empresa": empresa_manual or inferred.get("empresa", ""),
            "local": local_manual or inferred.get("local", ""),
            "link": link_manual
        }
        analysis_m = analyze_match(manual_text, profile)
        st.session_state["manual_job"] = job_m
        st.session_state["manual_analysis"] = analysis_m

    if "manual_analysis" in st.session_state:
        analysis_m = st.session_state["manual_analysis"]
        job_m = st.session_state["manual_job"]
        st.metric("Score de aderência", f"{analysis_m['score']}%")
        st.success(analysis_m["recomendacao"])
        st.write("Competências encontradas:", ", ".join(analysis_m["competencias_encontradas"]) or "Nenhuma")
        st.text_area("Mensagem para recrutador", recruiter_message(profile, job_m, analysis_m), height=220)
        st.text_area("Resumo para candidatura", application_summary(profile, job_m, analysis_m), height=220)
        if st.button("Salvar análise manual no pipeline", key="save_manual"):
            save_application(job_m, analysis_m["score"], obs="Captura manual/LinkedIn", base_dir=BASE_DIR)
            st.success("Registro salvo.")

with tab3:
    st.subheader("Pipeline de candidaturas")
    df = load_pipeline(BASE_DIR)
    st.dataframe(df, use_container_width=True)
    st.download_button("Baixar pipeline CSV", df.to_csv(index=False).encode("utf-8"), file_name="pipeline_candidaturas.csv")

with tab4:
    st.subheader("Como rodar localmente")
    st.code("""python -m venv .venv
.venv\\Scripts\\activate
pip install -r requirements.txt
streamlit run app.py""", language="bash")
    st.subheader("Principais correções da V1.5")
    st.markdown("""
- Corrigido erro `FileNotFoundError` do `perfil_candidato.json` usando caminho absoluto baseado no arquivo `app.py`.
- O app agora cria automaticamente `perfil_candidato.json` se o arquivo não existir.
- O pipeline usa caminho absoluto local e cria `data/pipeline.csv` automaticamente.
- Removida dependência obrigatória de `lxml`; o parser usa `html.parser`.
- Botão de salvar análise manual corrigido fora do bloco de clique inicial.
- Implementado botão para abrir links do LinkedIn em nova aba.
- Mantida captura manual para LinkedIn e leitura por URL para páginas públicas externas.
""")
    st.subheader("Implementações incluídas")
    st.markdown("""
- Leitura de páginas públicas por URL.
- Abertura assistida de links do LinkedIn em nova aba.
- Captura manual segura para LinkedIn.
- Análise de aderência por competências do perfil.
- Geração de mensagem para recrutador.
- Resumo de candidatura.
- Pipeline em CSV.
- Estrutura preparada para extensão Chrome local em `browser_extension_linkedin_capture/`.
""")
