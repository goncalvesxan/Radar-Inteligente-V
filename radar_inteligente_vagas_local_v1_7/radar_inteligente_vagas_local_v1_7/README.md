# Radar Inteligente de Vagas AI — Local V1.7

## Rodar localmente

```bash
cd radar_inteligente_vagas_local_v1_7
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m playwright install chromium
streamlit run app.py
```

## O que foi corrigido na V1.7

- Botão direto para abrir o link no navegador padrão.
- Botão `Abrir link direto`, que funciona melhor no navegador do usuário.
- Navegador local assistido com Playwright usando perfil persistente.
- Permite login no LinkedIn dentro da janela local.
- Captura do texto visível da página aberta.
- Transporte automático para os campos: cargo, empresa, local, modalidade, senioridade, descrição e requisitos.
- Tela completa para editar perfil do candidato.
- Pipeline de candidaturas em CSV.

## Observação

A captura do LinkedIn é supervisionada e local: você abre a página, faz login e aciona a captura. O sistema não realiza scraping em massa, não envia candidaturas automaticamente e não automatiza conexões ou mensagens.
