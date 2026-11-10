"""Run using Python with Playwright installed; serves only the standalone site."""
import functools
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import os
import shutil
import threading

from playwright.sync_api import sync_playwright, expect


ROOT = Path(__file__).resolve().parents[1]
COURSES = [('index.html', '301번 버스'), ('zigzag.html', '지그재그'),
           ('relay.html', '이어달리기'), ('bread.html', '장애물')]


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *_args):
        pass


server = ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(QuietHandler, directory=str(ROOT / 'site')))
thread = threading.Thread(target=server.serve_forever, daemon=True)
thread.start()
base = f'http://127.0.0.1:{server.server_port}'
try:
    with sync_playwright() as p:
        executable = os.environ.get('CHROMIUM_PATH') or shutil.which('chromium')
        launch = {'executable_path': executable} if executable else {}
        browser = p.chromium.launch(headless=True, **launch)
        context = browser.new_context(reduced_motion='reduce')
        requests, errors, responses = [], [], []
        context.on('request', lambda req: requests.append((req.method, req.url)))
        context.on('response', lambda res: responses.append((res.status, res.url)))
        page = context.new_page()
        page.on('pageerror', lambda err: errors.append(str(err)))
        for viewport in [{'width': 1280, 'height': 900}, {'width': 390, 'height': 844}]:
            page.set_viewport_size(viewport)
            page.goto(base + '/index.html')
            page.clock.install()
            for path, name in COURSES:
                page.locator(f'.nav a[href="{path}"]').click()
                expect(page).to_have_url(base + '/' + path)
                expect(page.locator('.nav a[aria-current]')).to_have_text(name)
                assert page.locator('.nav a[href$=".html"]').count() == 4
                assert page.locator('.gate, .crew, .mine, #login, #recBadge').count() == 0
                assert page.evaluate('typeof window.RUNNING_SHEET_URL') == 'undefined'
                assert page.evaluate('typeof window.RunStudent') == 'undefined'
                page.wait_for_function("[...document.querySelectorAll('video')].every(v => v.readyState >= 3 && !v.error)")
                target = float(page.locator('[data-t]').first.text_content())
                # No backend is reachable during measurement.
                context.set_offline(True)
                page.locator('#toggle').click()
                page.clock.fast_forward(600)
                page.locator('#lap').click()
                page.locator('#toggle').click()
                expect(page.locator('#state')).to_have_text('성공')
                expect(page.locator('#laps li')).to_have_count(1)
                assert page.evaluate("!document.getElementById('okClip').paused")
                page.locator('#reset').click()
                expect(page.locator('#state')).to_have_text('대기')
                expect(page.locator('#ss')).to_have_text('00')
                expect(page.locator('#laps li')).to_have_count(0)
                page.locator('#toggle').click()
                page.clock.fast_forward(int((target + 1) * 1000))
                page.locator('#toggle').click()
                expect(page.locator('#state')).to_have_text('실패')
                assert page.evaluate("!document.getElementById('failClip').paused")
                page.locator('#retry').click()
                expect(page.locator('#state')).to_have_text('대기')
                page.keyboard.press('Space')
                expect(page.locator('#state')).to_have_text('러닝 중')
                page.clock.fast_forward(300)
                page.keyboard.press('Space')
                expect(page.locator('#state')).to_have_text('성공')
                page.keyboard.press('Space')
                expect(page.locator('#state')).to_have_text('대기')
                context.set_offline(False)
            page.locator('#buzzSet').click()
            page.keyboard.press('KeyB')
            expect(page.locator('#buzzInfo')).to_contain_text('B')
            assert page.evaluate("localStorage.getItem('running-timer-standalone-buzzer')")
            assert page.evaluate("localStorage.getItem('running-timer-buzzer')") is None
            page.keyboard.press('KeyB')
            expect(page.locator('#state')).to_have_text('러닝 중')
            page.clock.fast_forward(300)
            page.keyboard.press('KeyB')
            expect(page.locator('#state')).to_have_text('성공')
            page.locator('#reset').click()
            page.locator('.nav a[href="index.html"]').click()
            expect(page.locator('#buzzInfo')).to_contain_text('B')
        assert not errors, errors
        assert all(method == 'GET' and url.startswith(base + '/') for method, url in requests), requests
        assert not any(status >= 400 for status, _ in responses), responses
        browser.close()
    print('PASS: desktop/mobile x 4 courses, media, success/failure, laps/reset, keyboard buzzer, offline timers, no login/API/external requests')
finally:
    server.shutdown()
    server.server_close()
    thread.join()
