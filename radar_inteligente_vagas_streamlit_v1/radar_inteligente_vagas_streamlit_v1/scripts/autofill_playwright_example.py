"""
Exemplo educacional de autofill supervisionado com Playwright.
Use somente em sites onde você tenha autorização.
O envio final da candidatura deve ser manual.
"""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE_DIR = Path(__file__).resolve().parents[1]
PROFILE_PATH = BASE_DIR / "data" / "profile.json"


def main():
    profile = json.loads(PROFILE_PATH.read_text(encoding="utf-8"))
    url = input("Cole a URL do formulário externo da candidatura: ").strip()
    if not url:
        raise SystemExit("URL não informada.")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto(url, wait_until="domcontentloaded")

        # Exemplos genéricos. Ajuste os seletores conforme o site.
        mappings = {
            "input[name='name']": profile.get("nome", ""),
            "input[name='email']": profile.get("email", ""),
            "input[name='phone']": profile.get("telefone", ""),
            "input[name='linkedin']": profile.get("linkedin", ""),
            "textarea[name='summary']": profile.get("resumo", "")
        }

        for selector, value in mappings.items():
            try:
                if value and page.locator(selector).count() > 0:
                    page.locator(selector).first.fill(value)
            except Exception as exc:
                print(f"Não foi possível preencher {selector}: {exc}")

        print("Preenchimento inicial concluído. Revise manualmente antes de enviar.")
        input("Pressione ENTER para fechar o navegador...")
        browser.close()


if __name__ == "__main__":
    main()
