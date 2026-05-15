from pathlib import Path
from datetime import datetime
import json
import webbrowser
import pandas as pd
import requests
import streamlit as st
from bs4 import BeautifulSoup

from modules.profile_store import BASE_DIR, PIPELINE_PATH, ensure_files, load_profile, save_profile
from modules.job_parser import parse_job_text, clean_text
from modules.matching import analyze_fit, recruiter_message
from modules.browser_assistant import BrowserAssistant

ensure_files()
st.set_page_config(page_title="Radar Inteligente de Vagas AI V1.7", layout="wide")
st.title("Radar Inteligente de Vagas AI — Local V1.7")
st.caption("Copiloto local para analisar vagas, capturar texto visível com navegador assistido e preencher campos para decisão humana.")

if "job" not in st.session_state:
    st.session_state.job = {"cargo":"", "empresa":"", "local":"", "modalidade":"", "senioridade":"", "descricao":"", "requisitos":"", "link":""}
if "analysis" not in st.session_state:
    st.session_state.analysis = None
if "browser" not in st.session_state:
    st.session_state.browser = None

profile = load_profile()

def save_pipeline(job, analysis, status="Analisada"):
    row = {
        "data": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "cargo": job.get("cargo", ""),
        "empresa": job.get("empresa", ""),
        "local": job.get("local", ""),
        "modalidade": job.get("modalidade", ""),
        "score": analysis.get("score", 0) if analysis else 0,
        "status": status,
        "link": job.get("link", ""),
        "observacoes": analysis.get("recomendacao", "") if analysis else "",
    }
    df_old = pd.read_csv(PIPELINE_PATH) if PIPELINE_PATH.exists() else pd.DataFrame()
    df = pd.concat([df_old, pd.DataFrame([row])], ignore_index=True)
    df.to_csv(PIPELINE_PATH, index=False)

def fetch_public_url(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, headers=headers, timeout=20)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    for tag in soup(["script", "style", "noscript"]): tag.decompose()
    return clean_text(soup.get_text("\n"))

tabs = st.tabs(["1. Capturar vaga", "2. Análise", "3. Perfil", "4. Pipeline", "5. Ajuda local"])

with tabs[0]:
    st.subheader("Captura da vaga")
    url = st.text_input("Link da vaga", value=st.session_state.job.get("link", ""), placeholder="Cole aqui o link do LinkedIn ou site da empresa")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Abrir link no navegador padrão", use_container_width=True):
            if url:
                webbrowser.open_new_tab(url)
                st.success("Link enviado ao navegador padrão. Se estiver no Streamlit Cloud, use o botão/link abaixo.")
            else:
                st.warning("Cole um link primeiro.")
        if url:
            st.link_button("Abrir link direto", url, use_container_width=True)
    with col2:
        if st.button("Iniciar navegador local assistido", use_container_width=True):
            try:
                browser = BrowserAssistant(BASE_DIR)
                browser.start(url or "https://www.linkedin.com/jobs/")
                st.session_state.browser = browser
                st.success("Navegador local aberto. Faça login no LinkedIn se necessário e deixe a vaga aberta.")
            except Exception as exc:
                st.error(f"Não consegui iniciar o navegador local: {exc}")
                st.info("Execute também: python -m playwright install chromium")
    with col3:
        if st.button("Capturar texto da página aberta", use_container_width=True):
            try:
                browser = st.session_state.browser
                if browser is None:
                    browser = BrowserAssistant(BASE_DIR)
                    browser.start(url or "https://www.linkedin.com/jobs/")
                    st.session_state.browser = browser
                raw = browser.capture_visible_text()
                current_url = browser.current_url() or url
                job = parse_job_text(raw, current_url)
                st.session_state.job.update(job)
                st.success("Texto visível capturado e transportado para os campos abaixo.")
            except Exception as exc:
                st.error(f"Não foi possível capturar a página aberta: {exc}")
                st.info("Confirme que o navegador local foi iniciado, que você está logado e que a página da vaga está visível.")

    st.divider()
    st.markdown("### Captura por site público")
    if st.button("Buscar detalhes pelo link público", use_container_width=True):
        if not url:
            st.warning("Cole um link primeiro.")
        elif "linkedin.com" in url.lower():
            st.warning("Para LinkedIn, use o navegador local assistido ou cole o texto copiado. O app não faz scraping massivo do LinkedIn.")
        else:
            try:
                raw = fetch_public_url(url)
                st.session_state.job.update(parse_job_text(raw, url))
                st.success("Dados extraídos do site público.")
            except Exception as exc:
                st.error(f"Falha ao buscar site público: {exc}")

    st.divider()
    st.markdown("### Colar texto manualmente")
    pasted = st.text_area("Cole aqui o texto copiado da vaga", height=220)
    if st.button("Transportar texto colado para os campos", use_container_width=True):
        st.session_state.job.update(parse_job_text(pasted, url))
        st.success("Texto processado e campos atualizados.")

    st.divider()
    st.markdown("### Campos identificados")
    j = st.session_state.job
    c1, c2 = st.columns(2)
    with c1:
        j["cargo"] = st.text_input("Cargo", value=j.get("cargo", ""))
        j["empresa"] = st.text_input("Empresa", value=j.get("empresa", ""))
        j["local"] = st.text_input("Local", value=j.get("local", ""))
    with c2:
        j["modalidade"] = st.text_input("Modalidade", value=j.get("modalidade", ""))
        j["senioridade"] = st.text_input("Senioridade", value=j.get("senioridade", ""))
        j["link"] = st.text_input("Link original", value=url or j.get("link", ""))
    j["descricao"] = st.text_area("Descrição completa", value=j.get("descricao", ""), height=260)
    j["requisitos"] = st.text_area("Requisitos / responsabilidades", value=j.get("requisitos", ""), height=180)
    st.session_state.job = j

with tabs[1]:
    st.subheader("Análise de aderência")
    if st.button("Analisar vaga", type="primary", use_container_width=True):
        st.session_state.analysis = analyze_fit(st.session_state.job, load_profile())
    analysis = st.session_state.analysis
    if analysis:
        c1, c2, c3 = st.columns(3)
        c1.metric("Score", f"{analysis['score']}%")
        c2.metric("Competências encontradas", len(analysis["competencias_encontradas"]))
        c3.metric("Gaps mapeados", len(analysis["gaps"]))
        st.success(analysis["recomendacao"])
        st.markdown("#### Competências encontradas")
        st.write(", ".join(analysis["competencias_encontradas"]) or "Nenhuma competência principal encontrada.")
        st.markdown("#### Gaps")
        st.write(", ".join(analysis["gaps"]) or "Sem gaps relevantes na base atual.")
        st.markdown("#### Mensagem sugerida ao recrutador")
        st.text_area("Mensagem", recruiter_message(st.session_state.job, load_profile(), analysis), height=160)
        if st.button("Salvar no pipeline", use_container_width=True):
            save_pipeline(st.session_state.job, analysis)
            st.success("Registro salvo no pipeline.")
    else:
        st.info("Capture ou preencha uma vaga e clique em Analisar vaga.")

with tabs[2]:
    st.subheader("Configuração do meu perfil")
    p = load_profile()
    p["nome"] = st.text_input("Nome", p.get("nome", ""))
    p["titulo"] = st.text_input("Título profissional", p.get("titulo", ""))
    colA, colB = st.columns(2)
    with colA:
        p["email"] = st.text_input("E-mail", p.get("email", ""))
        p["telefone"] = st.text_input("Telefone", p.get("telefone", ""))
        p["cidade"] = st.text_input("Cidade", p.get("cidade", ""))
    with colB:
        p["linkedin"] = st.text_input("LinkedIn", p.get("linkedin", ""))
        p["pretensao_salarial"] = st.text_input("Pretensão salarial", p.get("pretensao_salarial", ""))
        p["disponibilidade"] = st.text_input("Disponibilidade", p.get("disponibilidade", ""))
    p["resumo"] = st.text_area("Resumo profissional", p.get("resumo", ""), height=140)
    p["competencias"] = [x.strip() for x in st.text_area("Competências, uma por linha", "\n".join(p.get("competencias", [])), height=180).splitlines() if x.strip()]
    p["cargos_alvo"] = [x.strip() for x in st.text_area("Cargos-alvo, um por linha", "\n".join(p.get("cargos_alvo", [])), height=120).splitlines() if x.strip()]
    p["setores_alvo"] = [x.strip() for x in st.text_area("Setores-alvo, um por linha", "\n".join(p.get("setores_alvo", [])), height=100).splitlines() if x.strip()]
    if st.button("Salvar perfil", type="primary", use_container_width=True):
        save_profile(p)
        st.success("Perfil salvo com sucesso.")

with tabs[3]:
    st.subheader("Pipeline de candidaturas")
    df = pd.read_csv(PIPELINE_PATH) if PIPELINE_PATH.exists() else pd.DataFrame()
    st.dataframe(df, use_container_width=True, hide_index=True)
    st.download_button("Baixar pipeline CSV", data=df.to_csv(index=False).encode("utf-8-sig"), file_name="pipeline_candidaturas.csv", mime="text/csv")

with tabs[4]:
    st.subheader("Como usar a captura do LinkedIn")
    st.markdown("""
1. Cole o link da vaga do LinkedIn.
2. Clique em **Iniciar navegador local assistido**.
3. Faça login no LinkedIn dentro da janela aberta, se necessário.
4. Deixe a página da vaga aberta e carregada.
5. Volte ao Streamlit e clique em **Capturar texto da página aberta**.
6. Revise os campos e clique em **Analisar vaga**.

Para instalar o navegador do Playwright, execute uma vez no terminal:
```bash
python -m playwright install chromium
```

Observação: esta versão é local e supervisionada. Ela não dispara candidaturas nem mensagens automaticamente.
""")
