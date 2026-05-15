import os
import webbrowser
import streamlit as st
import pandas as pd

from modules.core import (
    load_profile, save_profile, extract_job_fields, fetch_public_page,
    score_job, generate_recruiter_message, save_pipeline, load_pipeline_df
)

st.set_page_config(page_title="Radar Inteligente de Vagas AI V1.8", page_icon="🎯", layout="wide")

st.title("🎯 Radar Inteligente de Vagas AI — Local V1.8")
st.caption("Copiloto local para análise de vagas, LinkedIn assistido, perfil editável e pipeline de candidatura.")

if "job_fields" not in st.session_state:
    st.session_state.job_fields = {"cargo":"", "empresa":"", "local":"", "modalidade":"", "senioridade":"", "descricao":"", "link":""}
if "score_info" not in st.session_state:
    st.session_state.score_info = None

profile = load_profile()

def set_job_fields(fields):
    current = st.session_state.job_fields.copy()
    current.update(fields or {})
    st.session_state.job_fields = current

abas = st.tabs(["🔗 Capturar vaga", "🧠 Analisar", "👤 Meu perfil", "📊 Pipeline", "⚙️ Diagnóstico"])

with abas[0]:
    st.subheader("1) Captura por link ou texto copiado")
    st.info("Para LinkedIn, a forma mais estável é abrir a página logado no seu navegador, copiar o texto visível da vaga e colar abaixo. A captura automática pode funcionar localmente quando o perfil do navegador Playwright estiver logado.")

    url = st.text_input("Link da vaga", value=st.session_state.job_fields.get("link", ""), placeholder="Cole aqui o link da vaga")
    c1, c2, c3 = st.columns(3)

    with c1:
        if st.button("🌐 Abrir link no navegador padrão", use_container_width=True):
            if url:
                webbrowser.open_new_tab(url)
                set_job_fields({"link": url})
                st.success("Link enviado ao navegador padrão. Se estiver no Streamlit Cloud, use o link abaixo para abrir no seu navegador.")
            else:
                st.warning("Cole um link primeiro.")
    with c2:
        st.link_button("↗️ Abrir link diretamente", url or "https://www.linkedin.com/jobs/", use_container_width=True)
    with c3:
        if st.button("📥 Buscar página pública", use_container_width=True):
            result = fetch_public_page(url)
            if result.get("ok"):
                set_job_fields(result["fields"])
                st.success("Dados extraídos da página pública.")
            else:
                st.error(result.get("error"))

    st.divider()
    st.subheader("LinkedIn assistido local")
    st.warning("Este modo usa Playwright e tenta instalar o Chromium automaticamente se estiver ausente. Em Streamlit Cloud, a janela visual pode não abrir; em ambiente local funciona melhor.")
    lc1, lc2 = st.columns(2)
    with lc1:
        if st.button("🧭 Abrir LinkedIn com navegador local persistente", use_container_width=True):
            if not url:
                st.warning("Cole o link do LinkedIn primeiro.")
            else:
                with st.spinner("Abrindo navegador local persistente..."):
                    from modules.linkedin_assist import open_linkedin_persistent
                    result = open_linkedin_persistent(url, headless=False)
                if result.get("ok"):
                    set_job_fields({"link": url})
                    st.success(result.get("message", "Página aberta."))
                else:
                    st.error(result.get("error"))
    with lc2:
        if st.button("🔎 Tentar capturar texto do LinkedIn logado", use_container_width=True):
            if not url:
                st.warning("Cole o link do LinkedIn primeiro.")
            else:
                with st.spinner("Tentando capturar texto com sessão local..."):
                    from modules.linkedin_assist import capture_linkedin_headless
                    result = capture_linkedin_headless(url)
                if result.get("ok") and result.get("text"):
                    fields = extract_job_fields(result["text"], url)
                    set_job_fields(fields)
                    st.success("Texto capturado e transportado para os campos. Revise antes de analisar.")
                elif result.get("ok"):
                    st.warning("A página abriu, mas não retornou texto útil. Copie manualmente o texto visível e cole abaixo.")
                else:
                    st.error(result.get("error"))

    st.divider()
    pasted = st.text_area("Cole aqui o texto copiado da página da vaga", height=280, placeholder="Copie o texto visível da vaga no LinkedIn ou no site da empresa e cole aqui.")
    if st.button("🧩 Transportar texto para campos específicos", type="primary", use_container_width=True):
        if pasted.strip():
            fields = extract_job_fields(pasted, url)
            set_job_fields(fields)
            st.success("Texto interpretado e campos preenchidos. Revise abaixo.")
        else:
            st.warning("Cole o texto da vaga primeiro.")

    st.subheader("Campos extraídos / editáveis")
    f = st.session_state.job_fields
    colA, colB = st.columns(2)
    with colA:
        f["cargo"] = st.text_input("Cargo", value=f.get("cargo", ""))
        f["empresa"] = st.text_input("Empresa", value=f.get("empresa", ""))
        f["local"] = st.text_input("Localização", value=f.get("local", ""))
    with colB:
        f["modalidade"] = st.text_input("Modalidade", value=f.get("modalidade", ""))
        f["senioridade"] = st.text_input("Senioridade", value=f.get("senioridade", ""))
        f["link"] = st.text_input("Link original", value=f.get("link", url or ""))
    f["descricao"] = st.text_area("Descrição completa da vaga", value=f.get("descricao", ""), height=300)
    st.session_state.job_fields = f

with abas[1]:
    st.subheader("2) Análise de aderência")
    f = st.session_state.job_fields
    if not f.get("descricao"):
        st.warning("Capture ou cole uma descrição de vaga primeiro.")
    else:
        col1, col2, col3 = st.columns(3)
        col1.metric("Cargo", f.get("cargo") or "Não identificado")
        col2.metric("Empresa", f.get("empresa") or "Não identificada")
        col3.metric("Modalidade", f.get("modalidade") or "Não identificada")

        if st.button("🧠 Calcular aderência", type="primary"):
            st.session_state.score_info = score_job(f.get("descricao", ""), profile)

        if st.session_state.score_info:
            s = st.session_state.score_info
            st.metric("Score de aderência", f"{s['score']}%")
            st.success(s["recommendation"])
            c1, c2 = st.columns(2)
            with c1:
                st.write("**Competências encontradas na vaga**")
                st.write(", ".join(s["matched"]) if s["matched"] else "Nenhuma competência do perfil encontrada de forma literal.")
            with c2:
                st.write("**Possíveis gaps ou termos não encontrados**")
                st.write(", ".join(s["missing"]) if s["missing"] else "Sem gaps relevantes.")

            msg = generate_recruiter_message(f, profile, s)
            st.text_area("Mensagem sugerida ao recrutador", value=msg, height=170)

            resumo = f"""Resumo da candidatura
Cargo: {f.get('cargo')}
Empresa: {f.get('empresa')}
Local: {f.get('local')}
Modalidade: {f.get('modalidade')}
Score: {s['score']}%
Recomendação: {s['recommendation']}
Pontos fortes: {', '.join(s['matched'][:8])}
"""
            st.text_area("Resumo para candidatura", value=resumo, height=180)

            colp1, colp2 = st.columns([2, 1])
            status = colp1.selectbox("Status para salvar no pipeline", ["Mapeada", "Aplicar", "Aplicada", "Networking", "Descartada"])
            notes = st.text_input("Observações")
            if colp2.button("💾 Salvar no pipeline", use_container_width=True):
                save_pipeline(f, s["score"], status, notes)
                st.success("Vaga salva no pipeline.")

with abas[2]:
    st.subheader("3) Configuração editável do seu perfil")
    st.caption("Esses dados alimentam a análise de aderência e a geração de mensagens.")
    with st.form("profile_form"):
        profile["nome"] = st.text_input("Nome", value=profile.get("nome", ""))
        profile["titulo"] = st.text_input("Título profissional", value=profile.get("titulo", ""))
        c1, c2 = st.columns(2)
        profile["email"] = c1.text_input("E-mail", value=profile.get("email", ""))
        profile["telefone"] = c2.text_input("Telefone", value=profile.get("telefone", ""))
        profile["linkedin"] = st.text_input("LinkedIn", value=profile.get("linkedin", ""))
        profile["cidade"] = st.text_input("Cidade / Região", value=profile.get("cidade", ""))
        profile["resumo"] = st.text_area("Resumo profissional", value=profile.get("resumo", ""), height=160)
        comps = st.text_area("Competências - uma por linha", value="\n".join(profile.get("competencias", [])), height=220)
        exps = st.text_area("Experiências-chave - uma por linha", value="\n".join(profile.get("experiencias_chave", [])), height=160)
        idiomas = st.text_area("Idiomas - um por linha", value="\n".join(profile.get("idiomas", [])), height=100)
        c3, c4 = st.columns(2)
        profile["pretensao_salarial"] = c3.text_input("Pretensão salarial", value=profile.get("pretensao_salarial", ""))
        profile["disponibilidade"] = c4.text_input("Disponibilidade", value=profile.get("disponibilidade", ""))
        submitted = st.form_submit_button("💾 Salvar perfil", type="primary")
        if submitted:
            profile["competencias"] = [x.strip() for x in comps.splitlines() if x.strip()]
            profile["experiencias_chave"] = [x.strip() for x in exps.splitlines() if x.strip()]
            profile["idiomas"] = [x.strip() for x in idiomas.splitlines() if x.strip()]
            save_profile(profile)
            st.success("Perfil salvo com sucesso.")

with abas[3]:
    st.subheader("4) Pipeline de candidaturas")
    try:
        df = load_pipeline_df()
        st.dataframe(df, use_container_width=True)
        st.download_button("⬇️ Baixar pipeline CSV", data=df.to_csv(index=False).encode("utf-8-sig"), file_name="pipeline_candidaturas.csv", mime="text/csv")
    except Exception as e:
        st.error(f"Erro ao carregar pipeline: {e}")

with abas[4]:
    st.subheader("5) Diagnóstico do ambiente")
    st.write("Use esta tela quando houver erro do Playwright/Chromium.")
    if st.button("🩺 Verificar Playwright e Chromium"):
        try:
            from modules.linkedin_assist import ensure_playwright_browser, PROFILE_DIR
            ok, msg = ensure_playwright_browser()
            if ok:
                st.success(msg)
            else:
                st.error(msg)
            st.code(f"Perfil persistente local: {PROFILE_DIR}")
        except Exception as e:
            st.error(str(e))
    st.code("python -m playwright install chromium")
    st.caption("Se estiver rodando localmente e a instalação automática falhar, execute o comando acima no terminal do ambiente virtual.")
