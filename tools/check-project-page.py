#!/usr/bin/env python3
"""Smoke-check a locally served site, including the actual MP4 playback.

Start `python tools/serve-preview.py --port 8765`, then run this script.
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
            assert page.locator('track[kind=captions][srclang=de]').count() == 4
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
            assert result['width'] == 1920 and result['height'] == 1080, result
            assert 58.9 <= result['duration'] <= 59.1, result
            assert result['controls'] and not result['autoplay'] and not result['paused'], result
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), 'Horizontal overflow'
            page.wait_for_function('document.querySelector("video").currentTime > 0.8')
            # Switching formats pauses the previous film; portrait keeps its real aspect ratio.
            portrait = page.locator('.video-portrait video')
            assert not portrait.is_visible()
            page.get_by_text('Hochformat', exact=True).click()
            assert page.locator('#format-portrait').is_checked()
            assert page.locator('video').first.evaluate('(v) => v.paused')
            assert not page.locator('video').first.is_visible()
            assert portrait.is_visible()
            assert portrait.get_attribute('autoplay') is None
            assert portrait.get_attribute('controlslist') == 'nodownload'
            portrait.evaluate('(v) => v.load()')
            page.wait_for_function('document.querySelector(".video-portrait video").readyState >= 2')
            assert portrait.evaluate('(v) => v.videoWidth') == 1080
            assert portrait.evaluate('(v) => v.videoHeight') == 1920
            assert 58.9 <= portrait.evaluate('(v) => v.duration') <= 59.1
            portrait.evaluate('(v) => v.textTracks[0].mode = "showing"')
            page.wait_for_function('document.querySelector(".video-portrait video").textTracks[0].cues?.length > 0')
            assert portrait.evaluate(r'(v) => Array.from(v.textTracks[0].cues).some(c => c.startTime >= 56 && c.text.replace(/\s+/g, " ").includes("separaten Video"))')
            box = page.locator('.video-portrait').bounding_box()
            assert abs(box['width'] / box['height'] - 9 / 16) < .005, box
            assert box['width'] <= 360.1
            portrait.evaluate('''async v => { v.currentTime = 57.3; await new Promise(r => v.addEventListener('seeked', r, {once:true})); }''')
            portrait.screenshot(path=f'/tmp/abgehakt-portrait-{width}-{mode}.png')
            portrait.evaluate('(v) => v.play()')
            page.wait_for_function('document.querySelector(".video-portrait video").currentTime > 57.5')
            page.get_by_text('Querformat', exact=True).click()
            assert portrait.evaluate('(v) => v.paused')
            assert not portrait.is_visible()
            assert page.locator('video').first.is_visible()
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
            assert 25.8 <= teaser.evaluate('(v) => v.duration') <= 26.2
            page.locator('video').first.evaluate('(v) => v.play()')
            teaser.evaluate('(v) => v.play()')
            page.wait_for_function('document.querySelector(".teaser-details video").currentTime > 0.8')
            assert page.locator('video').first.evaluate('(v) => v.paused'), 'Concurrent audio playback'
            teaser.evaluate('(v) => v.pause()')
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), 'Teaser overflow'
            page.locator('.catalog-details summary').click()
            catalog = page.locator('.catalog-details video')
            assert catalog.get_attribute('controlslist') == 'nodownload'
            assert catalog.get_attribute('autoplay') is None
            catalog.evaluate('(v) => v.load()')
            page.wait_for_function('document.querySelector(".catalog-details video").readyState >= 2')
            assert abs(catalog.evaluate('(v) => v.duration') - 22) < .1
            assert catalog.evaluate('(v) => v.videoWidth') == 1280
            catalog.evaluate('(v) => v.textTracks[0].mode = "hidden"')
            page.wait_for_function('document.querySelector(".catalog-details video").textTracks[0].cues?.length > 0')
            teaser.evaluate('(v) => v.play()')
            catalog.evaluate('(v) => v.play()')
            page.wait_for_function('document.querySelector(".catalog-details video").currentTime > .5')
            assert teaser.evaluate('(v) => v.paused'), 'Concurrent catalogue and Pro audio'
            catalog.evaluate('(v) => v.pause()')
            catalog.evaluate('''async v => { v.currentTime = 7; await new Promise(r => v.addEventListener('seeked', r, {once:true})); }''')
            assert abs(catalog.evaluate('(v) => v.currentTime') - 7) < .1
            catalog.evaluate('(v) => v.play()')
            page.wait_for_function('document.querySelector(".catalog-details video").currentTime > 7.1')
            catalog.evaluate('(v) => v.pause()')
            catalog.screenshot(path=f'/tmp/catalog-video-{width}-{mode}.png')
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), 'Catalogue overflow'
            assert not errors, errors
            page.goto(base + '/')
            page.locator('.card').click()
            assert page.url.endswith('projekte.html#einkaufsliste'), page.url
            assert page.locator('.project').count() == 1
            print(json.dumps({'viewport': width, 'theme': mode, **result}))
            page.close()
    browser.close()
