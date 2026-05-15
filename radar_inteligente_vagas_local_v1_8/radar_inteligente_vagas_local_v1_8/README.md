# Radar Inteligente de Vagas AI — Local V1.8

## Como rodar localmente

```bash
cd radar_inteligente_vagas_local_v1_8
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m playwright install chromium
streamlit run app.py
```

## Correções da V1.8

- Corrige o erro `Executable doesn't exist` do Playwright.
- Instala o Chromium automaticamente quando possível.
- Mantém perfil persistente local para login no LinkedIn.
- Inclui fallback seguro: abrir link no navegador padrão e colar texto manualmente.
- Permite editar todo o perfil do candidato dentro do app.
- Transporta texto copiado da vaga para campos específicos.
- Salva pipeline em CSV.

## Observação sobre LinkedIn

A captura automática pode falhar por login, proteção da página ou execução em nuvem. O fluxo mais estável é:

1. Abrir o link no navegador padrão ou navegador persistente local.
2. Fazer login manualmente.
3. Copiar o texto visível da vaga.
4. Colar no app.
5. Clicar em “Transportar texto para campos específicos”.
