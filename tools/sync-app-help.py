#!/usr/bin/env python3
"""Copy the canonical offline app help to the site; translations remain paired."""
from pathlib import Path
import argparse,json,shutil
ap=argparse.ArgumentParser();ap.add_argument('--app-repo',type=Path,default=Path('../Einkaufsliste'));a=ap.parse_args()
source=a.app_repo/'app/src/main/assets/help-usecases.json';data=json.loads(source.read_text())
assert data['languages']==['de','en']
ids=set()
for c in data['cases']:
 assert c['id'] not in ids;ids.add(c['id'])
 assert c['group'] in data['groups'] and c['access'] in data['access']
 for lang in data['languages']:
  assert c[lang]['title'] and len(c[lang]['steps'])>=3
  assert len(c[lang].get('images',[]))>=2,(c['id'],lang)
  for image in c[lang]['images']:
   assert image['src'].startswith('help-images/'+lang+'/')
   assert (a.app_repo/'app/src/main/assets'/image['src']).is_file()
out=Path(__file__).resolve().parents[1]/'assets/abgehakt/help-usecases.json';out.parent.mkdir(exist_ok=True,parents=True);shutil.copy2(source,out)
images=a.app_repo/'app/src/main/assets/help-images'
shutil.copytree(images,out.parent/'help-images',dirs_exist_ok=True)
expected={image['src'] for case in data['cases'] for lang in data['languages'] for image in case[lang]['images']}
for p in (out.parent/'help-images').rglob('*.webp'):
 if str(p.relative_to(out.parent)) not in expected:p.unlink()
print(f'Synced {len(ids)} bilingual guides; run tools/build-language-pages.py next.')
