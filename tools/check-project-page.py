#!/usr/bin/env python3
"""Smoke-check a locally served site, including the actual MP4 playback.

Start `python -m http.server 8765`, then run this script.
Needs Playwright and Chromium; no extra JavaScript is installed on the site.
"""
import json
import sys
from playwright.sync_api import sync_playwright

base = sys.argv[1] if len(sys.argv) > 1 else 'http://127.0.0.1:8765'
with sync_playwright() as p:
    browser = p.chromium.launch(executable_path='/usr/bin/chromium', args=['--no-sandbox'])
    for width, height in [(390, 844), (1440, 1000)]:
        for mode in ['light', 'dark']:
            page = browser.new_page(viewport={'width': width, 'height': height}, color_scheme=mode)
            errors = []
            page.on('pageerror', lambda e: errors.append(str(e)))
            page.goto(base + '/projekte.html#einkaufsliste')
            page.screenshot(path=f'/tmp/projekte-poster-{width}-{mode}.png', full_page=True)
            page.locator('video').evaluate('(v) => v.load()')
            page.wait_for_function('document.querySelector("video").readyState >= 2')
            result = page.locator('video').evaluate('''async v => {
                await v.play();
                return {duration:v.duration, width:v.videoWidth, height:v.videoHeight,
                        autoplay:v.autoplay, controls:v.controls, paused:v.paused};
            }''')
            assert result['width'] == 720 and result['height'] == 1280, result
            assert 55 <= result['duration'] <= 70, result
            assert result['controls'] and not result['autoplay'] and not result['paused'], result
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), 'Horizontal overflow'
            page.wait_for_function('document.querySelector("video").currentTime > 0.8')
            page.locator('video').evaluate('(v) => v.pause()')
            page.wait_for_timeout(300)
            page.screenshot(path=f'/tmp/projekte-{width}-{mode}.png', full_page=True)
            assert not errors, errors
            page.goto(base + '/')
            page.locator('.card').click()
            assert page.url.endswith('projekte.html#einkaufsliste'), page.url
            assert page.locator('.project').count() == 1
            print(json.dumps({'viewport': width, 'theme': mode, **result}))
            page.close()
    browser.close()
