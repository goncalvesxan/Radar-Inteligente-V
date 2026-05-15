"""
Exemplo educacional de autofill supervisionado com Playwright.

Importante:
- Este arquivo NÃO é necessário para rodar o app Streamlit.
- O Playwright é opcional e deve ser instalado somente se você for testar autofill localmente.
- Não use para envio automático de candidaturas.
"""

from pathlib import Path
import json

BASE_DIR = Path(__file__).resolve().parents[1]
PROFILE_PATH = BASE_DIR / "data" / "profile.json"


def load_profile():
    with open(PROFILE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def run_supervised_autofill(url: str):
    try:
        from playwright.sync_api import sync_playwright
    except ModuleNotFoundError as exc:
        raise SystemExit(
            "Playwright não está instalado. Rode: pip install playwright && python -m playwright install"
        ) from exc

    profile = load_profile()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto(url)

        # Exemplos genéricos. Ajuste seletores conforme o site externo.
        candidate = profile.get("candidate", {})
        field_map = {
            "input[name='name']": candidate.get("name", ""),
            "input[name='email']": candidate.get("email", ""),
            "input[name='phone']": candidate.get("phone", ""),
            "input[name='linkedin']": candidate.get("linkedin", ""),
        }

        for selector, value in field_map.items():
            try:
                if value and page.locator(selector).count() > 0:
                    page.locator(selector).first.fill(value)
            except Exception:
                pass

        input("Revise o formulário no navegador. Pressione ENTER aqui para encerrar sem enviar automaticamente...")
        browser.close()


if __name__ == "__main__":
    target_url = input("Cole a URL do formulário externo: ").strip()
    if not target_url:
        raise SystemExit("URL não informada.")
    run_supervised_autofill(target_url)
