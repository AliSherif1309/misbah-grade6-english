from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import os
import threading
import unittest
from playwright.sync_api import sync_playwright


class QuizTests(unittest.TestCase):
    def test_progress_survives_reload_and_can_be_reset(self):
        server = ThreadingHTTPServer(('127.0.0.1', 0), partial(SimpleHTTPRequestHandler, directory=str(Path(__file__).parent)))
        threading.Thread(target=server.serve_forever, daemon=True).start()
        try:
            with sync_playwright() as runner:
                browser = runner.chromium.launch(channel=os.environ.get('BROWSER_CHANNEL') or None)
                page = browser.new_page(viewport={'width': 390, 'height': 844})
                page.goto(f'http://127.0.0.1:{server.server_port}/index.html')
                page.locator('.question-card').first.locator('button').nth(1).click()
                self.assertEqual(page.locator('#score-board').inner_text(), 'Score: 1 / 5')
                page.reload()
                self.assertEqual(page.locator('#score-board').inner_text(), 'Score: 1 / 5')
                self.assertTrue(page.locator('.question-card').first.locator('button').first.is_disabled())
                page.locator('#restart-quiz').click()
                self.assertEqual(page.locator('#score-board').inner_text(), 'Score: 0 / 5')
                self.assertFalse(page.locator('.question-card').first.locator('button').first.is_disabled())
                page.reload()
                self.assertEqual(page.locator('#score-board').inner_text(), 'Score: 0 / 5')
                browser.close()
        finally:
            server.shutdown()
            server.server_close()


if __name__ == '__main__':
    unittest.main()
