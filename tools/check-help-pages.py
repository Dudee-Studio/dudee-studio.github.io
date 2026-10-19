#!/usr/bin/env python3
"""Verify bilingual task guides, search, links and no-script fallback."""
import hashlib,json,sys
from pathlib import Path
from playwright.sync_api import sync_playwright
root=Path(__file__).resolve().parents[1]
base=(sys.argv[1] if len(sys.argv)>1 else 'http://127.0.0.1:8766').rstrip('/')
data=json.loads((root/'assets/abgehakt/help-usecases.json').read_text())
assert len(data['cases'])==42
source=root.parent/'Einkaufsliste/app/src/main/assets/help-usecases.json'
if source.exists():assert source.read_bytes()==(root/'assets/abgehakt/help-usecases.json').read_bytes()
out=Path('/tmp/abgehakt-help-check');out.mkdir(exist_ok=True)
checks=[]
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 for width in [390,1440]:
  for scheme in ['light','dark']:
   page=b.new_page(viewport={'width':width,'height':900},color_scheme=scheme,reduced_motion='reduce')
   errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
   for lang,url in [('de','/hilfe.html'),('en','/en/help.html')]:
    page.goto(base+url+'#sprache')
    assert page.locator('html').get_attribute('lang')==lang
    assert page.locator('.help-case').count()==42
    assert page.locator('#sprache').evaluate('(d)=>d.open')
    assert page.locator('video').count()==0
    for c in data['cases']:
     box=page.locator('#'+c['id'])
     assert box.locator('summary span').inner_text()==c[lang]['title']
     assert box.locator('li').all_text_contents()==c[lang]['steps']
    page.locator('#help-search').fill('coupon')
    assert page.locator('#coupons-abschluss').is_visible()
    assert page.locator('.help-case:visible').count()<42
    page.locator('#help-search').fill('zzzzdoesnotexist')
    assert page.locator('#help-no-results').is_visible()
    assert page.locator('.help-case:visible').count()==0
    page.locator('#help-search').fill('')
    assert page.locator('.help-case:visible').count()==42
    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
    page.screenshot(path=str(out/f'help-{lang}-{width}-{scheme}.png'),full_page=True)
    other='en' if lang=='de' else 'de'
    page.locator(f'.language-switch a[lang={other}]').click()
    assert page.url.endswith(('/en/help.html' if other=='en' else '/hilfe.html')+'#sprache')
    assert page.locator('#sprache').evaluate('(d)=>d.open')
    assert not errors,errors
    checks.append({'language':lang,'width':width,'theme':scheme,'guides':42})
   page.close()
 ctx=b.new_context(java_script_enabled=False);page=ctx.new_page();page.goto(base+'/en/help.html')
 page.locator('#sprache summary').click();assert page.locator('#sprache ol').is_visible()
 page.locator('.language-switch a[lang=de]').click();assert page.url==base+'/hilfe.html'
 ctx.close();b.close()
print(json.dumps({'passed':True,'checks':checks,'app_source_matches':source.exists(),'proof':str(out)},ensure_ascii=False,indent=2))
