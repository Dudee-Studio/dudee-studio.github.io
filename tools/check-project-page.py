#!/usr/bin/env python3
"""Check DE/EN navigation, visible video previews, captions and actual playback.

Start `python tools/serve-preview.py --port 8766`, then run this script.
Uses locally installed Playwright/Chromium; the site itself has no dependencies.
"""
import json
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

base = (sys.argv[1] if len(sys.argv) > 1 else 'http://127.0.0.1:8766').rstrip('/')
root = Path(__file__).resolve().parents[1]
films = json.loads((root / 'videos/library.json').read_text())['films']
pairs = [('/', '/en/'), ('/projekte.html', '/en/projects.html'), ('/apps.html', '/en/apps.html'),
         ('/games.html', '/en/games.html'), ('/apps/abgehakt.html', '/en/apps/abgehakt.html'),
         ('/kontakt.html', '/en/contact.html'), ('/impressum.html', '/en/legal.html'),
         ('/datenschutz.html', '/en/privacy.html'), ('/hilfe.html','/en/help.html')]
proof = Path('/tmp/abgehakt-site-check'); proof.mkdir(exist_ok=True)
results = []
with sync_playwright() as p:
    browser = p.chromium.launch(executable_path='/usr/bin/chromium', args=['--no-sandbox'])
    for width, height in [(390, 844), (1440, 1000)]:
        for mode in ['light', 'dark']:
            page = browser.new_page(viewport={'width': width, 'height': height}, color_scheme=mode,
                                    reduced_motion='reduce')
            errors = []
            page.on('pageerror', lambda e: errors.append(str(e)))
            for de, en in pairs:
                for lang, url, other in [('de', de, en), ('en', en, de)]:
                    page.goto(base + url)
                    assert page.locator('html').get_attribute('lang') == lang
                    switch = page.locator('.language-switch')
                    assert switch.is_visible()
                    assert switch.locator('a').count() == 2
                    assert switch.locator('[aria-current=true]').inner_text() == lang.upper()
                    assert switch.locator('a').filter(has_text='EN' if lang == 'de' else 'DE').get_attribute('href') == other
                    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), url
                    assert page.locator('link[rel=alternate][hreflang=de]').count() == 1
                    assert page.locator('link[rel=alternate][hreflang=en]').count() == 1
                    for a in page.locator('header.top nav > a, footer nav a').all():
                        href = a.get_attribute('href')
                        assert href.startswith('/en/') == (lang == 'en'), (url, href)
            # A visitor can discover the app and its help through the new tabs.
            for lang in ['de', 'en']:
                prefix='/en' if lang=='en' else ''
                page.goto(base+prefix+'/apps.html')
                assert page.locator('header.top a[aria-current=page]').inner_text()=='Apps'
                page.locator('.card').click()
                assert page.url==base+prefix+'/apps/abgehakt.html'
                assert page.locator('h1').inner_text()=='Abgehakt'
                assert page.locator('.help-link').count()==1
                page.locator('.product-links a').last.click()
                assert page.url==base+('/en/help.html' if lang=='en' else '/hilfe.html')
                page.locator('.breadcrumbs a').last.click()
                assert page.url==base+prefix+'/apps/abgehakt.html'
                page.locator('header.top nav > a').filter(has_text='Games').click()
                assert page.url==base+prefix+'/games.html'
                assert page.locator('header.top a[aria-current=page]').inner_text()=='Games'
            for lang, url in [('de', '/apps/abgehakt.html'), ('en', '/en/apps/abgehakt.html')]:
                page.goto(base + url + '#einkaufsliste')
                assert page.locator('video').count() == 1
                video = page.locator('#abgehakt-player')
                assert video.get_attribute('preload') == 'none'
                assert video.get_attribute('autoplay') is None
                assert video.get_attribute('controlslist') == 'nodownload'
                assert page.locator('a[download]').count() == 0
                cards = page.locator('.video-choice')
                available = [f for f in films if f['language'] == lang]
                assert cards.count() == len(available)
                assert page.locator('.video-choice[aria-current=true]').count() == 1
                assert page.locator('.video-choice[aria-current=true]').get_attribute('data-language') == lang
                for card in cards.all():
                    assert card.is_visible()
                    assert card.get_attribute('data-language') == lang
                    assert card.locator('details').count() == 0
                    card.locator('img').evaluate('(i) => i.decode()')
                    assert 'hochformat' not in card.get_attribute('href')
                # One pass through every source in each language on mobile and desktop.
                for card in cards.all():
                    target = card.get_attribute('href').split('?')[0].lstrip('/')
                    film = next(f for f in films if f['src'] == target)
                    card.click()
                    page.wait_for_function('document.querySelector("video").readyState >= 2 && !document.querySelector("video").paused')
                    result = video.evaluate('(v) => ({duration:v.duration,width:v.videoWidth,height:v.videoHeight})')
                    assert result['width'] == 1920 and result['height'] == 1080, (film, result)
                    assert abs(result['duration'] - film['duration_sec']) < .1, (film, result)
                    assert video.locator('track').get_attribute('srclang') == film['language']
                    video.evaluate('(v) => v.textTracks[0].mode = "hidden"')
                    page.wait_for_function('document.querySelector("video").textTracks[0].cues?.length > 0')
                    cues = video.evaluate('(v) => Array.from(v.textTracks[0].cues).map(c => c.text).join(" ")')
                    if film['id'] == 'analyse':
                        assert 'Vergleiche deine Ausgaben pro Markt.' in ' '.join(cues.split()), cues
                    if film['id'] == 'analyse-en':
                        assert 'Compare your spending by store.' in ' '.join(cues.split()), cues
                    if film['id'] == 'overview-en':
                        assert 'Pro version' in cues, cues
                    assert page.locator('#selected-video-title').inner_text() == card.get_attribute('data-title')
                    assert card.get_attribute('aria-current') == 'true'
                    video.evaluate('(v) => v.pause()')
                # Keyboard selection, language switch with open section, and actual retained captions.
                cards.first.focus(); page.keyboard.press('Enter')
                page.wait_for_function('!document.querySelector("video").paused')
                video.evaluate('(v) => v.pause()')
                assert page.locator('.language-switch a').first.get_attribute('href').endswith('#einkaufsliste')
                page.locator('header.top').screenshot(path=str(proof / f'header-{lang}-{width}-{mode}.png'))
                page.locator('.project-demo').screenshot(path=str(proof / f'gallery-{lang}-{width}-{mode}.png'))
                assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
                assert not errors, errors
                results.append({'language':lang,'viewport':width,'theme':mode,'films_played':len(available)})
            page.close()
    # Static links also work when JavaScript is unavailable.
    context = browser.new_context(java_script_enabled=False)
    page = context.new_page()
    page.goto(base + '/projekte.html')
    page.locator('.language-switch a[lang=en]').click()
    assert page.url == base + '/en/projects.html'
    assert page.locator('video').get_attribute('controls') is not None
    page.locator('.video-choice').first.click()
    assert '.mp4?' in page.url
    context.close(); browser.close()
print(json.dumps({'passed':True,'checks':results,'proof':str(proof)}, ensure_ascii=False, indent=2))
