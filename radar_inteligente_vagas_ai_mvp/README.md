# Radar Inteligente de Vagas AI

MVP seguro para monitorar vagas, calcular aderência ao perfil, gerar mensagens personalizadas e preparar autofill supervisionado em sites externos de candidatura.

## Importante
- Não faz scraping nem automação dentro do LinkedIn.
- O envio final de candidaturas e mensagens é manual.
- O módulo de autofill é supervisionado e deve ser usado apenas em páginas onde você tem permissão para preencher seus próprios dados.

## Como usar
1. Instale dependências:
```bash
pip install -r requirements.txt
```
2. Configure seu perfil em `data/profile.json`.
3. Cadastre vagas em `data/jobs.csv` ou cole descrições no app.
4. Rode:
```bash
streamlit run app/main.py
```

## Módulos
- `matcher.py`: calcula score de aderência.
- `generator.py`: gera mensagem para recrutador e resumo da candidatura.
- `tracker.py`: registra pipeline de candidatura.
- `autofill_schema.json`: mapeia dados para formulários externos.
