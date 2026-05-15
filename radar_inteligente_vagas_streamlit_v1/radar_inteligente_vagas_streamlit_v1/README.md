# Radar Inteligente de Vagas AI - Streamlit V1

Aplicação local em Streamlit para análise de vagas, score de aderência, geração de mensagem ao recrutador, resumo de candidatura e controle de pipeline.

## Como rodar no Windows

```bash
cd radar_inteligente_vagas_streamlit_v1
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

## Como rodar no macOS/Linux

```bash
cd radar_inteligente_vagas_streamlit_v1
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Estrutura

```text
app.py
modules/
  matching.py
  messages.py
  pipeline.py
data/
  profile.json
  pipeline.csv
  vagas_exemplo.csv
scripts/
  autofill_playwright_example.py
templates/
  autofill_schema.json
docs/
  arquitetura.md
requirements.txt
```

## Uso recomendado

1. Abra o Streamlit.
2. Cole cargo, empresa, link e descrição da vaga.
3. Clique em Analisar aderência.
4. Revise o score, competências e gaps.
5. Copie e ajuste a mensagem sugerida.
6. Salve no pipeline.
7. Faça o envio final manualmente.

## Autofill supervisionado

Para instalar os navegadores do Playwright:

```bash
python -m playwright install
```

Para rodar o exemplo:

```bash
python scripts/autofill_playwright_example.py
```

Use apenas em sites onde você tem autorização. Revise tudo antes de enviar.
