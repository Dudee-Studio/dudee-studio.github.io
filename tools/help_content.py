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
            body+=f'<details class="help-case" id="{item["id"]}"><summary><span>{esc(copy["title"])}</span><small>{esc(access)}</small></summary><ol>'
            for index,step in enumerate(copy['steps'],1):
                body+=f'<li><p class="help-step-text">{esc(step)}</p>'
                images=[image for image in copy.get('images',[]) if image['step']==index]
                if images:body+='<div class="help-step-images">'
                for image in images:
                    caption=image['caption'];label=f'{"Step" if en else "Schritt"} {index}: {caption}'
                    enlarge=f'{"Enlarge image" if en else "Bild vergrößern"}: {label}'
                    x,y,w,h=image['focus']
                    body+=f'<a class="help-shot" href="/assets/abgehakt/{esc(image["src"])}" data-caption="{esc(label,quote=True)}" aria-label="{esc(enlarge,quote=True)}"><span class="help-shot-frame" style="aspect-ratio:{image["width"]}/{image["height"]}"><img src="/assets/abgehakt/{esc(image["src"])}" width="{image["width"]}" height="{image["height"]}" alt="{esc(label,quote=True)}" loading="lazy" decoding="async"><span class="help-focus" aria-hidden="true" style="left:{x*100:.4f}%;top:{y*100:.4f}%;width:{w*100:.4f}%;height:{h*100:.4f}%"></span></span><span class="help-shot-label">{esc(caption)} <span aria-hidden="true">↗</span></span></a>'
                if images:body+='</div>'
                body+='</li>'
            body+='</ol>'
            if copy['note']:body+=f'<p class="help-note">{esc(copy["note"])}</p>'
            body+='</details>'
        body+='</section>'
    body+='</div>'
    close='Close' if en else 'Schließen';previous='Previous image' if en else 'Vorheriges Bild';next_label='Next image' if en else 'Nächstes Bild'
    body+=f'<dialog id="help-image-viewer" class="help-image-viewer" aria-labelledby="help-image-caption"><div class="help-viewer-controls"><button type="button" id="help-image-prev" aria-label="{previous}">←</button><button type="button" id="help-image-close">{close}</button><button type="button" id="help-image-next" aria-label="{next_label}">→</button></div><div id="help-image-stage"></div><p id="help-image-caption"></p></dialog>'
    back='Back to Abgehakt' if en else 'Zurück zu Abgehakt';path='/en/projects.html' if en else '/projekte.html'
    body+=f'<p class="help-back"><a href="{path}#einkaufsliste">{back}</a></p>'
    return f'''<!doctype html>
<html lang="{language}">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover"><title>Abgehakt · {title} | Dudee Studio</title><meta name="description" content="{intro}"><link rel="stylesheet" href="/style.css?v=13"></head>
<body><div class="wrap"><header class="top"></header><main class="help-page">{body}</main><footer></footer></div></body></html>
'''
