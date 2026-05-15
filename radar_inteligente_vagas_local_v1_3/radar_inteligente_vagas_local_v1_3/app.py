import json
from pathlib import Path
import streamlit as st
import pandas as pd

from modules.job_parser import extract_from_public_url, infer_job_fields
from modules.matching import analyze_match
from modules.messages import recruiter_message, application_summary
from modules.pipeline import load_pipeline, save_application

st.set_page_config(page_title="Radar Inteligente de Vagas AI", layout="wide")

PROFILE_PATH = Path("perfil_candidato.json")

@st.cache_data
def load_profile():
    return json.loads(PROFILE_PATH.read_text(encoding="utf-8"))

profile = load_profile()

st.title("Radar Inteligente de Vagas AI — Local V1.3")
st.caption("Copiloto local para análise de vagas, captura manual do LinkedIn, leitura de páginas públicas e pipeline de candidatura.")

with st.sidebar:
    st.header("Perfil")
    st.write(profile.get("nome"))
    st.write(profile.get("resumo"))
    st.divider()
    st.info("LinkedIn: use captura manual do texto visível. Sites públicos externos podem ser lidos por URL.")

tab1, tab2, tab3, tab4 = st.tabs(["Analisar vaga", "Captura Manual / LinkedIn", "Pipeline", "Guia local"])

with tab1:
    st.subheader("Buscar detalhes por link público")
    url = st.text_input("Cole o link da vaga", placeholder="https://...")
    col_a, col_b = st.columns([1, 1])
    with col_a:
        fetch = st.button("Buscar detalhes da vaga pelo link", type="primary")
    with col_b:
        st.caption("Para LinkedIn, abra a vaga no navegador e cole o texto na aba Captura Manual.")

    if fetch and url:
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

    job = st.session_state.get("job", {"cargo": "", "empresa": "", "local": "", "link": url})
    c1, c2, c3 = st.columns(3)
    with c1:
        job["cargo"] = st.text_input("Cargo", value=job.get("cargo", ""), key="cargo_url")
    with c2:
        job["empresa"] = st.text_input("Empresa", value=job.get("empresa", ""), key="empresa_url")
    with c3:
        job["local"] = st.text_input("Local", value=job.get("local", ""), key="local_url")
    job["link"] = url or job.get("link", "")
    job_text = st.text_area("Descrição da vaga", value=st.session_state.get("job_text", ""), height=260)

    if st.button("Analisar aderência", key="analisar_url"):
        analysis = analyze_match(job_text, profile)
        st.session_state["analysis"] = analysis
        st.session_state["job"] = job
        st.metric("Score de aderência", f"{analysis['score']}%")
        st.success(analysis["recomendacao"])
        st.write("Competências encontradas:", ", ".join(analysis["competencias_encontradas"]) or "Nenhuma")
        st.write("Palavras-chave:", ", ".join(analysis["palavras_chave"][:15]))

    if "analysis" in st.session_state:
        st.divider()
        st.subheader("Mensagem para recrutador")
        st.text_area("Mensagem gerada", recruiter_message(profile, st.session_state["job"], st.session_state["analysis"]), height=220)
        st.subheader("Resumo para candidatura")
        st.text_area("Resumo", application_summary(profile, st.session_state["job"], st.session_state["analysis"]), height=220)
        if st.button("Salvar no pipeline", key="save_url"):
            save_application(st.session_state["job"], st.session_state["analysis"]["score"], obs="Salvo pela análise por URL/manual")
            st.success("Candidatura registrada no pipeline.")

with tab2:
    st.subheader("Captura Manual / LinkedIn")
    st.write("Abra a vaga no navegador, copie o texto visível e cole abaixo. A ferramenta analisa localmente sem scraping massivo.")
    link_manual = st.text_input("Link da vaga para referência", key="link_manual")
    manual_text = st.text_area("Cole aqui o texto copiado da vaga", height=360, key="manual_text")
    cm1, cm2, cm3 = st.columns(3)
    with cm1:
        cargo_manual = st.text_input("Cargo", key="cargo_manual")
    with cm2:
        empresa_manual = st.text_input("Empresa", key="empresa_manual")
    with cm3:
        local_manual = st.text_input("Local", key="local_manual")
    if st.button("Analisar texto colado", type="primary"):
        inferred = infer_job_fields(manual_text, url=link_manual)
        job_m = {
            "cargo": cargo_manual or inferred.get("cargo", ""),
            "empresa": empresa_manual or inferred.get("empresa", ""),
            "local": local_manual or inferred.get("local", ""),
            "link": link_manual
        }
        analysis_m = analyze_match(manual_text, profile)
        st.metric("Score de aderência", f"{analysis_m['score']}%")
        st.success(analysis_m["recomendacao"])
        st.write("Competências encontradas:", ", ".join(analysis_m["competencias_encontradas"]) or "Nenhuma")
        st.text_area("Mensagem para recrutador", recruiter_message(profile, job_m, analysis_m), height=220)
        st.text_area("Resumo para candidatura", application_summary(profile, job_m, analysis_m), height=220)
        if st.button("Salvar análise manual no pipeline"):
            save_application(job_m, analysis_m["score"], obs="Captura manual/LinkedIn")
            st.success("Registro salvo.")

with tab3:
    st.subheader("Pipeline de candidaturas")
    df = load_pipeline()
    st.dataframe(df, use_container_width=True)
    st.download_button("Baixar pipeline CSV", df.to_csv(index=False).encode("utf-8"), file_name="pipeline_candidaturas.csv")

with tab4:
    st.subheader("Como rodar localmente")
    st.code("""python -m venv .venv
.venv\\Scripts\\activate
pip install -r requirements.txt
streamlit run app.py""", language="bash")
    st.subheader("Implementações incluídas")
    st.markdown("""
- Leitura de páginas públicas por URL.
- Bloqueio orientativo para LinkedIn com captura manual segura.
- Análise de aderência por competências do perfil.
- Geração de mensagem para recrutador.
- Resumo de candidatura.
- Pipeline em CSV.
- Estrutura preparada para extensão Chrome local em `browser_extension_linkedin_capture/`.
""")
