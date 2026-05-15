from pathlib import Path

class BrowserAssistant:
    def __init__(self, base_dir: Path):
        self.base_dir = Path(base_dir)
        self.playwright = None
        self.context = None
        self.page = None

    def available(self):
        try:
            import playwright.sync_api  # noqa
            return True, "Playwright disponível."
        except Exception as exc:
            return False, f"Playwright não instalado: {exc}"

    def start(self, url: str = "https://www.linkedin.com/jobs/"):
        from playwright.sync_api import sync_playwright
        if self.playwright is None:
            self.playwright = sync_playwright().start()
        profile_dir = self.base_dir / "data" / "browser_profile"
        profile_dir.mkdir(parents=True, exist_ok=True)
        if self.context is None:
            self.context = self.playwright.chromium.launch_persistent_context(
                user_data_dir=str(profile_dir),
                headless=False,
                viewport={"width": 1366, "height": 900},
                args=["--start-maximized"],
            )
        self.page = self.context.pages[0] if self.context.pages else self.context.new_page()
        if url:
            self.page.goto(url, wait_until="domcontentloaded", timeout=60000)
        return True

    def open_url(self, url: str):
        if self.page is None:
            self.start(url)
        else:
            self.page.goto(url, wait_until="domcontentloaded", timeout=60000)
        return True

    def current_url(self):
        return self.page.url if self.page else ""

    def capture_visible_text(self):
        if self.page is None:
            raise RuntimeError("Navegador local ainda não foi iniciado.")
        self.page.wait_for_timeout(1500)
        text = self.page.evaluate("""
        () => {
          const selectorsToRemove = ['script','style','noscript','svg','canvas'];
          const clone = document.body.cloneNode(true);
          selectorsToRemove.forEach(sel => clone.querySelectorAll(sel).forEach(e => e.remove()));
          return clone.innerText || '';
        }
        """)
        return text or ""

    def close(self):
        try:
            if self.context:
                self.context.close()
        finally:
            self.context = None
            self.page = None
            if self.playwright:
                self.playwright.stop()
                self.playwright = None
