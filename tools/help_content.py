"""Render the app's shared help content as static, accessible web pages."""
from pathlib import Path
import html,json
R=Path(__file__).resolve().parents[1]
def document(language):
    en=language=='en';data=json.loads((R/'assets/abgehakt/help-usecases.json').read_text());esc=html.escape
    title='Help & guides' if en else 'Hilfe & Anleitungen'
    intro='Choose a task. Follow the steps in the app.' if en else 'Wähle eine Aufgabe. Folge den Schritten in der App.'
    search='Search guides' if en else 'Anleitungen suchen'
    none='No matching guides.' if en else 'Keine passende Anleitung.'
    body=f'<h1 class="page-title">Abgehakt · {title}</h1><p class="help-intro">{intro}</p><label class="help-search" for="help-search">{search}<input id="help-search" type="search" autocomplete="off" aria-controls="help-topics"></label><p id="help-no-results" hidden role="status">{none}</p><div id="help-topics">'
    for group,labels in data['groups'].items():
        body+=f'<section class="help-group" aria-labelledby="help-group-{group}"><h2 id="help-group-{group}">{esc(labels[language])}</h2>'
        for item in data['cases']:
            if item['group']!=group:continue
            copy=item[language];access=data['access'][item['access']][language]
            body+=f'<details class="help-case" id="{item["id"]}"><summary><span>{esc(copy["title"])}</span><small>{esc(access)}</small></summary><ol>'+''.join(f'<li>{esc(step)}</li>' for step in copy['steps'])+'</ol>'
            if copy['note']:body+=f'<p class="help-note">{esc(copy["note"])}</p>'
            body+='</details>'
        body+='</section>'
    body+='</div>'
    back='Back to Abgehakt' if en else 'Zurück zu Abgehakt';path='/en/projects.html' if en else '/projekte.html'
    body+=f'<p class="help-back"><a href="{path}#einkaufsliste">{back}</a></p>'
    return f'''<!doctype html>
<html lang="{language}">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover"><title>Abgehakt · {title} | Dudee Studio</title><meta name="description" content="{intro}"><link rel="stylesheet" href="/style.css?v=12"></head>
<body><div class="wrap"><header class="top"></header><main class="help-page">{body}</main><footer></footer></div></body></html>
'''
