# Radar Inteligente de Vagas AI - Streamlit V1.2

## Objetivo
Aplicação local em Streamlit para apoiar busca estratégica de vagas, análise de aderência, geração de mensagens e controle de candidaturas.

## Módulos

### app.py
Interface principal do Streamlit.

### modules/matching.py
Motor de score de aderência entre vaga e perfil.

### modules/messages.py
Geração de mensagem para recrutador e resumo de candidatura.

### modules/pipeline.py
Registro e leitura do pipeline em CSV.

### scripts/autofill_playwright_example.py
Exemplo de autofill supervisionado em sites externos. Não envia candidaturas automaticamente.

## Modelo seguro
A solução trabalha como copiloto supervisionado:
- analisa;
- recomenda;
- gera mensagens;
- registra pipeline;
- ajuda a preencher campos;
- mantém decisão e envio final com o usuário.

## Limites recomendados
Não usar para scraping agressivo, envio massivo, bypass de captcha, automação de login ou ações proibidas por plataformas.
