# Radar Inteligente de Vagas AI — Local V1.4

## Como rodar

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

## Correções da V1.4

- Corrige `FileNotFoundError` do `perfil_candidato.json` em Streamlit Cloud ou execução fora da pasta raiz.
- Cria automaticamente `perfil_candidato.json` e `data/pipeline.csv` caso não existam.
- Usa caminhos absolutos baseados em `Path(__file__).parent`.
- Remove dependência de `lxml`.
- Corrige o fluxo de salvar análise manual.

## Uso recomendado para LinkedIn

Cole o texto visível da vaga na aba **Captura Manual / LinkedIn**. A ferramenta não faz scraping massivo no LinkedIn.
