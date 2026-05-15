"""
Exemplo supervisionado de preenchimento em site externo.
Use apenas em formulários onde você está preenchendo seus próprios dados.
Não envia candidatura automaticamente.
"""
from playwright.sync_api import sync_playwright
import json
from pathlib import Path

schema = json.loads(Path("templates/autofill_schema.json").read_text(encoding="utf-8"))
p = schema["personal"]

url = input("Cole a URL do formulário externo: ").strip()

with sync_playwright() as pw:
    browser = pw.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto(url)
    print("Página aberta. Ajuste os seletores conforme o ATS/site.")

    # Exemplos: adaptar por Workday, Gupy, Greenhouse, Lever etc.
    possible_fields = {
        "input[name='first_name']": p["first_name"],
        "input[name='last_name']": p["last_name"],
        "input[type='email']": p["email"],
        "input[type='tel']": p["phone"],
    }

    for selector, value in possible_fields.items():
        try:
            if value and page.locator(selector).count() > 0:
                page.locator(selector).first.fill(value)
                print(f"Preenchido: {selector}")
        except Exception as exc:
            print(f"Não preenchido {selector}: {exc}")

    input("Revise no navegador. Pressione ENTER para fechar. O envio final deve ser manual.")
    browser.close()
