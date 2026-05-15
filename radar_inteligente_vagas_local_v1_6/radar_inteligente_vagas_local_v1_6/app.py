import json
import webbrowser
from datetime import datetime

import pandas as pd
import streamlit as st

from modules.storage import load_profile, save_profile, load_pipeline, append_pipeline, ensure_files
from modules.parser import fetch_public_page, extract_job_fields, is_linkedin
from modules.matching import analyze_match
from modules.messages import recruiter_message, application_summary

try:
    import pyperclip
except Exception:
    pyperclip = None

st.set_page_config(page_title="Radar Inteligente de Vagas AI", layout="wide", page_icon="🎯")
ensure_files()

st.title("🎯 Radar Inteligente de Vagas AI — Local V1.6")
st.caption("Copiloto local para análise de vagas, LinkedIn assistido, perfil editável e pipeline de candidatura.")

with st.sidebar:
    st.header("Menu")
    page = st.radio("Escolha a área", ["Analisar vaga", "Meu perfil", "Pipeline", "Instruções"], label_visibility="collapsed")

profile = load_profile()

if page == "Meu perfil":
    st.subheader("⚙️ Configuração do meu perfil")
    st.info("Edite seu perfil aqui. Essas informações serão usadas para calcular aderência, gerar mensagens e preencher resumos.")
    with st.form("profile_form"):
        col1, col2 = st.columns(2)
        with col1:
            nome = st.text_input("Nome", value=profile.get("nome", ""))
            headline = st.text_input("Headline profissional", value=profile.get("headline", ""))
            localizacao = st.text_input("Localização", value=profile.get("localizacao", ""))
            email = st.text_input("E-mail", value=profile.get("email", ""))
        with col2:
            telefone = st.text_input("Telefone", value=profile.get("telefone", ""))
            linkedin = st.text_input("LinkedIn", value=profile.get("linkedin", ""))
            idiomas_txt = st.text_area("Idiomas — um por linha", value="\n".join(profile.get("idiomas", [])), height=110)
        resumo = st.text_area("Resumo profissional", value=profile.get("resumo", ""), height=140)
        competencias_txt = st.text_area("Competências — uma por linha", value="\n".join(profile.get("competencias", [])), height=180)
        experiencias_txt = st.text_area("Experiências-chave — uma por linha", value="\n".join(profile.get("experiencias_chave", [])), height=160)
        prefs = profile.get("preferencias", {}) or {}
        col3, col4, col5 = st.columns(3)
        with col3:
            cargos_txt = st.text_area("Cargos-alvo — um por linha", value="\n".join(prefs.get("cargos_alvo", [])), height=140)
        with col4:
            modelos_txt = st.text_area("Modelos preferidos — um por linha", value="\n".join(prefs.get("modelo", [])), height=140)
        with col5:
            senioridade_txt = st.text_area("Senioridade — uma por linha", value="\n".join(prefs.get("senioridade", [])), height=140)

        salvar = st.form_submit_button("💾 Salvar perfil")
        if salvar:
            new_profile = {
                "nome": nome,
                "headline": headline,
                "localizacao": localizacao,
                "email": email,
                "telefone": telefone,
                "linkedin": linkedin,
                "resumo": resumo,
                "competencias": [x.strip() for x in competencias_txt.splitlines() if x.strip()],
                "experiencias_chave": [x.strip() for x in experiencias_txt.splitlines() if x.strip()],
                "idiomas": [x.strip() for x in idiomas_txt.splitlines() if x.strip()],
                "preferencias": {
                    "cargos_alvo": [x.strip() for x in cargos_txt.splitlines() if x.strip()],
                    "modelo": [x.strip() for x in modelos_txt.splitlines() if x.strip()],
                    "senioridade": [x.strip() for x in senioridade_txt.splitlines() if x.strip()],
                },
            }
            save_profile(new_profile)
            st.success("Perfil salvo com sucesso.")
            st.rerun()

elif page == "Analisar vaga":
    st.subheader("🔎 Analisar vaga")
    st.write("Cole um link público ou um link do LinkedIn. Para LinkedIn, o app abre a página para você copiar o texto visível e depois extrair os campos automaticamente a partir do texto colado.")

    link = st.text_input("Link da vaga", placeholder="https://www.linkedin.com/jobs/view/... ou site da empresa")
    c1, c2, c3 = st.columns([1,1,1])

    with c1:
        if st.button("🌐 Abrir link no navegador", use_container_width=True, disabled=not link):
            webbrowser.open_new_tab(link)
            st.success("Link aberto no navegador padrão.")

    with c2:
        if st.button("🔍 Buscar dados de página pública", use_container_width=True, disabled=not link):
            result = fetch_public_page(link)
            if result.get("ok"):
                fields = extract_job_fields(result.get("text", ""), link)
                st.session_state["job_fields"] = fields
                st.success("Dados extraídos da página pública.")
            else:
                st.warning(result.get("error", "Não foi possível buscar os dados."))

    with c3:
        if st.button("📋 Ler texto da área de transferência", use_container_width=True):
            if pyperclip:
                try:
                    txt = pyperclip.paste()
                    fields = extract_job_fields(txt, link)
                    st.session_state["job_fields"] = fields
                    st.success("Texto da área de transferência processado.")
                except Exception as e:
                    st.error(f"Não consegui ler a área de transferência: {e}")
            else:
                st.error("Biblioteca pyperclip não instalada. Use o campo manual abaixo.")

    if link and is_linkedin(link):
        st.info("LinkedIn assistido: faça login no seu navegador, abra o link, copie o texto visível da vaga e cole abaixo. O app não faz scraping massivo nem captura credenciais.")

    st.divider()
    st.markdown("### Captura manual / LinkedIn")
    raw_text = st.text_area("Cole aqui o texto copiado da vaga", height=260, placeholder="Cole título, empresa, localização, descrição e requisitos...")
    if st.button("🧠 Extrair campos do texto colado", disabled=not raw_text):
        st.session_state["job_fields"] = extract_job_fields(raw_text, link)
        st.success("Campos extraídos. Revise abaixo antes de analisar.")

    fields = st.session_state.get("job_fields", {"cargo":"", "empresa":"", "local":"", "modalidade":"", "requisitos":"", "descricao":"", "link": link})
    st.markdown("### Campos da vaga")
    col1, col2 = st.columns(2)
    with col1:
        cargo = st.text_input("Cargo", value=fields.get("cargo", ""))
        empresa = st.text_input("Empresa", value=fields.get("empresa", ""))
        local = st.text_input("Local", value=fields.get("local", ""))
        modalidade = st.text_input("Modalidade", value=fields.get("modalidade", ""))
    with col2:
        requisitos = st.text_area("Requisitos", value=fields.get("requisitos", ""), height=180)
    descricao = st.text_area("Descrição completa", value=fields.get("descricao", ""), height=260)

    job = {"cargo": cargo, "empresa": empresa, "local": local, "modalidade": modalidade, "requisitos": requisitos, "descricao": descricao, "link": link}

    if st.button("✅ Calcular aderência e gerar materiais", type="primary"):
        analysis = analyze_match(job, profile)
        st.session_state["analysis"] = analysis
        st.session_state["job"] = job

    if "analysis" in st.session_state:
        analysis = st.session_state["analysis"]
        job = st.session_state["job"]
        st.metric("Score de aderência", f"{analysis['score']}%")
        st.success(analysis["recomendacao"])
        a, b = st.columns(2)
        with a:
            st.markdown("#### Competências encontradas")
            st.write(analysis.get("competencias_encontradas") or "Nenhuma competência encontrada automaticamente.")
        with b:
            st.markdown("#### Gaps / pontos de revisão")
            st.write(analysis.get("gaps") or "Sem gaps relevantes.")

        st.markdown("#### Mensagem para recrutador")
        st.text_area("Mensagem", value=recruiter_message(job, profile, analysis), height=230)
        st.markdown("#### Resumo da candidatura")
        st.text_area("Resumo", value=application_summary(job, profile, analysis), height=260)

        status = st.selectbox("Status da candidatura", ["Analisada", "Aplicar", "Aplicada", "Networking", "Descartada", "Entrevista"])
        if st.button("💾 Salvar no pipeline"):
            append_pipeline({
                "data": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "cargo": job.get("cargo", ""),
                "empresa": job.get("empresa", ""),
                "local": job.get("local", ""),
                "link": job.get("link", ""),
                "score": analysis.get("score", ""),
                "recomendacao": analysis.get("recomendacao", ""),
                "status": status,
            })
            st.success("Candidatura salva no pipeline.")

elif page == "Pipeline":
    st.subheader("📊 Pipeline de candidaturas")
    df = load_pipeline()
    st.dataframe(df, use_container_width=True)
    st.download_button("⬇️ Baixar pipeline CSV", df.to_csv(index=False).encode("utf-8-sig"), "pipeline_vagas.csv", "text/csv")

elif page == "Instruções":
    st.subheader("📌 Como usar")
    st.markdown("""
1. Acesse **Meu perfil** e edite suas informações profissionais.
2. Em **Analisar vaga**, cole o link da vaga.
3. Se for site público da empresa, clique em **Buscar dados de página pública**.
4. Se for LinkedIn, clique em **Abrir link no navegador**, faça login normalmente no seu navegador, copie o texto visível da vaga e cole no campo manual.
5. Clique em **Extrair campos do texto colado**.
6. Revise os campos e clique em **Calcular aderência e gerar materiais**.
7. Salve no pipeline.

Observação: esta versão evita captura automática de credenciais e scraping massivo. O fluxo do LinkedIn é assistido e depende da sua ação manual de copiar o texto visível.
""")
