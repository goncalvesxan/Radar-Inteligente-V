from __future__ import annotations
import json
from pathlib import Path
import pandas as pd
import streamlit as st
from matcher import keyword_score
from generator import recruiter_message, cover_note
from tracker import save_application

st.set_page_config(page_title="Radar Inteligente de Vagas AI", layout="wide")
st.title("Radar Inteligente de Vagas AI")
st.caption("MVP com análise de aderência, mensagens personalizadas e pipeline de candidatura supervisionado.")

profile = json.loads(Path("data/profile.json").read_text(encoding="utf-8"))

with st.sidebar:
    st.header("Perfil base")
    st.write(profile.get("nome"))
    st.write(profile.get("titulo"))
    st.divider()
    threshold = st.slider("Score mínimo para recomendar candidatura", 0, 100, 70)

st.subheader("1. Cole ou selecione uma vaga")
mode = st.radio("Entrada", ["Colar descrição", "Usar CSV"], horizontal=True)

job = {}
if mode == "Colar descrição":
    c1, c2, c3 = st.columns(3)
    job["titulo"] = c1.text_input("Título da vaga", "Especialista em Ativo Imobilizado")
    job["empresa"] = c2.text_input("Empresa", "")
    job["local"] = c3.text_input("Local", "")
    job["link"] = st.text_input("Link da vaga/site externo", "")
    job["descricao"] = st.text_area("Descrição da vaga", height=220)
else:
    df = pd.read_csv("data/jobs.csv")
    selected = st.selectbox("Vaga", df.index, format_func=lambda i: f"{df.loc[i, 'titulo']} - {df.loc[i, 'empresa']}")
    job = df.loc[selected].to_dict()
    st.write(job.get("descricao"))

if st.button("Analisar vaga", type="primary"):
    analysis = keyword_score(job.get("descricao", "") + " " + job.get("titulo", ""), profile)
    st.session_state["job"] = job
    st.session_state["analysis"] = analysis

if "analysis" in st.session_state:
    analysis = st.session_state["analysis"]
    job = st.session_state["job"]
    st.subheader("2. Resultado da análise")
    m1, m2, m3 = st.columns(3)
    m1.metric("Score de aderência", f"{analysis['score']}%")
    m2.metric("Pontos fortes", len(analysis["aderentes"]))
    m3.metric("Gaps", len(analysis["gaps"]))
    st.success(analysis["recomendacao"] if analysis["score"] >= threshold else "Abaixo do limite definido. Prioridade reduzida.")

    with st.expander("Competências aderentes"):
        st.write(analysis["aderentes"])
    with st.expander("Gaps ou pontos a reforçar"):
        st.write(analysis["gaps"])

    st.subheader("3. Mensagem ao recrutador")
    st.text_area("Copie e personalize antes de enviar", recruiter_message(profile, job, analysis), height=260)

    st.subheader("4. Nota para candidatura")
    st.text_area("Resumo para usar no cadastro externo", cover_note(profile, job, analysis), height=140)

    if st.button("Registrar no pipeline"):
        save_application(job, analysis["score"], "analisada")
        st.toast("Candidatura registrada.")

st.divider()
st.subheader("5. Pipeline")
tracker = Path("data/application_tracker.csv")
if tracker.exists():
    st.dataframe(pd.read_csv(tracker), use_container_width=True)
else:
    st.info("Nenhuma candidatura registrada ainda.")
