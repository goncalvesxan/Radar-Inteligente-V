# Radar Inteligente de Vagas AI — Local V1.6

## Recursos
- Link público: busca e extração básica de informações.
- LinkedIn assistido: abre o link no navegador, você copia o texto visível e o app organiza nos campos.
- Perfil editável dentro do Streamlit.
- Score de aderência.
- Mensagem para recrutador.
- Resumo da candidatura.
- Pipeline em CSV.

## Rodar localmente
```bash
cd radar_inteligente_vagas_local_v1_6
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

## Observação sobre LinkedIn
Esta versão não faz scraping massivo e não captura senha/token. O app abre o link, e a extração ocorre a partir do texto que você copia manualmente da página visível.
