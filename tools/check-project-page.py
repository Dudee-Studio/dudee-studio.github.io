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
            assert page.get_by_role('heading', name='Abgehakt', exact=True).count() == 1
            page.locator('.app-title img').evaluate('(i) => i.decode()')
            assert page.get_by_text('Dein Einkauf im Griff.', exact=True).count() == 1
            assert page.locator('a[download]').count() == 0
            assert page.locator('track[kind=captions][srclang=de]').count() == 2
            assert page.locator('video').first.get_attribute('controlslist') == 'nodownload'
            assert not page.locator('.feature-details').evaluate('(d) => d.open')
            page.locator('video').first.evaluate('(v) => v.load()')
            page.wait_for_function('document.querySelector("video").readyState >= 2')
            page.locator('video').first.evaluate('(v) => v.textTracks[0].mode = "hidden"')
            page.wait_for_function('document.querySelector("video").textTracks[0].cues?.length > 0')
            result = page.locator('video').first.evaluate('''async v => {
                await v.play();
                return {duration:v.duration, width:v.videoWidth, height:v.videoHeight,
                        autoplay:v.autoplay, controls:v.controls, paused:v.paused};
            }''')
            assert result['width'] == 720 and result['height'] == 1280, result
            assert result['duration'] == 90, result
            assert result['controls'] and not result['autoplay'] and not result['paused'], result
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), 'Horizontal overflow'
            page.wait_for_function('document.querySelector("video").currentTime > 0.8')
            page.locator('video').first.evaluate('(v) => v.pause()')
            page.wait_for_timeout(300)
            page.screenshot(path=f'/tmp/projekte-{width}-{mode}.png', full_page=True)
            page.locator('.feature-details summary').click()
            for image in page.locator('.feature-gallery img').all():
                image.scroll_into_view_if_needed()
                image.evaluate('(i) => i.loading = "eager"')
                image.evaluate('(i) => i.decode()')
            assert page.locator('.feature-gallery img').count() == 3
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), 'Expanded gallery overflow'
            page.screenshot(path=f'/tmp/abgehakt-details-{width}-{mode}.png', full_page=True)
            page.locator('.teaser-details summary').click()
            teaser = page.locator('.teaser-details video')
            assert teaser.get_attribute('controlslist') == 'nodownload'
            teaser.evaluate('(v) => v.load()')
            page.wait_for_function('document.querySelector(".teaser-details video").readyState >= 2')
            assert teaser.evaluate('(v) => v.duration') == 30
            page.locator('video').first.evaluate('(v) => v.play()')
            teaser.evaluate('(v) => v.play()')
            page.wait_for_function('document.querySelector(".teaser-details video").currentTime > 0.8')
            assert page.locator('video').first.evaluate('(v) => v.paused'), 'Concurrent audio playback'
            teaser.evaluate('(v) => v.pause()')
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), 'Teaser overflow'
            assert not errors, errors
            page.goto(base + '/')
            page.locator('.card').click()
            assert page.url.endswith('projekte.html#einkaufsliste'), page.url
            assert page.locator('.project').count() == 1
            print(json.dumps({'viewport': width, 'theme': mode, **result}))
            page.close()
    browser.close()
