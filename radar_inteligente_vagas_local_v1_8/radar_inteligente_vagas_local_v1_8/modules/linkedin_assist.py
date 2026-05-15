import os
import sys
import subprocess
from pathlib import Path

PROFILE_DIR = Path.home() / ".radar_vagas_linkedin_browser"


def ensure_playwright_browser():
    """Instala Chromium do Playwright quando ausente. Evita o erro 'Executable doesn't exist'."""
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            path = p.chromium.executable_path
            if path and Path(path).exists():
                return True, "Chromium do Playwright disponível."
    except Exception:
        pass

    try:
        subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], check=True, timeout=180)
        return True, "Chromium instalado automaticamente."
    except Exception as e:
        return False, f"Não foi possível instalar o navegador do Playwright automaticamente: {e}"


def open_linkedin_persistent(url: str, headless: bool = False):
    """
    Abre LinkedIn com perfil persistente local.
    Se você fizer login uma vez, a sessão tende a permanecer nesse diretório.
    """
    ok, msg = ensure_playwright_browser()
    if not ok:
        return {"ok": False, "error": msg}
    try:
        from playwright.sync_api import sync_playwright
        PROFILE_DIR.mkdir(parents=True, exist_ok=True)
        with sync_playwright() as p:
            browser = p.chromium.launch_persistent_context(
                user_data_dir=str(PROFILE_DIR),
                headless=headless,
                args=["--start-maximized"],
                viewport=None,
            )
            page = browser.new_page() if not browser.pages else browser.pages[0]
            page.goto(url, wait_until="domcontentloaded", timeout=60000)
            # Mantém janela aberta por tempo suficiente em modo local/headful.
            if not headless:
                return {"ok": True, "message": "Página aberta no navegador local. Faça login se necessário e copie o texto visível para o app."}
            text = page.locator("body").inner_text(timeout=30000)
            browser.close()
            return {"ok": True, "text": text}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def capture_linkedin_headless(url: str):
    """
    Tenta capturar texto em modo headless usando o perfil persistente.
    Funciona somente se a sessão local já estiver autenticada e se o LinkedIn entregar o conteúdo.
    """
    return open_linkedin_persistent(url, headless=True)
