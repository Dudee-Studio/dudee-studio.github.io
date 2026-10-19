#!/usr/bin/env python3
"""Verify bilingual task guides, search, links and no-script fallback."""
import hashlib,json,sys
from pathlib import Path
from PIL import Image
from playwright.sync_api import sync_playwright
root=Path(__file__).resolve().parents[1]
base=(sys.argv[1] if len(sys.argv)>1 else 'http://127.0.0.1:8766').rstrip('/')
data=json.loads((root/'assets/abgehakt/help-usecases.json').read_text())
assert len(data['cases'])==42
source=root.parent/'Einkaufsliste/app/src/main/assets/help-usecases.json'
if source.exists():assert source.read_bytes()==(root/'assets/abgehakt/help-usecases.json').read_bytes()
assets=set()
for case in data['cases']:
 for lang in data['languages']:
  pictures=case[lang]['images'];assert len(pictures)>=2,(case['id'],lang)
  for picture in pictures:
   assert picture['src'].startswith('help-images/'+lang+'/')
   path=root/'assets/abgehakt'/picture['src']
   with Image.open(path) as im:
    assert im.size==(picture['width'],picture['height']);im.load()
   x,y,w,h=picture['focus'];assert 0<=x<1 and 0<=y<1 and 0<w<=1 and 0<h<=1 and x+w<=1.000001 and y+h<=1.000001
   if source.exists():assert path.read_bytes()==(source.parent/picture['src']).read_bytes()
   assets.add(picture['src'])
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
     assert box.locator('.help-step-text').all_text_contents()==c[lang]['steps']
     assert box.locator('.help-shot').count()==len(c[lang]['images'])
     for link in box.locator('.help-shot').all():assert ('/help-images/'+lang+'/') in link.get_attribute('href')
    # Open the same complete app frame and its highlight together, then navigate the sequence.
    first=page.locator('#sprache .help-shot').first
    first.click()
    viewer=page.locator('#help-image-viewer');assert viewer.is_visible()
    picture=viewer.locator('img');picture.evaluate('(i)=>i.decode()')
    geom=viewer.locator('.help-shot-frame').bounding_box();focus=viewer.locator('.help-focus').bounding_box()
    assert focus['x']>=geom['x']-1 and focus['y']>=geom['y']-1
    assert focus['x']+focus['width']<=geom['x']+geom['width']+1
    assert focus['y']+focus['height']<=geom['y']+geom['height']+1
    assert picture.evaluate('(i)=>getComputedStyle(i).objectFit')=='contain'
    expected=data['cases'][next(i for i,c in enumerate(data['cases']) if c['id']=='sprache')][lang]['images'][0]
    assert abs(geom['width']/geom['height']-expected['width']/expected['height'])<.01
    caption=page.locator('#help-image-caption').inner_text()
    page.locator('#help-image-next').click();assert page.locator('#help-image-caption').inner_text()!=caption
    page.keyboard.press('ArrowLeft');assert page.locator('#help-image-caption').inner_text()==caption
    viewer.screenshot(path=str(out/f'viewer-{lang}-{width}-{scheme}.png'))
    page.keyboard.press('Escape');assert not viewer.is_visible();assert first.evaluate('(e)=>e===document.activeElement')
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
 assert page.locator('#sprache .help-shot').count()>=2
 page.locator('#sprache .help-shot').first.click();assert '/help-images/en/' in page.url
 page.go_back()
 page.locator('.language-switch a[lang=de]').click();assert page.url==base+'/hilfe.html'
 ctx.close();b.close()
print(json.dumps({'passed':True,'checks':checks,'image_assets_decoded':len(assets),'multiple_images_in_all_84_guides':True,'app_source_matches':source.exists(),'proof':str(out)},ensure_ascii=False,indent=2))
