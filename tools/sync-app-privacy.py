#!/usr/bin/env python3
"""Keep the app policy in the existing website page; preserve hosting and navigation."""
import argparse
import importlib.util
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('--app-repo', type=Path, default=Path('../Einkaufsliste'))
args = parser.parse_args()
app = args.app_repo.resolve()
root = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location('app_site_builder', app / 'tools/build_website.py')
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)
source = (app / 'docs/play-store/datenschutz.md').read_text(encoding='utf-8')
# The website has its own page title; nest the app's policy sections below it.
body = builder.markdown(source.split('\n', 1)[1]).replace('<h2 ', '<h3 ').replace('</h2>', '</h3>')
section = '<section aria-labelledby="app-datenschutz"><h2 id="app-datenschutz">Datenschutz der Android-App Abgehakt</h2>\n' + body + '\n      </section>'
page = root / 'datenschutz.html'
html = page.read_text(encoding='utf-8')
start = html.find('<section aria-labelledby="app-datenschutz">')
if start >= 0:
    end = html.index('</section>', start) + len('</section>')
    html = html[:start] + section + html[end:]
else:
    html = html.replace('    </div>\n  </main>', '      <hr>\n      ' + section + '\n    </div>\n  </main>')
page.write_text(html, encoding='utf-8')
