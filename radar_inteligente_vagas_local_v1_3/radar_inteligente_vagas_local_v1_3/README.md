# Radar Inteligente de Vagas AI — Local V1.3

## Rodar
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

## Recursos
- Busca de detalhes por link público de sites externos.
- Captura manual para LinkedIn.
- Score de aderência.
- Mensagem para recrutador.
- Resumo para candidatura.
- Pipeline CSV.
- Extensão Chrome local opcional para copiar texto visível.

## Extensão Chrome local
1. Abra `chrome://extensions/`.
2. Ative o modo desenvolvedor.
3. Clique em "Carregar sem compactação".
4. Selecione a pasta `browser_extension_linkedin_capture`.
5. Abra a vaga no LinkedIn e clique na extensão para copiar o texto visível.
