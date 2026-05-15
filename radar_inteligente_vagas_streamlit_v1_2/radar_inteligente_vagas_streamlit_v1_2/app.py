import json
from pathlib import Path

import pandas as pd
import streamlit as st

from modules.matching import score_job
from modules.messages import build_recruiter_message, build_application_summary
from modules.pipeline import load_pipeline, save_application

BASE_DIR = Path(__file__).parent
PROFILE_PATH = BASE_DIR / "data" / "profile.json"
PIPELINE_PATH = BASE_DIR / "data" / "pipeline.csv"

st.set_page_config(
    page_title="Radar Inteligente de Vagas AI",
    page_icon="🎯",
    layout="wide"
)


def load_profile():
    with open(PROFILE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_profile(profile):
    with open(PROFILE_PATH, "w", encoding="utf-8") as f:
        json.dump(profile, f, ensure_ascii=False, indent=2)

profile = load_profile()

st.title("🎯 Radar Inteligente de Vagas AI - Streamlit V1.2")
st.caption("Copiloto supervisionado para análise de vagas, priorização, mensagens e pipeline de candidaturas.")

with st.sidebar:
    st.header("Menu")
    page = st.radio(
        "Selecione o módulo",
        ["Analisar vaga", "Pipeline", "Perfil", "Autofill supervisionado", "Como rodar"]
    )

if page == "Analisar vaga":
    st.subheader("1. Análise de aderência da vaga")

    col1, col2 = st.columns([1, 1])
    with col1:
        cargo = st.text_input("Cargo da vaga", placeholder="Ex.: Analista de Controladoria Sênior")
        empresa = st.text_input("Empresa", placeholder="Ex.: Empresa ABC")
        link = st.text_input("Link da vaga", placeholder="Cole o link da vaga")
        contato = st.text_input("Nome do recrutador/contato", placeholder="Opcional")
    with col2:
        status = st.selectbox("Status inicial", ["Analisada", "Aplicar", "Networking", "Aplicada", "Descartada"])
        st.info("Cole abaixo a descrição completa da vaga. Quanto mais completa, melhor a análise.")

    descricao = st.text_area("Descrição da vaga", height=280, placeholder="Cole aqui os requisitos, responsabilidades e diferenciais da vaga...")

    if st.button("Analisar aderência", type="primary"):
        if not descricao.strip() or not cargo.strip() or not empresa.strip():
            st.warning("Preencha ao menos cargo, empresa e descrição da vaga.")
        else:
            result = score_job(profile, descricao, cargo)
            message = build_recruiter_message(profile, cargo, empresa, result["matched_skills"], contato)
            summary = build_application_summary(profile, cargo, empresa, result["matched_skills"])

            st.session_state["last_result"] = result
            st.session_state["last_message"] = message
            st.session_state["last_summary"] = summary
            st.session_state["last_form"] = {"cargo": cargo, "empresa": empresa, "link": link, "contato": contato, "status": status}

    if "last_result" in st.session_state:
        result = st.session_state["last_result"]
        form = st.session_state["last_form"]
        message = st.session_state["last_message"]
        summary = st.session_state["last_summary"]

        st.divider()
        c1, c2, c3 = st.columns(3)
        c1.metric("Score de aderência", f"{result['score']}%")
        c2.metric("Competências encontradas", len(result["matched_skills"]))
        c3.metric("Palavras-chave da vaga", len(result["job_keywords"]))

        st.success(result["recommendation"])

        left, right = st.columns(2)
        with left:
            st.markdown("#### Competências aderentes")
            st.write(result["matched_skills"] or "Nenhuma competência-chave encontrada de forma direta.")
            st.markdown("#### Palavras-chave identificadas na vaga")
            st.write(result["job_keywords"] or "Nenhuma palavra-chave mapeada.")
        with right:
            st.markdown("#### Possíveis gaps ou termos não encontrados")
            st.write(result["missing_skills"] or "Sem gaps relevantes identificados.")

        st.markdown("#### Mensagem sugerida ao recrutador")
        st.text_area("Copie, ajuste e envie manualmente", message, height=260)

        st.markdown("#### Resumo para adaptar currículo/candidatura")
        st.text_area("Resumo", summary, height=120)

        if st.button("Salvar no pipeline"):
            save_application(
                str(PIPELINE_PATH),
                form["cargo"], form["empresa"], form["link"], result["score"], form["status"], form["contato"], message, summary
            )
            st.success("Registro salvo no pipeline.")

elif page == "Pipeline":
    st.subheader("2. Pipeline de candidaturas")
    df = load_pipeline(str(PIPELINE_PATH))
    if df.empty:
        st.info("Ainda não há candidaturas registradas.")
    else:
        col1, col2 = st.columns([1, 1])
        with col1:
            status_filter = st.multiselect("Filtrar por status", sorted(df["status"].dropna().unique().tolist()))
        with col2:
            min_score = st.slider("Score mínimo", 0, 100, 0)
        view = df.copy()
        if status_filter:
            view = view[view["status"].isin(status_filter)]
        view["score"] = pd.to_numeric(view["score"], errors="coerce").fillna(0)
        view = view[view["score"] >= min_score]
        st.dataframe(view, use_container_width=True, height=420)
        st.download_button("Baixar pipeline CSV", data=view.to_csv(index=False).encode("utf-8"), file_name="pipeline_candidaturas.csv", mime="text/csv")

elif page == "Perfil":
    st.subheader("3. Perfil mestre do candidato")
    st.caption("Edite sua base profissional. Ela alimenta o score e as mensagens.")

    profile_text = st.text_area("profile.json", json.dumps(profile, ensure_ascii=False, indent=2), height=520)
    if st.button("Salvar perfil"):
        try:
            new_profile = json.loads(profile_text)
            save_profile(new_profile)
            st.success("Perfil salvo. Recarregue a página para usar os novos dados.")
        except json.JSONDecodeError as e:
            st.error(f"JSON inválido: {e}")

elif page == "Autofill supervisionado":
    st.subheader("4. Autofill supervisionado em sites externos")
    st.warning("Use apenas em sites onde você tem autorização e revise tudo antes de enviar. O envio final deve ser manual.")
    st.markdown("""
Este módulo foi preparado para atuar como **copiloto de preenchimento**, não como robô de candidatura.

Fluxo recomendado:
1. abrir o site externo da empresa;
2. identificar campos do formulário;
3. preencher dados objetivos com base no perfil mestre;
4. sugerir respostas personalizadas;
5. você revisa;
6. você envia manualmente.

O exemplo técnico opcional está em: `scripts/autofill_playwright_example.py`. Ele não é necessário para rodar o painel Streamlit.
""")
    st.code("""# opcional, somente para testar autofill localmente:
pip install playwright
python -m playwright install
python scripts/autofill_playwright_example.py""", language="bash")
elif page == "Como rodar":
    st.subheader("5. Como rodar localmente")
    st.code("""
cd radar_inteligente_vagas_streamlit_v1_2
python -m venv .venv
.venv\\Scripts\\activate
pip install -r requirements.txt
streamlit run app.py
""", language="bash")
    st.markdown("Depois disso, o Streamlit abrirá o painel no navegador.")
