# Radar Inteligente de Vagas AI - Streamlit V1.1

Correção da V1: o Playwright agora é opcional. O app Streamlit roda sem depender do módulo `playwright`.

## Como rodar localmente

```bash
cd radar_inteligente_vagas_streamlit_v1_1
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

## Dependências principais

- streamlit
- pandas
- python-dotenv
- openai

## Autofill supervisionado opcional

O autofill com Playwright é apenas um exemplo técnico local e supervisionado. Para testar:

```bash
pip install playwright
python -m playwright install
python scripts/autofill_playwright_example.py
```

Não envie candidaturas automaticamente. Revise tudo manualmente.
