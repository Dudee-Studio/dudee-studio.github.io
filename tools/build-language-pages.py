#!/usr/bin/env python3
"""Build static English pages and the shared DE/EN video gallery; no runtime service."""
from pathlib import Path
import html,json,re
from help_content import document as help_document

R=Path(__file__).resolve().parents[1]
PAGES={'index.html':'index.html','projekte.html':'projects.html','kontakt.html':'contact.html','impressum.html':'legal.html','datenschutz.html':'privacy.html','hilfe.html':'help.html'}
FILMS=json.loads((R/'videos/library.json').read_text())['films']
esc=lambda v:html.escape(str(v),quote=True)
def header(page,lang):
    en=lang=='en';root='/en/' if en else '/'
    links=[('index.html','Home' if en else 'Start'),('projekte.html','Projects' if en else 'Projekte'),('kontakt.html','Contact' if en else 'Kontakt'),('hilfe.html','Help' if en else 'Hilfe')]
    nav=''.join(f'<a href="{root+(PAGES[p] if en else p) if p!="index.html" else root}"'+(' aria-current="page"' if p==page else '')+f'>{title}</a>' for p,title in links)
    langs=''.join(f'<a href="{url}" lang="{code}" hreflang="{code}" data-language-switch'+(' aria-current="true"' if code==lang else '')+f'>{code.upper()}</a>' for code,url in [('de','/' if page=='index.html' else '/'+page),('en','/en/' if page=='index.html' else '/en/'+PAGES[page])])
    return f'<header class="top"><a class="brand" href="{root}">Dudee Studio</a><nav aria-label="'+('Main navigation' if en else 'Hauptnavigation')+f'">{nav}<span class="language-switch" role="group" aria-label="'+('Language' if en else 'Sprache')+f'">{langs}</span></nav></header>'
def footer(lang,page):
    en=lang=='en';root='/en/' if en else '/'
    links=''.join(f'<a href="{root+(PAGES[p] if en else p)}"'+(' aria-current="page"' if p==page else '')+f'>{name}</a>' for p,name in [('impressum.html','Legal notice' if en else 'Impressum'),('datenschutz.html','Privacy' if en else 'Datenschutz')])
    return '<footer><span>© 2026 Dudee Studio</span><nav aria-label="'+('Legal' if en else 'Rechtliches')+f'">{links}</nav></footer>'
def gallery(lang):
    en=lang=='en';films=[x for x in FILMS if x['language']==lang];first=next(x for x in films if x['id'].startswith('overview'));films=[first]+[x for x in films if x!=first]
    title=lambda f:f['title_en'] if en else f['title_de']
    label=lambda f:('English' if f['language']=='en' else 'German') if en else ('Englisch' if f['language']=='en' else 'Deutsch')
    info=lambda f:label(f)+' · '+str(round(f['duration_sec']))+(' sec' if en else ' Sek.')+(' · '+('Preview; live activation is pending.' if en else 'Vorschau; Live-Freischaltung steht noch aus.') if f.get('preview') else '')
    url=lambda p:'/'+p+'?v=final19'
    cards=''
    for f in films:
        seconds=round(f['duration_sec']);duration=f'{seconds//60}:{seconds%60:02d}'
        cards+=f'''<a class="video-choice" href="{url(f['src'])}" data-title="{esc(title(f))}" data-info="{esc(info(f))}" data-poster="{url(f['poster'])}" data-captions="{url(f['captions'])}" data-language="{f['language']}" data-preview="{str(f['preview']).lower()}"'''+(' aria-current="true"' if f==first else '')+(' id="artikelkatalog-1-1"' if f['id'].startswith('community') else '')+f''' aria-label="{esc(title(f)+', '+label(f)+', '+duration)}"><span class="video-preview"><img src="{url(f['poster'])}" alt="" width="640" height="360" loading="lazy"><span class="video-play" aria-hidden="true">▶</span><span class="video-duration">{duration}</span></span><span class="video-title">{esc(title(f))}</span><span class="video-language">{label(f)}</span></a>'''
    return f'''<figure class="project-demo">
          <div class="media" id="abgehakt-player-wrap"><video id="abgehakt-player" controls controlslist="nodownload" playsinline preload="none" poster="{url(first['poster'])}" width="1920" height="1080" aria-label="{esc(title(first))}" aria-describedby="selected-video-info"><source src="{url(first['src'])}" type="video/mp4"><track kind="captions" src="{url(first['captions'])}" srclang="{first['language']}" label="{label(first)}">'''+('Please use a current browser to play this video.' if en else 'Bitte nutze einen aktuellen Browser zur Videowiedergabe.')+f'''</video></div>
          <div class="video-gallery" id="abgehakt-videos"><h4>Videos</h4><nav class="video-grid" aria-label="'''+('Choose a video' if en else 'Video auswählen')+f'''">{cards}</nav></div>
          <figcaption><strong id="selected-video-title" aria-live="polite">{esc(title(first))}</strong><span id="selected-video-info">{esc(info(first))}</span><small>'''+('AI photos and genuine app screens with sample data.' if en else 'KI-Fotos und echte Appansichten mit Beispieldaten.')+'''</small></figcaption>
        </figure>'''
def common(doc,page,lang):
    en=lang=='en';doc=doc.replace('<html lang="de">',f'<html lang="{lang}">')
    doc=re.sub(r'<header class="top">.*?</header>',header(page,lang),doc,flags=re.S)
    doc=re.sub(r'<footer>.*?</footer>',footer(lang,page),doc,flags=re.S)
    doc=re.sub(r'<link rel="stylesheet" href="[^"]+">','<link rel="stylesheet" href="/style.css?v=13">',doc)
    doc=re.sub(r'<script src="[^"]*script.js[^"]*"></script>','',doc)
    doc=doc.replace('</body>','<script src="/script.js?v=6"></script>\n</body>')
    doc=re.sub(r'<link rel="(?:alternate|canonical)"[^>]*>\s*','',doc)
    de='https://dudee-studio.com/'+('' if page=='index.html' else page)
    english='https://dudee-studio.com/en/'+('' if page=='index.html' else PAGES[page])
    doc=doc.replace('</head>',f'<link rel="alternate" hreflang="de" href="{de}">\n<link rel="alternate" hreflang="en" href="{english}">\n<link rel="canonical" href="{english if en else de}">\n</head>')
    return re.sub(r'\n{3,}', '\n\n', doc)
PROJECT_TEXT={
 'Projekte | Dudee Studio':'Projects | Dudee Studio', '>Anleitungen<':'>Help &amp; guides<',
 'Abgehakt: Dein Einkauf im Griff. Einkaufslisten, Gerichte und Angebote – mit kostenloser Basis und optionalem Pro. Eine Android-App von Dudee Studio.':'Abgehakt: Shopping, sorted. Shopping lists, dishes and offers, with a free core and an optional Pro version. An Android app by Dudee Studio.',
 '>Projekte<':'>Projects<','>Aktuelle Projekte<':'>Current projects<','>Android-App<':'>Android app<','>In Entwicklung<':'>In development<',
 'Dein Einkauf im Griff.':'Shopping, sorted.',
 'Weniger im Kopf. Alles auf deiner Liste. Nutze Einkaufsvorschläge aus deinem Kaufrhythmus, plane mit Artikeln und Gerichten, kaufe gemeinsam ein und behalte Angebote und Ausgaben im Blick.':'Less on your mind. Everything on your list. Get suggestions based on your shopping rhythm, plan with items and dishes, shop together and keep track of offers and spending.',
 'Funktionen ansehen ↓':'Explore features ↓','>Basis<':'>Free core<','>Pro-Version<':'>Pro version<','>Gemeinsam<':'>Together<','>Verfügbarkeit<':'>Availability<',
 'Kostenlos: lokale Listen, Artikel, Gerichte, Einkaufsprognose und Basis-Auswertung.':'Free: local lists, items, dishes, shopping forecasts and basic spending information.',
 'Barcodes scannen, gemeinsame Gruppe erstellen und erweiterte Auswertungen nutzen.':'Scan barcodes, create a shared group and use detailed spending analysis.',
 'Einmalig 3,99 € · kein Abo':'€3.99 once · no subscription',
 'Deutscher Basispreis. Der Preis im Google Play Store kann je nach Land abweichen.':'German base price. The Google Play price may vary by country.',
 'Für den Listen-Sync reicht eine Pro-Version. Andere treten kostenlos bei. Eigener Scanner und erweiterte Analyse benötigen jeweils die Pro-Version.':'One Pro purchase is enough for list sync. Others join for free. Personal access to the scanner and detailed analysis requires each person’s own Pro version.',
 'Bald bei Google Play':'Coming to Google Play','Fragen zur App?':'Questions about the app?',
 'Abgehakt im Alltag':'Abgehakt in everyday life','>Vorbereiten<':'>Plan ahead<','>Einkaufen<':'>Go shopping<','>Überblick behalten<':'>Stay on top<',
 'Artikel durchgehen. Prognose prüfen. Zutaten aus deinen Gerichten übernehmen.':'Check your items and forecasts. Add ingredients from your dishes.',
 'Liste abhaken. Spontane Einkäufe ergänzen. Coupons eintragen.':'Tick off your list. Add spontaneous purchases. Enter coupons.',
 'Letzten Angebotspreis mit Kaufdatum und deine Ausgaben ansehen.':'See the last offer price and purchase date, and keep track of spending.',
 'Funktionen genauer ansehen':'Explore the features','Artikelübersicht mit Plus- und Minus-Tasten zum Füllen der Liste':'Item overview with plus and minus controls to fill the shopping list',
 'Gericht mit auswählbaren Zutaten und Mengen für die Einkaufsliste':'Dish with selectable ingredients and shopping list quantities',
 'Erweiterte Auswertung mit Ausgaben pro Monat und Durchschnitt pro Einkauf, anhand von Demo-Daten':'Detailed analysis with monthly spending and average purchase totals, using sample data',
 'Artikel durchgehen. Liste füllen.':'Check your items. Fill your list.','Gericht wählen. Zutaten übernehmen.':'Choose a dish. Add its ingredients.',
 'Ausgaben verstehen.':'Understand spending.','>Mit Pro<':'>Pro version<','App-Ansichten mit Demo-Daten.':'App screens with sample data.',
}
def main():
    (R/'en').mkdir(exist_ok=True)
    for page,target in PAGES.items():
        doc=help_document('de') if page=='hilfe.html' else (R/page).read_text()
        if page=='projekte.html':
            if 'class="help-link"' not in doc:doc=doc.replace('<div class="buttons">','<div class="buttons"><a class="btn help-link" href="hilfe.html">Anleitungen</a>')
            doc=re.sub(r'<figure class="project-demo">.*?</figure>',gallery('de'),doc,count=1,flags=re.S)
            doc=re.sub(r'\s*<details class="(?:teaser-details|catalog-details)".*?</details>','',doc,flags=re.S)
            doc=doc.replace('<dt>Pro</dt>','<dt>Pro-Version</dt>')
            doc=doc.replace('Für Paare, WGs, Freunde und Familien: kostenlos beitreten und gemeinsam einkaufen. Eigener Scanner und erweiterte Analyse benötigen Pro.','Für den Listen-Sync reicht eine Pro-Version. Andere treten kostenlos bei. Eigener Scanner und erweiterte Analyse benötigen jeweils die Pro-Version.')
        doc=common(doc,page,'de');(R/page).write_text(doc)
        en=doc
        if page=='projekte.html':
            for de,english in PROJECT_TEXT.items():en=en.replace(de,english)
            en=re.sub(r'<figure class="project-demo">.*?</figure>',gallery('en'),en,count=1,flags=re.S)
        elif page=='index.html':
            for de,english in {
                'Dudee Studio entwickelt Apps und PC-Spiele.':'Dudee Studio creates apps and PC games.',
                'Dudee Studio: Apps und PC-Spiele':'Dudee Studio: Apps and PC games','Apps und PC-Spiele':'Apps and PC games',
                'Aktuelle Projekte':'Current projects','Zu den Projekten':'Explore projects','Android-App':'Android app','In Entwicklung':'In development',
                'Abgehakt: Dein Einkauf im Griff. Vorschau des App-Videos':'Abgehakt: Shopping, sorted. App video preview',
                'Dein Einkauf im Griff. Weniger im Kopf. Alles auf deiner Liste.':'Shopping, sorted. Less on your mind. Everything on your list.',
                'Abgehakt kennenlernen →':'Meet Abgehakt →',
                'assets/einkaufsliste/poster.jpg?v=13':'assets/einkaufsliste/videos/overview-en.jpg?v=final19',
            }.items():en=en.replace(de,english)
        elif page=='kontakt.html':
            for de,english in {'Kontakt | Dudee Studio':'Contact | Dudee Studio','So erreichen Sie Dudee Studio.':'Get in touch with Dudee Studio.','>Kontakt<':'>Contact<','Fragen zu meinen Apps und Spielen oder zur Zusammenarbeit? Schreiben Sie mir eine E-Mail.':'Questions about my apps, games or working together? Send me an email.'}.items():en=en.replace(de,english)
        elif page=='impressum.html':
            for de,english in {'Impressum | Dudee Studio':'Legal notice | Dudee Studio','Impressum von Dudee Studio.':'Legal information for Dudee Studio.','>Impressum<':'>Legal notice<','Angaben gemäß § 5 DDG':'Information under Section 5 of the German Digital Services Act (DDG)','>Kontakt<':'>Contact<','E-Mail:':'Email:','Verantwortlich für den Inhalt':'Responsible for content','Eike Dudel, Anschrift wie oben (§ 18 Abs. 2 MStV)':'Eike Dudel, address as above (Section 18(2) of the German Interstate Media Treaty, MStV)'}.items():en=en.replace(de,english)
        elif page=='hilfe.html':
            en=help_document('en')
        else:
            en=en.replace('Datenschutz | Dudee Studio','Privacy | Dudee Studio').replace('Datenschutzerklärung von Dudee Studio.','Privacy statement for Dudee Studio.')
            en=re.sub(r'<main>.*?</main>','<main>\n'+(R/'tools/i18n/privacy.en.html').read_text()+'\n  </main>',en,flags=re.S)
        # Internal navigation stays within the selected language; shared assets stay at root.
        for de,target_en in PAGES.items():en=en.replace('href="'+de,'href="/en/'+target_en)
        en=en.replace('href="./"','href="/en/"')
        en=re.sub(r'((?:src|poster)="|href=")(assets/|videos/)',r'\1/\2',en)
        en=common(en,page,'en')
        if page=='projekte.html':en=en.replace('App screens with sample data.', 'German app screens with sample data.')
        (R/'en'/target).write_text(en)
    print(f'Built {len(PAGES)} English pages and language-filtered landscape previews.')
if __name__=='__main__':main()
