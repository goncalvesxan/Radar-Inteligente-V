# Radar Inteligente de Vagas AI — Local V1.5

## Como rodar

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

## Correções da V1.5

- Corrige `FileNotFoundError` do `perfil_candidato.json` em Streamlit Cloud ou execução fora da pasta raiz.
- Cria automaticamente `perfil_candidato.json` e `data/pipeline.csv` caso não existam.
- Usa caminhos absolutos baseados em `Path(__file__).parent`.
- Remove dependência de `lxml`.
- Corrige o fluxo de salvar análise manual.

## Uso recomendado para LinkedIn

Cole o texto visível da vaga na aba **Captura Manual / LinkedIn**. A ferramenta não faz scraping massivo no LinkedIn.


## V1.5 - Abertura assistida do LinkedIn

- Cole o link da vaga do LinkedIn na aba **Captura Manual / LinkedIn**.
- Clique em **Abrir página da vaga no LinkedIn**.
- A página será aberta em nova aba do navegador.
- Copie manualmente o texto visível da vaga e cole no campo de análise.
- O app calcula aderência, gera mensagem e salva no pipeline.

Essa implementação não faz scraping do LinkedIn. Ela apenas abre o link e processa o texto fornecido manualmente pelo usuário.
