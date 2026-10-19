"""Static product pages. Keep product copy and its English translation together."""
import html


def shell(language, title, description, body):
    return f'''<!doctype html>
<html lang="{language}"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{html.escape(title)} | Dudee Studio</title>
<meta name="description" content="{html.escape(description, quote=True)}">
<link rel="stylesheet" href="/style.css?v=14"></head>
<body><div class="wrap"><header class="top"></header><main>{body}</main><footer></footer></div></body></html>
'''


def app_card(language):
    en = language == 'en'
    path = '/en/apps/abgehakt.html' if en else '/apps/abgehakt.html'
    poster = '/assets/einkaufsliste/videos/overview-en.jpg?v=final19' if en else '/assets/einkaufsliste/videos/overview-de.jpg?v=final19'
    return f'''<li><a class="card" href="{path}">
      <div class="media project-cover"><img src="{poster}" alt="Abgehakt" width="1920" height="1080" loading="lazy"></div>
      <div class="meta"><span class="tag">Android</span><span class="pill dev">{'In development' if en else 'In Entwicklung'}</span></div>
      <h2>Abgehakt</h2><p>{'Less on your mind. Everything on your list.' if en else 'Weniger im Kopf. Alles auf deiner Liste.'}</p>
      <span>{'Features, videos & guides →' if en else 'Funktionen, Videos & Anleitungen →'}</span>
    </a></li>'''


def apps_document(language):
    en = language == 'en'
    return shell(language, 'Apps',
        'Discover apps by Dudee Studio: Abgehakt for Android.' if en else 'Entdecke die Apps von Dudee Studio: Abgehakt für Android.',
        '<h1 class="page-title">Apps</h1><p class="page-intro">' +
        ('More time for everyday life.' if en else 'Mehr Zeit für deinen Alltag.') +
        '</p><ul class="cards app-cards">' + app_card(language) + '</ul>')


def games_document(language):
    en = language == 'en'
    title = 'Games'
    intro = 'Discover games by Dudee Studio.' if en else 'Entdecke die Spiele von Dudee Studio.'
    body = '<h1 class="page-title">Games</h1><section class="empty-catalog">'
    body += ('<h2>New games to come</h2><p>There are no games to show yet. Future games will appear here.</p>' if en else
             '<h2>Neue Spiele folgen</h2><p>Aktuell gibt es noch keine Spiele vorzustellen. Künftige Spiele findest du hier.</p>')
    body += '</section>'
    return shell(language, title, intro, body)


def abgehakt_document(language, gallery):
    en = language == 'en'
    apps = '/en/apps.html' if en else '/apps.html'
    help_url = '/en/help.html' if en else '/hilfe.html'
    contact = '/en/contact.html' if en else '/kontakt.html'
    tagline = 'Shopping, sorted.' if en else 'Dein Einkauf im Griff.'
    intro = ('Plan meals, fill your list and see what your shopping costs as you go. '
             'Abgehakt helps you spend less time organising and more time on the things you enjoy.' if en else
             'Essen planen, Liste füllen und beim Einkaufen die Kosten im Blick behalten. '
             'Abgehakt hilft dir, weniger Zeit mit Organisation zu verbringen und mehr Zeit für die schönen Dinge zu haben.')
    body = f'''<nav class="breadcrumbs" aria-label="{'Breadcrumb' if en else 'Brotkrümelnavigation'}"><a href="{apps}">Apps</a><span aria-hidden="true">/</span><span>Abgehakt</span></nav>
    <header class="product-heading"><h1 class="page-title app-title"><img src="/assets/abgehakt/mark.png" alt="" width="56" height="56">Abgehakt</h1><p class="product-tagline">{tagline}</p><p>{intro}</p>
    <nav class="product-links" aria-label="Abgehakt"><a href="#abgehakt-funktionen">{'Features' if en else 'Funktionen'}</a><a href="#einkaufsliste">Videos</a><a href="{help_url}">{'Help & guides' if en else 'Hilfe & Anleitungen'}</a></nav></header>
    <section class="project" id="einkaufsliste" aria-label="{'App overview and videos' if en else 'Appüberblick und Videos'}">{gallery}
    <div class="info"><div class="meta"><span class="tag">Android</span><span class="pill dev">{'In development' if en else 'In Entwicklung'}</span></div>
    <h2>{'Less on your mind. More time for life.' if en else 'Weniger im Kopf. Mehr Zeit fürs Leben.'}</h2>
    <p>{'Get ready with items and dishes. Tick things off in the shop. Understand your spending afterwards.' if en else 'Mit Artikeln und Gerichten vorbereiten. Im Laden abhaken. Danach die Ausgaben verstehen.'}</p>
    <dl class="facts"><div><dt>{'Free core' if en else 'Kostenlos'}</dt><dd>{'Lists, items, dishes, forecasts, offers and basic spending information. No account needed for local use.' if en else 'Listen, Artikel, Gerichte, Prognose, Angebote und Basis-Auswertung. Lokal ohne Konto nutzbar.'}</dd></div>
    <div><dt>{'Pro version' if en else 'Pro-Version'}</dt><dd>{'Shared group, barcode scanner, online search and detailed analysis.' if en else 'Gemeinsame Gruppe, Barcode-Scanner, Online-Suche und erweiterte Analyse.'}<br><strong>{'€3.99 once · no subscription' if en else 'Einmalig 3,99 € · kein Abo'}</strong></dd></div>
    <div><dt>{'Availability' if en else 'Verfügbarkeit'}</dt><dd>{'Coming to Google Play' if en else 'Bald bei Google Play'}</dd></div></dl>
    <div class="buttons"><a class="btn primary help-link" href="{help_url}">{'Illustrated guides' if en else 'Anleitungen mit Bildern'}</a><a class="btn" href="{contact}">{'Questions?' if en else 'Fragen zur App?'}</a></div></div></section>
    <section class="product-description app-features" id="abgehakt-funktionen"><h2>{'How Abgehakt helps' if en else 'So hilft dir Abgehakt'}</h2><p class="section-intro">{'From the first meal idea to your last purchase.' if en else 'Von der ersten Essensidee bis zum abgeschlossenen Einkauf.'}</p><div class="description-grid">'''
    features = [
        ('artikel-vorbereiten',
         'Artikel einmal anlegen', 'Set up your items once',
         'Speichere Artikel mit Foto, Preis, Einheit, Markt und Kategorie. Gehe deine Artikel vor dem Einkauf durch und passe Mengen direkt an. Favoriten, Vorrat und eigene Kategorien helfen beim Überblick.',
         'Save items with a photo, price, unit, store and category. Check them before shopping and adjust quantities directly. Favourites, stock and your own categories keep things organised.'),
        ('prognose',
         'Wiederkehrenden Bedarf merken', 'Remember recurring needs',
         'Die Prognose schlägt Artikel anhand deiner bisherigen Einkäufe vor. Ein ~ kennzeichnet geschätzte Mengen. Du kannst auch selbst einen regelmäßigen Bedarf hinterlegen und entscheidest, was auf die Liste kommt.',
         'Forecasts suggest items based on your purchase history. A ~ marks estimated quantities. You can also set a regular need yourself and choose what goes onto the list.'),
        ('gericht-auf-liste',
         'Gericht wählen, Zutaten übernehmen', 'Choose a dish, add its ingredients',
         'Hinterlege Gerichte mit Zutaten und Mengen. Wähle ein Gericht aus und übernimm die benötigten Zutaten auf die Liste. Wiederverwendbare Vorlagen bündeln Artikel und Gerichte für Grillabend, Picknick und andere Anlässe.',
         'Save dishes with ingredients and quantities. Choose a dish and add the ingredients you need to your list. Reusable templates collect items and dishes for a barbecue, picnic or other occasion.'),
        ('kosten-live',
         'Im Laden den Überblick behalten', 'Stay on top in the shop',
         'Passe Stückzahlen an und hake Artikel ab. Gesamtbetrag, Betrag im Wagen und noch offene Artikel bleiben sichtbar. Die Übersicht nutzt deine hinterlegten Preise. Kurze Hinweise wie „Bitte ungesüßt“ helfen beim richtigen Griff ins Regal.',
         'Adjust quantities and tick items off. See the total, the amount in your basket and what is still missing. The overview uses your saved prices. Short notes such as “Unsweetened, please” help you pick the right item.'),
        ('letztes-angebot',
         'Angebote besser einschätzen', 'Know a good offer',
         'Erfasse befristete Angebote und vergleiche sie mit dem letzten tatsächlich gekauften Angebotspreis samt Datum. Hinterlege unterschiedliche Marktpreise und berücksichtige Coupons beim Einkaufsabschluss.',
         'Save time-limited offers and compare them with the last offer price you actually paid, including its date. Keep prices for different stores and apply coupons when completing your purchase.'),
        ('monatsausgaben',
         'Nach dem Einkauf Klarheit haben', 'Understand what you spent',
         'Vergleiche die Ausgaben dieses und des letzten Monats. Sieh dir den Preisverlauf einzelner Artikel an. Mit der Pro-Version kannst du zusätzlich nach Kategorien, Artikeln und Märkten auswerten.',
         'Compare this month’s spending with last month’s and see how individual item prices change. The Pro version adds analysis by category, item and store.'),
    ]
    for anchor, de_title, en_title, de_text, en_text in features:
        body += f'<article><h3>{en_title if en else de_title}</h3><p>{en_text if en else de_text}</p><a href="{help_url}#{anchor}">{"Step-by-step guide →" if en else "Schritt für Schritt →"}</a></article>'
    body += '</div></section>'
    body += f'''<section class="product-section" id="gemeinsam"><h2>{'Plan together, share the load' if en else 'Gemeinsam planen, Aufgaben teilen'}</h2><p>{'With a shared group, everyone can help plan: a partner, flatmates, friends or family. Share a list, suggest dishes and keep shopping notes in one place.' if en else 'In einer gemeinsamen Gruppe können alle mitplanen: Partner, WG, Freunde oder Familie. Ihr nutzt dieselbe Liste, schlagt Gerichte vor und haltet Einkaufshinweise an einem Ort fest.'}</p>
    <p><strong>{'One valid Pro version in the group is enough for sync.' if en else 'Für den Sync reicht eine gültige Pro-Version in der Gruppe.'}</strong> {'Others join for free. Each person needs their own Pro version to use the scanner, online search and detailed analysis themselves.' if en else 'Die anderen treten kostenlos bei. Für den eigenen Scanner, die Online-Suche und die erweiterte Analyse braucht jede Person die Pro-Version.'}</p>
    <a href="{help_url}#gruppe-starten">{'Set up a shared list →' if en else 'Gemeinsame Liste einrichten →'}</a></section>
    <section class="product-section" id="pro-version"><h2>{'What the Pro version adds' if en else 'Das bietet die Pro-Version zusätzlich'}</h2><ul class="product-list"><li>{'Create a shared group and invite others.' if en else 'Eine gemeinsame Gruppe erstellen und andere einladen.'}</li><li>{'Add items with the barcode scanner or online search.' if en else 'Artikel per Barcode-Scanner oder Online-Suche ergänzen.'}</li><li>{'Analyse spending by category, item and store.' if en else 'Ausgaben nach Kategorien, Artikeln und Märkten analysieren.'}</li></ul><p><strong>{'€3.99 once · no subscription.' if en else 'Einmalig 3,99 € · kein Abo.'}</strong> <small>{'German base price. The Google Play price may vary by country.' if en else 'Deutscher Basispreis. Der Google-Play-Preis kann je nach Land abweichen.'}</small></p></section>
    <details class="product-extras"><summary>{'More everyday helpers' if en else 'Weitere Helfer im Alltag'}</summary><p>{'Share a list as text, use the home-screen widget, export and import your data, choose German or English and adjust the appearance and sounds.' if en else 'Liste als Text verschicken, Startbildschirm-Widget nutzen, Daten exportieren und importieren, Deutsch oder Englisch wählen sowie Design und Töne anpassen.'}</p><p><strong>{'Community catalogue · version 1.1 preview' if en else 'Community-Katalog · Vorschau auf Version 1.1'}</strong><br>{'A shared catalogue for discovering items and optionally contributing your own. Importing items requires the Pro version. Live activation is still pending.' if en else 'Ein Katalog der Gemeinschaft, um Artikel zu entdecken und eigene freiwillig bereitzustellen. Zum Übernehmen ist die Pro-Version nötig. Die Live-Freischaltung steht noch aus.'}</p><a href="{help_url}#community-suchen">{'About the community catalogue →' if en else 'Zum Community-Katalog →'}</a></details>
    <section class="product-section product-help" id="hilfe"><h2>{'Help for every step' if en else 'Hilfe für jeden Schritt'}</h2><p>{'42 searchable guides with full app screenshots and highlighted controls, in German and English.' if en else '42 durchsuchbare Anleitungen mit vollständigen Appbildern und hervorgehobenen Bedienelementen, auf Deutsch und Englisch.'}</p><a class="btn primary" href="{help_url}">{'Open illustrated guides →' if en else 'Bebilderte Anleitungen öffnen →'}</a></section>'''
    return shell(language, 'Abgehakt', intro, body)
